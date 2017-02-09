""" samain.py - Script for analyzing seed images.

This script takes a file directory containing images of seeds as an
input and uses the images to produce output csv files containing data
such as color, volume, and seed measurements. Note that the
measurements require calibration data to be converted to real
world units (typically centimeters or centimeters cubed). Also note
that the pre-processing must be completed before using this script.
The directory structure and steps for inputting calibration data can
be found in the user guides on Google Drive. Developed and tested with
Python 2.7.x and OpenCV 2.4.x.

Written by Kevin Kreher (kmk279@cornell.edu).
"""

__author__ = 'Kevin Kreher'

from salib import *
import saconfig as sacfg
import numpy as np
import cv2
import math
import csv
import string
import os.path
import operator

# These variables are responsible for converting from pixel length
#    measurements made by the script to real world distances. They are
#    all defined and described in saconfig.py, and the associated
#	 Google Drive documentation.
top_ScaleFactor = sacfg.topScaleFactor
top_CameraDist_in = sacfg.topCameraDistin
top_CameraDist_angle = sacfg.topCameraDistangle
side_ScaleFactor_eqM = sacfg.sideScaleFactoreqM
side_ScaleFactor_eqB = sacfg.sideScaleFactoreqB
side_ScaleFactor_intersectX = sacfg.sideScaleFactorintersectX
top_cropleft = sacfg.topCropleft
top_croptop = sacfg.topCroptop

# DebugMode shows the image at each step, not recommended when
#    many images need to be processed.
debugMode = sacfg.debugmode
workingDir = raw_input('Directory name (ex. test12801/SeedImages)?: ')
csvfile = open(workingDir + '_processed.csv', 'wb') # CSV file for data.
fieldnames = ['number','file path','length (cm)','width (cm)','height (cm)',
              'color value (R)','color value (G)','color value (B)',
			  'volume (cm3)','angle (degrees)','error','height_ratiomethod (cm)',
			  'count1','r1','g1','b1','count2','r2','g2','b2','count3','r3',
			  'g3','b3','count4','r4','g4','b4','count5','r5','g5','b5']
