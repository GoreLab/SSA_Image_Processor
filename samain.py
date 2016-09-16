# samain.py
#
# author:
# Kevin Kreher
# KMK279@cornell.edu
#
# compatibility Python version 2.7.10 + OpenCV version 2.4.12
# there are notes in here for porting 
# to Python 3 or OpenCV 3 (findContour breaks, etc.)

from salib import *
import numpy as np
import cv
import cv2
import math
import csv
import string

# note: pre-process first
# correct color with Picasa or similar
# remove lens distortion if possible (negligible for seeds falling into center of FOV)
# Run through Guo's algorithm to remove background

# debug mode?
debugMode = input('debug mode? (1 = yes, 0 = no): ')
# end debug mode check

# calibrate pixel size to centimeters
# we don't repeat this for each image
# pixelSizeCalibrate is an attempt at automating this
# but it should not change in most cases, if it does change, the manual calibration
# method will work as well
#bgModelLength = 4.5 # change this - in cm
#bgModelWidth = 3 # change this - in cm
#fileName = 'calibration/scale02.bmp'
#imageScale = cv2.imread(fileName,0)
#lengthScaleFactorTop, widthScaleFactorTop = pixelSizeCalibrate(imageScale,150,bgModelLength,bgModelWidth)
lengthScaleFactorTop = 0.003118 # cm/pixel at (set distance) from lense
widthScaleFactorTop = lengthScaleFactorTop # cm/pixel
side_ScaleFactor_eqM = 0.00154 # slope for equation as calculated by scaling factor calculator
side_ScaleFactor_eqB = 0.0003111 # offset for equation as calculated by scaling factor calculator
side_ScaleFactor_intersectX = 466 # using ruler placed flat, also see CameraDist_in
CameraDist_in = 1.65625 # distance in inches that camera is out of image
CameraDist_angle = 76.4 # angle at which side camera is pointing into top image in degrees
#ScaleFactorSide = 0.00339 # cm/pixel 
# end size calibrate

# open the files and process each one
if debugMode:
	print('make sure there is a SeedImages_debug directory with the inteded images')
	workingDir = 'SeedImages_debug'
else:
	workingDir = raw_input('Directory name (ex. test12801/SeedImages)?: ')
	# this was deprecated in Python 3.0, will need to be changed to input, not raw_input

csvfile = open(workingDir + '_processed.csv', 'w')
fieldnames = ['number','file path','length (cm)','width (cm)','area (pixels)',
				'color value (R)','color value (G)','color value (B)',
				'height (cm)','volume (cm3)','angle (degrees)','error','topX','topY']
