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

# note: pre-process for color with Picasa

# debug mode?
debugMode = input('debug mode? (1 = yes, 0 = no): ')
# 

# remove lens distortion from all top images
# using the asymmetrical circle pattern
#lensCorrectImages(6,7)
# end distort remove

# calibrate pixel size to centimeters
# we don't repeat this for each image
bgModelLength = 4.5 # change this - in cm
bgModelWidth = 3 # change this - in cm
fileName = 'calibration/scale02.bmp'
imageScale = cv2.imread(fileName,0)
lengthScaleFactor, widthScaleFactor = pixelSizeCalibrate(imageScale,150,bgModelLength,bgModelWidth)
# end size calibrate

# open the files and process each one
if debugMode:
	print('make sure there is a SeedImages_debug directory with the inteded images')
	workingDir = 'SeedImages_debug'
else:
	workingDir = raw_input('Directory name (ex. test12801/SeedImages)?: ')
	# this was deprecated in Python 3.0, will need to be changed to input

csvfile = open(workingDir + '_processed.csv', 'w')
fieldnames = ['number','file path','length (cm)','width (cm)','area (pixels)',
				'color value (R)','color value (G)','color value (B)',
				'height (pixels)','volume (pixels)','angle (degrees)','error']
writerObj = csv.DictWriter(csvfile, fieldnames=fieldnames)
writerObj.writeheader()
# BEGIN LOOP
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
	imageCroppedBW = imageBW[150:950,150:1450] # NOTE: its image[y: y + h, x: x + w]
	imageCroppedColor = imageColor[150:950,150:1450]
	# end crop image

	# calculate length, width, area, and debug variables
	threshTopVal = 125
	topImgVariables = findLengthWidth(imageCroppedBW,threshTopVal)
	topLength = topImgVariables['length']
	topWidth = topImgVariables['width']
	topRotateAngle = topImgVariables['angle']
	topCenterPoint = topImgVariables['center']
	topArea = topImgVariables['area']
	topLargestIndex = topImgVariables['largestIndex'] 
	topContours = topImgVariables['contours']
	# end top calculations

	# debug
	#cv2.imshow(str(fileName),imageCroppedBW)
	#cv2.waitKey(0)
	#cv2.destroyWindow(str(fileName))
	if debugMode:
		debugThreshTop = imageThreshold(imageCroppedBW,threshTopVal)
		cv2.imshow(str(fileName),debugThreshTop)
		cv2.waitKey(0)
		cv2.destroyWindow(str(fileName))
		debugContourTop = imageCroppedColor
		cv2.drawContours(debugContourTop,topContours,topLargestIndex,(0,0,255),3)
		cv2.imshow(str(fileName),debugContourTop)
		cv2.waitKey(0)
		cv2.destroyWindow(str(fileName))

	# rotate the seed image so its length is along the x-axis
	if topRotateAngle != 0:
		imageCroppedBWRotated = rotateImage(imageCroppedBW,topRotateAngle,topCenterPoint)
		# useful for complex volume finding alogirthm
	# end rotate

	# find SIDE IMAGE height, volume
	# navigate to files and open
	fileName_Side = string.replace(fileName,'TopImage','SideImage')
	if fileName_Side[-7:-4] == '000':
		fileName_Side = string.replace(fileName,'SideImage','Side')
		# errors propogate... a lazy programmer made this necessary

	imageColor_Side = cv2.imread(fileName_Side,1) # three channel image (B,G,R)
	imageBW_Side = cv2.imread(fileName_Side,0)
	# end navigate

	# crop image
	imageCroppedBW_Side = imageBW_Side[390:940,900:970] # NOTE: its image[y: y + h, x: x + w]
	imageCroppedColor_Side = imageColor_Side[390:940,900:970]
	# end crop image

	# calculate length, width (height because side), area, and debug variables
	threshSideVal = 125
	sideImgVariables = findLengthWidth(imageCroppedBW_Side,threshSideVal)
	sideLength = sideImgVariables['length']
	sideWidth = sideImgVariables['width']
	sideRotateAngle = sideImgVariables['angle']
	sideCenterPoint = sideImgVariables['center']
	sideArea = sideImgVariables['area']
	sideLargestIndex = sideImgVariables['largestIndex'] 
	sideContours = sideImgVariables['contours']
	# end side calculations

	# debug
	if debugMode:
		debugThreshSide = imageThreshold(imageCroppedBW_Side,threshSideVal)
		cv2.imshow(str(fileName),debugThreshSide)
		cv2.waitKey(0)
		cv2.destroyWindow(str(fileName))
		debugContourSide = imageCroppedColor_Side
		cv2.drawContours(debugContourSide,sideContours,sideLargestIndex,(0,0,255),3)
		cv2.imshow(str(fileName),debugContourSide)
		cv2.waitKey(0)
		cv2.destroyWindow(str(fileName))

	# calculate volume
	#
	# we do this by multiplying the top area times the height
	#
	# this may be made into a more complex function call
	# in the future, but for now it is simple because 
	# our height is uncalibrated
	#	(by using as many height+width
	#	combinations as possible and know seed to side image
	#	angle. Make the measurements arguements to an ellipse
	#	and use the ellipses to fill out the seed along its length
	#	summing along the way to find total value)
	volume = topArea*sideWidth
	# end geometry calculation

	# find average color value
	# uses top images only because color correction was performed
	# goes through every pixel in array and find average value of each channel
	# !!!! note values are B G R !!!!

	# Initialize empty list
	lst_intensities = []
	# Create a mask image that contains the contour filled in
	cimg = np.zeros_like(imageCroppedBW)
	cv2.drawContours(cimg,topContours,topLargestIndex,255,-1)

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
	lengthcm = topLength*lengthScaleFactor
	widthcm = topWidth*widthScaleFactor
	# end scale

	# check for errors
	# case 1 - contour_conflicts_edge
	if contourHitsEdge(topLargestIndex,topContours,imageCroppedBW):
		error += 'contour_conflicts_edge-'

	# case 2 - area_too_small
	if topArea <= 100:
		error += 'area_too_small-'

	# case 3 - area_too_large
	if topArea >= 40000:
		error += 'area_too_large-'
	# end check for exceptions

	# create debug output
	debugImage = imageCroppedColor
	# draw contour trace
	cv2.drawContours(debugImage,topContours,topLargestIndex,(0,0,255),1)
	# draw rectangle
	# create top image rectangle (rotated) containing seed, and find midpoints
	bounds = cv2.minAreaRect(topContours[topLargestIndex])
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
	cv2.circle(debugImage,topCenterPoint,2,(0,255,0),-1)
	cv2.putText(debugImage,'ctr',topCenterPoint,cv2.FONT_HERSHEY_SIMPLEX,.5,(0,255,0))

	# add text
	lengthText = 'length (cm) = ' + str(lengthcm)
	widthText = 'width (cm) = ' + str(widthcm)
	areaText = 'area (pixels) = ' + str(topArea)
	colorValueText = 'color value (R G B) = (' + str(redAverage) + "," + str(greenAverage) + "," + str(blueAverage) + ")"
	heightText = 'height (pixels) = ' + str(sideWidth)
	volumeText = 'volume (pixels) = ' + str(volume)
	angleText = 'angle (degrees) = ' + str(topRotateAngle)
	errorText = error
	cv2.putText(debugImage,fileName,(10,20),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,lengthText,(10,40),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,widthText,(10,60),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,areaText,(10,80),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,colorValueText,(10,100),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,heightText,(10,120),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,volumeText,(10,140),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,angleText,(10,160),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
	cv2.putText(debugImage,errorText,(10,180),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))

	if debugMode:
		cv2.imshow(str(fileName),debugImage)
		cv2.waitKey(0)
		cv2.destroyWindow(str(fileName))

	writerObj.writerow({'number':str(x),'file path':fileName,
						'length (cm)':str(lengthcm),'width (cm)':str(widthcm),
						'area (pixels)':str(topArea),'color value (R)':str(redAverage),
						'color value (G)':str(greenAverage),'color value (B)':str(blueAverage),
						'height (pixels)':str(sideWidth),'volume (pixels)':str(volume),
						'angle (degrees)':str(topRotateAngle),'error':error})
	print('processed: ' + fileName + '  [' + str(x) + ']')
	x+=1
csvfile.close()
# !!!!!END LOOP!!!!!
print('done: data saved in ' + workingDir + '_processed.csv')

# write debug output and show image
#cv2.imwrite('debug.bmp',debugImage)