writerObj = csv.DictWriter(csvfile, fieldnames=fieldnames)
writerObj.writeheader()
print('Processing directory: ' + workingDir)
x = 0 # Tracks with image number.
for top_fileName in glob.glob(workingDir + '/TopImage*'):
	# Find the side image filename.
	side_fileName = string.replace(top_fileName,'TopImage','SideImage')
	if os.path.isfile(side_fileName) == False:
		# A lazy programmer made this step necessary.
		side_fileName = string.replace(side_fileName,'SideImage','Side')
	# Import top and side images.
	top_imageColor = cv2.imread(top_fileName,1) # B,G,R color channels
	top_imageBW = cv2.imread(top_fileName,0) # BW
	side_imageColor = cv2.imread(side_fileName,1) # B,G,R color channels
	side_imageBW = cv2.imread(side_fileName,0) # BW
    # Pre-processing now crops, this was left in case this changes.
	top_imageBW_crop = top_imageBW
	top_imageColor_crop = top_imageColor
	side_imageBW_crop = side_imageBW
	side_imageColor_crop = side_imageColor

	if debugMode:
		cv2.imshow(str(top_fileName),top_imageColor_crop)
		cv2.waitKey(0)
		cv2.destroyWindow(str(top_fileName))
		cv2.imshow(str(side_fileName),side_imageColor_crop)
		cv2.waitKey(0)
		cv2.destroyWindow(str(side_fileName))

	# Calculate the length, width, etc. of the top image seed.
	top_threshValue = 60
	top_Variables_noRotate = findLengthWidth(top_imageBW_crop,top_threshValue)
	top_Length_noRotate = top_Variables_noRotate['length']
	top_Width_noRotate = top_Variables_noRotate['width']
	top_Angle_noRotate = top_Variables_noRotate['angle']
	top_centerPoint_noRotate = top_Variables_noRotate['center']
	topX = top_centerPoint_noRotate[0]
	topY = top_centerPoint_noRotate[1]
	top_Area_noRotate = top_Variables_noRotate['area']
	top_largestIndex_noRotate = top_Variables_noRotate['largestIndex'] 
	top_Contours_noRotate = top_Variables_noRotate['contours']

	# If the seed is greatly angled the next step rotates the seed
	#    such that its length is parallel to the x-axis and re-
	#    calculates the variables found above (length, width, etc.).
	if abs(top_Angle_noRotate) > 5:
		top_imageBW_crop_rotated = rotateImage(top_imageBW_crop,
			                                   top_Angle_noRotate,
			                                   top_centerPoint_noRotate)
	else:
		top_imageBW_crop_rotated = top_imageBW_crop
    
	top_Variables_rotated = findLengthWidth(top_imageBW_crop_rotated,
		                                    top_threshValue)
	top_Length_rotated = top_Variables_rotated['length']
	top_Width_rotated = top_Variables_rotated['width']
	top_Angle_rotated = top_Variables_rotated['angle']
	top_centerPoint_rotated = top_Variables_rotated['center']
	top_Area_rotated = top_Variables_rotated['area']
	top_largestIndex_rotated = top_Variables_rotated['largestIndex'] 
	top_Contours_rotated = top_Variables_rotated['contours']

	if debugMode:
		unused, top_debugThresh = cv2.threshold(top_imageBW_crop_rotated,
			                                    top_threshValue,255,
			                                    cv2.THRESH_BINARY)
		top_debugThresh = erodeAndDilate(top_debugThresh,np.ones((5,5),
			                             np.uint8),1)
		cv2.imshow(str(top_fileName),top_debugThresh)
		cv2.waitKey(0)
		cv2.destroyWindow(str(top_fileName))
		debugContourTop = top_imageColor_crop
		cv2.drawContours(debugContourTop,top_Contours_noRotate,
			             top_largestIndex_noRotate,(0,0,255),1)
		cv2.imshow(str(top_fileName),debugContourTop)
		cv2.waitKey(0)
		cv2.destroyWindow(str(top_fileName))

	# Calculate the length, width, etc. of the side image seed.
	side_threshVal = 15
	side_Variables = findLengthWidth(side_imageBW_crop,side_threshVal)
	side_Length = side_Variables['length']
	side_Width = side_Variables['width']
	side_Angle = side_Variables['angle']
	side_centerPoint = side_Variables['center']
	side_Area = side_Variables['area']
	side_largestIndex = side_Variables['largestIndex'] 
	side_Contours = side_Variables['contours']
	side_ScaleFactor = calcSideScaleFactor(top_centerPoint_noRotate,
										  top_cropleft,top_croptop,
		                                  top_ScaleFactor,
		                                  side_ScaleFactor_eqM,
		                                  side_ScaleFactor_eqB,
		                                  side_ScaleFactor_intersectX,
		                                  top_CameraDist_in,
		                                  top_CameraDist_angle,
		                                  top_Angle_noRotate,
		                                  top_Length_rotated)

	if debugMode:
		unused, debugThreshSide = cv2.threshold(side_imageBW_crop,
			                                    side_threshVal,255,
			                                    cv2.THRESH_BINARY)
		debugThreshSide = erodeAndDilate(debugThreshSide,np.ones((5,5),
			                             np.uint8),1)
		cv2.imshow(str(top_fileName),debugThreshSide)
		cv2.waitKey(0)
		cv2.destroyWindow(str(top_fileName))
		debugContourSide = side_imageColor_crop
		# Create rectangle containing seed and find midpoints.
		bounds = cv2.minAreaRect(side_Contours[side_largestIndex])
		box = cv2.cv.BoxPoints(bounds)
		box = np.int0(box)
		cv2.drawContours(debugContourSide,[box],0,(0,0,255),1)
		cv2.drawContours(debugContourSide,side_Contours,side_largestIndex,
			             (0,0,255),1)
		cv2.imshow(str(top_fileName),debugContourSide)
		cv2.waitKey(0)
		cv2.destroyWindow(str(top_fileName))

	# Code for detecting any processing errors.
	top_Area_max_error = 40000
	top_Area_min_error = 100
	top_Angle_max_error = 80
	side_Area_max_error = 16000
	side_Area_min_error = 100
	# No seeds (oat), when properly detected were larger/smaller
	# than these numbers in tests. Applies to top/side.
	error = ''
	if contourHitsEdge(top_largestIndex_noRotate,top_Contours_noRotate,
		               top_imageBW_crop):
		error += 'top_contour_conflicts_edge-'
	if top_Area_noRotate <= top_Area_min_error:
		error += 'top_area_too_small-'
	if side_Area <= side_Area_min_error:
		error += 'side_area_too_small-'
	if top_Area_noRotate >= top_Area_max_error:
		error += 'top_area_too_large-'
	if side_Area >= side_Area_max_error:
		error += 'side_area_too_large-'
	if abs(top_Angle_noRotate) > top_Angle_max_error:
		error += 'angle_over_max_error-'

	# Volume calculation occurs below if no errors are detected.
	if len(error) < 1:
		if abs(side_Angle) > 6:
			# Rotate the side image so the axis of its length is
			#    parallel to the x-axis. Not always necessary.
			side_imageRotated_forVol = rotateImage(side_imageBW_crop,
				                                   side_Angle,
				                                   side_centerPoint)
			side_Variables_forVol = findLengthWidth(side_imageRotated_forVol,
				                                    side_threshVal)
		else:
			side_imageRotated_forVol = side_imageBW_crop
			side_Variables_forVol = side_Variables
		volume = findVolume(top_imageBW_crop_rotated,side_imageRotated_forVol,
			                top_Variables_rotated,side_Variables_forVol,
			                side_threshVal,top_ScaleFactor,side_ScaleFactor)
	else:
		volume = 0

	# Find average color value. Numpy values are saved as B,G,R.
	#    Only accurate if pre-processed correctly. The next steps
	#    Create a mask over the colored pixels before a list is made
	#    that can be used to start manipulating the color values.
	cimg = np.zeros_like(top_imageBW_crop)
	cv2.drawContours(cimg,top_Contours_noRotate,top_largestIndex_noRotate,
		             255,-1)
	pts = np.where(cimg == 255) # List of all seed colored pixels.
	i = 0
	lst_intensities = []
	while i < len(pts[0]):
		lst_intensities.append(top_imageColor_crop[pts[0][i], pts[1][i]])
		i += 1
	color_dict = {} # Dictionary for keeping count of color occurences.
	blue = 0
	green = 0
	red = 0
	i = 0
	pixelcount = 0
	while i < len(lst_intensities):
		b_temp = lst_intensities[i][0]
		g_temp = lst_intensities[i][1]
		r_temp = lst_intensities[i][2]
		# A filter could be used here.
		blue += b_temp
		green += g_temp
		red += r_temp
		pixelcount += 1 # Number of pixels analyzed (if filter used)
		rgb_key = (r_temp,g_temp,b_temp) # Key for dictionary.
		if rgb_key in color_dict:
			color_dict[rgb_key] += 1
		else:
			color_dict[rgb_key] = 1
		i += 1
	# An additional csv file is created to store RGB color information.
	slash_index = workingDir.rfind('/')
	if slash_index == -1:
		slash_index = workingDir.rfind('\\') # Running on windows.
	color_dir_name = workingDir[:slash_index+1]
	color_file_number = str(x).zfill(3) # Pad with zeroes.
	csvfile_colors = open(color_dir_name + 'TopImage_' + color_file_number
		                  + '_rgb.csv', 'wb') # CSV file for data.
	fieldnames_colors = ['r','g','b','count']
	writerObj2 = csv.DictWriter(csvfile_colors, fieldnames=fieldnames_colors)
	writerObj2.writeheader()
	writerObj2.writerow({'r':'','g':'','b':'total count:',
	                     'count':str(pixelcount)}) # Prints pixel total.
	for key, value in color_dict.items():
		if value > 2:
			writerObj2.writerow({'r':str(key[0]),'g':str(key[1]),
				                 'b':str(key[2]),'count':str(value)})
	csvfile_colors.close()
	if pixelcount > 0:
		blueAverage = blue/pixelcount
		greenAverage = green/pixelcount
		redAverage = red/pixelcount
	else:
		blueAverage = 0
		greenAverage = 0
		redAverage = 0
	# Also print the top 5 occurences into the main output.
	# This will be cleaned up in the future
	sorted_x = sorted(color_dict.items(),key=operator.itemgetter(1))
	if len(sorted_x) > 5:
		Count_Top_1 = sorted_x[-1][1]
		Red_Top_1 = sorted_x[-1][0][0]
		Green_Top_1 = sorted_x[-1][0][1]
		Blue_Top_1 = sorted_x[-1][0][2]
		Count_Top_2 = sorted_x[-2][1]
		Red_Top_2 = sorted_x[-2][0][0]
		Green_Top_2 = sorted_x[-2][0][1]
		Blue_Top_2 = sorted_x[-2][0][2]
		Count_Top_3 = sorted_x[-3][1]
		Red_Top_3 = sorted_x[-3][0][0]
		Green_Top_3 = sorted_x[-3][0][1]
		Blue_Top_3 = sorted_x[-3][0][2]
		Count_Top_4 = sorted_x[-4][1]
		Red_Top_4 = sorted_x[-4][0][0]
		Green_Top_4 = sorted_x[-4][0][1]
		Blue_Top_4 = sorted_x[-4][0][2]
		Count_Top_5 = sorted_x[-5][1]
		Red_Top_5 = sorted_x[-5][0][0]
		Green_Top_5 = sorted_x[-5][0][1]
		Blue_Top_5 = sorted_x[-5][0][2]
	else:
		# Error with image
		Count_Top_1 = 0
		Red_Top_1 = 0
		Green_Top_1 = 0
		Blue_Top_1 = 0
		Count_Top_2 = 0
		Red_Top_2 = 0
		Green_Top_2 = 0
		Blue_Top_2 = 0
		Count_Top_3 = 0
		Red_Top_3 = 0
		Green_Top_3 = 0
		Blue_Top_3 = 0
		Count_Top_4 = 0
		Red_Top_4 = 0
		Green_Top_4 = 0
		Blue_Top_4 = 0
		Count_Top_5 = 0
		Red_Top_5 = 0
		Green_Top_5 = 0
		Blue_Top_5 = 0

	# Final scaling step
	lengthcm = top_Length_noRotate*top_ScaleFactor
	widthcm = top_Width_noRotate*top_ScaleFactor
	heightcm = side_Width*side_ScaleFactor
	# New height method based on ratio of side pixel length vs.
	# top pixel length.
	angle_cor = (90-top_CameraDist_angle)-top_Angle_noRotate
	angle_cor_rad = math.radians(angle_cor)
	if angle_cor != 90 and side_Length != 0:
		side_length_cor = side_Length/math.cos(angle_cor_rad)
		side_ScaleFactor_ratiomethod = lengthcm/side_length_cor
		heightcm_ratiomethod = side_Width*side_ScaleFactor_ratiomethod
	else:
		heightcm_ratiomethod = 0

	if debugMode:
		debugImage = top_imageColor_crop
		cv2.drawContours(debugImage,top_Contours_noRotate,
			             top_largestIndex_noRotate,(0,0,255),1)
		bounds = cv2.minAreaRect(
			   top_Contours_noRotate[top_largestIndex_noRotate])
		box = cv2.cv.BoxPoints(bounds) # Box around seed
		box = np.int0(box)
		cv2.drawContours(debugImage,[box],0,(0,0,255),1)
		cv2.circle(debugImage,top_centerPoint_noRotate,2,(0,255,0),-1)
		cv2.putText(debugImage,'ctr',top_centerPoint_noRotate,
			        cv2.FONT_HERSHEY_SIMPLEX,.5,(0,255,0))
		lengthText = 'length (cm) = ' + str(lengthcm)
		widthText = 'width (cm) = ' + str(widthcm)
		areaText = 'area (pixels) = ' + str(top_Area_noRotate)
		colorValueText = 'color value (R G B) = (' + str(redAverage) + "," + str(greenAverage) + "," + str(blueAverage) + ")"
		heightText = 'height (cm) = ' + str(heightcm)
		volumeText = 'volume (cm3) = ' + str(volume)
		angleText = 'angle (degrees) = ' + str(top_Angle_noRotate)
		errorText = 'error = ' + error
		topxText = 'topXpos (pixel) = ' + str(topX)
		topyText = 'topYpos (pixel) = ' + str(topY)
		cv2.putText(debugImage,top_fileName,(10,20),
			        cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
		cv2.putText(debugImage,lengthText,(10,40),
			        cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
		cv2.putText(debugImage,widthText,(10,60),
			        cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
		cv2.putText(debugImage,areaText,(10,80),
			        cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
		cv2.putText(debugImage,colorValueText,(10,100),
			        cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
		cv2.putText(debugImage,heightText,(10,120),
			        cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
		cv2.putText(debugImage,volumeText,(10,140),
			        cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
		cv2.putText(debugImage,angleText,(10,160),
			        cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
		cv2.putText(debugImage,errorText,(10,180),
			        cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
		cv2.putText(debugImage,topxText,(10,200),
			        cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
		cv2.putText(debugImage,topyText,(10,220),
			        cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255))
		cv2.imshow(str(top_fileName) + ' final output',debugImage)
		cv2.waitKey(0)
		cv2.destroyWindow(str(top_fileName) + ' final output')

	writerObj.writerow({'number':str(x),
		                'file path':top_fileName,
						'length (cm)':str(lengthcm),
						'width (cm)':str(widthcm),
						'height (cm)':str(heightcm),
						'color value (R)':str(redAverage),
						'color value (G)':str(greenAverage),
						'color value (B)':str(blueAverage),
						'volume (cm3)':str(volume),
						'angle (degrees)':str(top_Angle_noRotate),
						'error':error,
						'height_ratiomethod (cm)':str(heightcm_ratiomethod),
						'count1':str(Count_Top_1),
						'r1':str(Red_Top_1),
						'g1':str(Green_Top_1),
						'b1':str(Blue_Top_1),
						'count2':str(Count_Top_2),
						'r2':str(Red_Top_2),
						'g2':str(Green_Top_2),
						'b2':str(Blue_Top_2),
						'count3':str(Count_Top_3),
						'r3':str(Red_Top_3),
						'g3':str(Green_Top_3),
						'b3':str(Blue_Top_3),
						'count4':str(Count_Top_4),
						'r4':str(Red_Top_4),
						'g4':str(Green_Top_4),
						'b4':str(Blue_Top_4),
						'count5':str(Count_Top_5),
						'r5':str(Red_Top_5),
						'g5':str(Green_Top_5),
						'b5':str(Blue_Top_5)})
	print('processed: ' + top_fileName + '  [' + str(x) + ']')
	x += 1
csvfile.close()
print('Done: data saved in ' + color_dir_name)
exit()