writerObj = csv.DictWriter(csvfile, fieldnames=fieldnames)
writerObj.writeheader()
# BEGIN LOOP
print('Processing directory: ' + workingDir)
x = 0
for fileName in glob.glob(workingDir + '/TopImage*'):
	error = ''

	# navigate to files and open
	imageColor = cv2.imread(fileName,1) # three channel image (B,G,R)
	imageBW = cv2.imread(fileName,0) # BW
	# end navigate

	# debug
	#cv2.imshow(str(fileName),imageColor)
	#cv2.waitKey(0)
	#cv2.destroyWindow(str(fileName))

	# crop image
	#cropystart = 150
	#cropyend = 950
	#cropxstart = 150
	#cropxend = 1650
	imageCroppedBW = imageBW#[cropystart:cropyend,cropxstart:cropxend] # NOTE: its image[y: y + h, x: x + w]
	imageCroppedColor = imageColor#[cropystart:cropyend,cropxstart:cropxend]
	# end crop image

	# calculate length, width, area, and debug variables
	threshTopVal = 70
	topImgVariables = findLengthWidth(imageCroppedBW,threshTopVal)
	topLength_norotate = topImgVariables['length']
	topWidth_norotate = topImgVariables['width']
	topRotateAngle_norotate = topImgVariables['angle']
	topCenterPoint_norotate = topImgVariables['center']
	topX = topCenterPoint_norotate[0]
	topY = topCenterPoint_norotate[1]
	topArea_norotate = topImgVariables['area']
	topLargestIndex_norotate = topImgVariables['largestIndex'] 
	topContours_norotate = topImgVariables['contours']

	# rotate the top seed image so its length is along the x-axis
	if abs(topRotateAngle_norotate) > 5:
		imageCroppedBWRotated = rotateImage(imageCroppedBW,topRotateAngle_norotate,topCenterPoint_norotate)
	else:
		imageCroppedBWRotated = imageCroppedBW
		# angle is OK, fill in the variables to continue working
	# useful for complex volume finding alogirthm
	# end rotate

	#recalculate length,width,area,debug variables
	topImgVariables = findLengthWidth(imageCroppedBWRotated,threshTopVal)
	topLength = topImgVariables['length']
	topWidth = topImgVariables['width']
	topRotateAngle = topImgVariables['angle']
	#print('angle = ' + str(topRotateAngle))
	#print('angle_norotate = ' + str(topRotateAngle_norotate))
	topCenterPoint = topImgVariables['center']
	topArea = topImgVariables['area']
	topLargestIndex = topImgVariables['largestIndex'] 
	topContours = topImgVariables['contours']
	# end top calculations

	# debug
	#cv2.imshow(str(fileName),imageCroppedBWRotated)
	#cv2.waitKey(0)
	#cv2.destroyWindow(str(fileName))
	if debugMode:
		print('topX = ' + str(topX))
		print('topY = ' + str(topY))
		unused, debugThreshTop = cv2.threshold(imageCroppedBWRotated,threshTopVal,255,cv2.THRESH_BINARY)
		debugThreshTop = erodeAndDilate(debugThreshTop,np.ones((5,5),np.uint8),1)
		cv2.imshow(str(fileName),debugThreshTop)
		cv2.waitKey(0)
		cv2.destroyWindow(str(fileName))
		debugContourTop = imageCroppedColor
		cv2.drawContours(debugContourTop,topContours_norotate,topLargestIndex_norotate,(0,0,255),3)
		cv2.imshow(str(fileName),debugContourTop)
		cv2.waitKey(0)
		cv2.destroyWindow(str(fileName))


	# find SIDE IMAGE height, volume
	# navigate to files and open
	fileName_Side = string.replace(fileName,'TopImage','SideImage')
	#if fileName_Side[-7:-4] == '000':
	#	fileName_Side = string.replace(fileName,'SideImage','Side')
	#	# errors propogate... a lazy programmer made this necessary
	fileName_Side = string.replace(fileName_Side,'-27-','-26-') # hack :(
	print('REMOVE THIS!' + ' fileName_Side = ' + fileName_Side)

	imageColor_Side = cv2.imread(fileName_Side,1) # three channel image (B,G,R)
	imageBW_Side = cv2.imread(fileName_Side,0)
	# end navigate

	# crop image
	#cropystart = 390
	#cropyend = 950
	#cropxstart = 850
	#cropxend = 970
	imageCroppedBW_Side = imageBW_Side#[cropystart:cropyend,cropxstart:cropxend] # NOTE: its image[y: y + h, x: x + w]
	imageCroppedColor_Side = imageColor_Side#[cropystart:cropyend,cropxstart:cropxend]
	# end crop image


	# calculate length, width (height because side), area, and debug variables
	threshSideVal = 30
	sideImgVariables = findLengthWidth(imageCroppedBW_Side,threshSideVal)
	sideLength = sideImgVariables['length']
	sideWidth = sideImgVariables['width']
	sideRotateAngle = sideImgVariables['angle']
	sideCenterPoint = sideImgVariables['center']
	sideArea = sideImgVariables['area']
	sideLargestIndex = sideImgVariables['largestIndex'] 
	sideContours = sideImgVariables['contours']
	# end side calculations

	#ScaleFactorSide now calculated per seed
	ScaleFactorSide = calcSideScaleFactor(topCenterPoint_norotate,200,200,lengthScaleFactorTop,side_ScaleFactor_eqM,side_ScaleFactor_eqB,side_ScaleFactor_intersectX,CameraDist_in,CameraDist_angle,topRotateAngle_norotate,topLength)
	#print('scaleFactorSide = ' + str(ScaleFactorSide))
	# end scaleFactorSide calculations



	# debug
	if debugMode:
		unused, debugThreshSide = cv2.threshold(imageCroppedBW_Side,threshSideVal,255,cv2.THRESH_BINARY)
		debugThreshSide = erodeAndDilate(debugThreshSide,np.ones((5,5),np.uint8),1)
		cv2.imshow(str(fileName),debugThreshSide)
		cv2.waitKey(0)
		cv2.destroyWindow(str(fileName))
		debugContourSide = imageCroppedColor_Side
		# draw rectangle
		# create top image rectangle containing seed, and find midpoints
		bounds = cv2.minAreaRect(sideContours[sideLargestIndex])
		# box used for finding midpoints and drawing
		box = cv2.cv.BoxPoints(bounds) # note cv2.cv.BoxPoints(rect) will be removed in openCV 3
		#cv2.boxPoints(bounds) - if openCV 3
		box = np.int0(box)
		cv2.drawContours(debugContourSide,[box],0,(0,0,255),1)
		cv2.drawContours(debugContourSide,sideContours,sideLargestIndex,(0,0,255),3)
		cv2.imshow(str(fileName),debugContourSide)
		cv2.waitKey(0)
		cv2.destroyWindow(str(fileName))



	# check for errors
	# case 1 - contour_conflicts_edge
	if contourHitsEdge(topLargestIndex_norotate,topContours_norotate,imageCroppedBW):
		error += 'contour_conflicts_edge-'

	# case 2 - area_too_small_top
	if topArea_norotate <= 100:
		error += 'area_too_small_top-'

	# case 3 - area_too_small_side
	if sideArea <= 100:
		error += 'area_too_small_side-'

	# case 4 - area_too_large
	if topArea_norotate >= 40000:
		error += 'area_too_large-'

	# case 5 - over angle
	if abs(topRotateAngle_norotate) > 80:
		error += 'angle_over_80-'
	# end check for exceptions


	# calculate volume
	if len(error) < 1:
		# before passing side image, we will rotate it so the long axis of the seedis in line
		# with the x-axis in the image
		# we will not have to rotate it often
		if abs(sideRotateAngle) > 6:
			imageRotated_Side = rotateImage(imageCroppedBW_Side,sideRotateAngle,sideCenterPoint)
			sideImgVariables_forVol = findLengthWidth(imageRotated_Side,threshSideVal)
		else:
			sideImgVariables_forVol = sideImgVariables
		volume = findVolume(imageCroppedBWRotated,imageCroppedBW_Side,topImgVariables,sideImgVariables_forVol,threshSideVal,lengthScaleFactorTop,ScaleFactorSide)
		#print('volume = ' + str(volume)) # debug output
		# running volume on poorly formed numpy arrays is a bad idea
	else:
		volume = 0
	# end volume calculation

	# find average color value
	# uses top images only because color correction was performed
	# goes through every pixel in array and find average value of each channel
	# !!!! note values are B G R !!!!

	# Initialize empty list
	lst_intensities = []
	# Create a mask image that contains the contour filled in
	cimg = np.zeros_like(imageCroppedBW)
	cv2.drawContours(cimg,topContours_norotate,topLargestIndex_norotate,255,-1)

	# debug
	#cv2.imshow('debugOutput_mask',cimg)
	#cv2.waitKey(0)
	#cv2.destroyWindow('debugOutput_mask')

	# Access the image pixels and create a 1D numpy array then add to list
	pts = np.where(cimg == 255)
	# (array([305, 305, 305, ..., 426, 426, 426]), array([507, 508, 509, ..., 707, 711, 712]))
	i = 0
	while i < len(pts[0]):
		lst_intensities.append(imageCroppedColor[pts[0][i], pts[1][i]])
		i += 1

	blue = 0
	green = 0
	red = 0
	i = 0
	pixelcount = 0
	while i < len(lst_intensities):
		# remove all white reflections 240, 240, 240
		# keep track of how many pixels actually get analyzed
		# use this for averaging
		if lst_intensities[i][0] < 240 and lst_intensities[i][1] < 240 and lst_intensities[i][2] < 240:
			blue += lst_intensities[i][0]
			green += lst_intensities[i][1]
			red += lst_intensities[i][2]
			pixelcount += 1
		i += 1
	if pixelcount > 0:
		blueAverage = blue/pixelcount
		greenAverage = green/pixelcount
		redAverage = red/pixelcount
	else:
		blueAverage = 0
		greenAverage = 0
		redAverage = 0
	# end color find

	# scale from pixels to cm
	lengthcm = topLength*lengthScaleFactorTop
	widthcm = topWidth*widthScaleFactorTop
	heightcm = sideWidth*ScaleFactorSide
	# end scale

	# create debug output
	debugImage = imageCroppedColor
	# draw contour trace
	cv2.drawContours(debugImage,topContours_norotate,topLargestIndex_norotate,(0,0,255),1)
	# draw rectangle
	# create top image rectangle (rotated) containing seed, and find midpoints
	bounds = cv2.minAreaRect(topContours_norotate[topLargestIndex_norotate])
	# box used for finding midpoints and drawing
	box = cv2.cv.BoxPoints(bounds) # note cv2.cv.BoxPoints(rect) will be removed in openCV 3
	#cv2.boxPoints(bounds) - if openCV 3
	box = np.int0(box)
	cv2.drawContours(debugImage,[box],0,(0,0,255),1)
	# draw line trace
	#cv2.line(debugImage,B,D,(0,0,255),1)
	#cv2.line(debugImage,A,C,(0,0,255),1)
	#cv2.circle(debugImage,A,2,(0,255,0),-1)
	#cv2.putText(debugImage,'A',A,cv2.FONT_HERSHEY_SIMPLEX,.5,(0,255,0))
	#cv2.circle(debugImage,B,2,(0,255,0),-1)
	#cv2.putText(debugImage,'B',B,cv2.FONT_HERSHEY_SIMPLEX,.5,(0,255,0))
	#cv2.circle(debugImage,C,2,(0,255,0),-1)
	#cv2.putText(debugImage,'C',C,cv2.FONT_HERSHEY_SIMPLEX,.5,(0,255,0))
	#cv2.circle(debugImage,D,2,(0,255,0),-1)
	#cv2.putText(debugImage,'D',D,cv2.FONT_HERSHEY_SIMPLEX,.5,(0,255,0))
	cv2.circle(debugImage,topCenterPoint_norotate,2,(0,255,0),-1)
	cv2.putText(debugImage,'ctr',topCenterPoint_norotate,cv2.FONT_HERSHEY_SIMPLEX,.5,(0,255,0))

	# add text
	lengthText = 'length (cm) = ' + str(lengthcm)
	widthText = 'width (cm) = ' + str(widthcm)
	areaText = 'area (pixels) = ' + str(topArea_norotate)
	colorValueText = 'color value (R G B) = (' + str(redAverage) + "," + str(greenAverage) + "," + str(blueAverage) + ")"
	heightText = 'height (cm) = ' + str(heightcm)
	volumeText = 'volume (cm3) = ' + str(volume)
	angleText = 'angle (degrees) = ' + str(topRotateAngle_norotate)
	errorText = 'error = ' + error
	topxText = 'topXpos (pixel) = ' + str(topX)
	topyText = 'topYpos (pixel) = ' + str(topY)
	cv2.putText(debugImage,fileName,(10,20),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,lengthText,(10,40),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,widthText,(10,60),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,areaText,(10,80),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,colorValueText,(10,100),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,heightText,(10,120),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,volumeText,(10,140),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,angleText,(10,160),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,errorText,(10,180),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,topxText,(10,200),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,topyText,(10,220),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))

	if debugMode:
		cv2.imshow(str(fileName),debugImage)
		cv2.waitKey(0)
		cv2.destroyWindow(str(fileName))

	writerObj.writerow({'number':str(x),'file path':fileName,
						'length (cm)':str(lengthcm),'width (cm)':str(widthcm),
						'area (pixels)':str(topArea_norotate),'color value (R)':str(redAverage),
						'color value (G)':str(greenAverage),'color value (B)':str(blueAverage),
						'height (cm)':str(heightcm),'volume (cm3)':str(volume),
						'angle (degrees)':str(topRotateAngle_norotate),'error':error,'topX':topX,'topY':topY})
	print('processed: ' + fileName + '  [' + str(x) + ']')
	x += 1
csvfile.close()
# !!!!!END LOOP!!!!!
print('>>> Done: data saved in ' + workingDir + '_processed.csv')
exit() # purposeful, this can be changed if this is turned into a MAIN function

# write debug output and show image
#cv2.imwrite('debug.bmp',debugImage)





