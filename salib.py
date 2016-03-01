# salib.py
# library containing functions for samain.py
#
# author:
# Kevin Kreher
# KMK279@cornell.edu
#
# compatibility python version 2.7.10

import numpy as np
import cv
import cv2
import math
import glob
import copy

def imageThreshold(img,threshVal):
	# converts an image to black a white
	#
	# img - is the image to threshold
	# threshVal - always an integer between 0 and 255 that
	# sets the threshold algorithm cutoff value
	#
	# returns a thresholded BW image imgBW

	maxVal = 255 # full swing B/W
	x,imgBW = cv2.threshold(img,threshVal,maxVal,cv2.THRESH_BINARY)
	return imgBW


# UNUSED
def blendImages(img1,img2,opac):
	# blends two images
	# transparency % = 1-(opac/100)
	# dimensions and channels of images must agree
	#
	# img1 - image (transparent)
	# img2 - image (background)
	# opac - opacity for the image, always an
	# FLOAT between 0.0 and 100.0 (floats must have .0 at end)
	#
	# returns the resulting blended image blendResult

	val1 = opac/100
	val2 = 1-val1
	blendResult = cv2.addWeighted(img1,val1,img2,val2,0)
	return blendResult


def rotateImage(src,angl,midpt):
	# rotates the given image by the given angle
	# around the given midpoint
	#
	# src - is the image to be rotated
	# angl - the angle to rotate the image by around the midpoint
	# midpt - midpoint to rotate about
	#
	# returns the rotated image imgRot

	rows,cols = src.shape[:2]
	M = cv2.getRotationMatrix2D((midpt[0],midpt[1]),angl,1)
	imgRot = cv2.warpAffine(src,M,(cols,rows))
	return imgRot


def findMaxSizeBounds(imgBW,thrVal):
	# finds the object with the maximimum area
	# to do this it performs thresholding on a BW image
	# base on well conditioned parameters and images
	# this max area object should be the seed
	#
	# imgBW - black and white image containing the seed
	# thrVal - value to use for thresholding (set to 135 default)
	#
	# returns the bounding info formatted as a dict structure
	# 'contourList' is a list containing the contour positions,
	# and 'indexSeed' is the index position of the largest contour

	# threshold image
	imageThreshed = imageThreshold(imgBW,thrVal)
	# end threshold image

	# find contours
	# create copy of image before passing to findContours
	imageContour = copy.copy(imageThreshed)
	contours, hierarchy = cv2.findContours(imageContour,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

	# we need to find the contour with max area, the seed
	i = 0
	largest = 0
	largestIndex = 0
	while i < len(contours):
		area = cv2.contourArea(contours[i])
		if area > largest:
			largest = area
			largestIndex = i
		i += 1
	# end find contours

	return {'seedIndex':largestIndex, 'contourList':contours}


def lensCorrectImages(row,col):
    # removes lens distortion
    # algorithm works on all images in working directory
    # must be preprocessed with Picasa (note: Picasa makes all jpg)
    #
    # Sources:
    # http://opencv-python-tutroals.readthedocs.org
    # /en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html
    # 
    # http://docs.opencv.org/2.4/doc/tutorials/calib3d/camera_calibration
    # /camera_calibration.html
    # 
    # Based of the asymmetrical circle pattern found below:
    # http://docs.opencv.org/2.4/_downloads/acircles_pattern.png
    #
    # MUST HAVE >10 CALIBRATION IMAGES IN DIRECTORY /calibration/ as .jpg
    # MUST HAVE SEED IMAGES IN DIRECTORY /seedImages/ as .jpg
    #
    # row - rows of asymmetrical circle pattern to detect (can be smaller than printed)
    # col - columns of asymmetrical circle pattern to detect (can be smaller than printed)
    # be sure that image directory locations are correct
    #
    # returns 1

    pts_x = row #6
    pts_y = col #7

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((pts_x*pts_y,3), np.float32)
    objp[:,:2] = np.mgrid[0:pts_y,0:pts_x].T.reshape(-1,2)

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    # calibration image directory, need at least 10
    images = glob.glob('calibration/*.jpg')

    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        # Find the circle centers
        ret, centers = cv2.findCirclesGrid(gray, (pts_y,pts_x),cv2.CALIB_CB_SYMMETRIC_GRID)

        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)

            # unused for circle pattern
            #corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)

            imgpoints.append(centers)

            # Draw and display the centers
            img = cv2.drawChessboardCorners(img, (pts_y,pts_x), centers,ret)
            cv2.imshow('img',img)
            cv2.waitKey(500)

    cv2.destroyAllWindows()

    # calculate camera characteristics
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)


    # undistort all images in working directory
    imagesCorr = glob.glob('seeedImages/TopImage*.jpg')
	# undistort top images only

    for fname in imagesCorr:

    	# debug test
    	print fname

    	# undistort the specified image
    	img = cv2.imread(fname)
    	h,  w = img.shape[:2]
    	newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
    	dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

    	# crop the image
    	x,y,w,h = roi
    	dst = dst[y:y+h, x:x+w]
    	cv2.imshow(fname,dst)
    	cv2.waitKey(0)
    	#cv2.imwrite(fname,dst)

    return 1


def findLengthWidth(workingImg,thrVal):
    # find seed contour - at a certain index position in the list of contours found
    # TODO input and output, error output (all 1)

    seedBounds = findMaxSizeBounds(workingImg,thrVal)
    largestIndex = seedBounds['seedIndex']
    contours = seedBounds['contourList']

    # error catching if NO CONTOUR IS FOUND
    if len(contours) == 0:
        return {'length':1, 'width':1, 'angle':0,
            'center':(1,1), 'area':1, 'largestIndex':0, 'contours':[np.array([[[199, 519]]], dtype=np.int32)]}


    # create rectangle (rotated) containing seed, and find midpoints
    bounds = cv2.minAreaRect(contours[largestIndex])
    # box used for finding midpoints and drawing
    box = cv2.cv.BoxPoints(bounds) # note cv2.cv.BoxPoints(rect) will be removed in openCV 3
    #cv2.boxPoints(bounds) - if openCV 3
    box = np.int0(box)
    # find midpoints
    # A = midpoint of points at box[0] and box[1]
    A = ((box[0][0]+box[1][0])/2 , (box[0][1]+box[1][1])/2)
    # B = midpoint of box[1] and box[2]
    B = ((box[1][0]+box[2][0])/2 , (box[1][1]+box[2][1])/2)
    # C = midpoint of box[2] and box[3]
    C = ((box[2][0]+box[3][0])/2 , (box[2][1]+box[3][1])/2)
    # D = midpoint of box[3] and box[0]
    D = ((box[3][0]+box[0][0])/2 , (box[3][1]+box[0][1])/2)
    # center = midpoints of A-C line and B-D
    centerPoint = ((B[0]+D[0])/2 , (A[1]+C[1])/2)
    # end create rectangle, midpoints

    # calculate geometry - length, width, area
    areaTop = cv2.contourArea(contours[largestIndex])
    distance1 = math.sqrt(math.pow(B[0]-D[0],2)+math.pow(B[1]-D[1],2))
    distance2 = math.sqrt(math.pow(A[0]-C[0],2)+math.pow(A[1]-C[1],2))
    # assign correct width or length
    if distance1 > distance2:
        length = distance1
        width = distance2
        rotateAngle = 90+bounds[2]
    else:
        length = distance2
        width = distance1
        rotateAngle = bounds[2]
    # end geometry calculation
    return {'length':length, 'width':width, 'angle':rotateAngle,
    'center':centerPoint, 'area':areaTop, 'largestIndex':largestIndex, 'contours':contours}


def pixelSizeCalibrate(imgBW,thrVal,modelLength,modelWidth):
    # returns parameters useful for the calibration of pixel distances to
    # standard unit measurements (does not correct for lens distortion).
    #
    # imgBW - input image with a calibration rectangle
    # thrVal - value to use for thresholding (set to 150 default)
    # modelLegnth - must be in centimeters, measured length of "model"
    # modelWidth - must be in centimeters, measured width of "model"
    #
    # returns two scaling factors - length, width (in cm/pixel) as a tuple

    imgBW_inverted = cv2.bitwise_not(imgBW)
    calibImageVariables  = findLengthWidth(imgBW_inverted,thrVal)
    #calibLepngth = calibImageVariables['length']
    #calibWidth = calibImageVariables['width']
    #calibRotateAngle = calibImageVariables['angle']
    #calibCenterPoint = calibImageVariables['center']
    #calibArea = calibImageVariables['area']
    #calibLargestIndex = calibImageVariables['largestIndex'] 
    #calibContours = calibImageVariables['contours']

    # find known shape
    lengthModelpix = calibImageVariables['length'] # in pixels - found above
    widthModelpix = calibImageVariables['width'] # in pixels - found above
    lengthModelcm = modelLength
    widthModelcm = modelWidth
    # pixel scale
    lengthScaleFactor = lengthModelcm/lengthModelpix
    widthScaleFactor = widthModelcm/widthModelpix

    # debug output
    #debugImage = imageScale
    # draw contour trace
    #cv2.drawContours(debugImage,scaleVariables['contours'],scaleVariables['largestIndex'],(0,0,255),1)
    # draw rectangle
    # create top image rectangle (rotated) containing seed, and find midpoints
    #bounds = cv2.minAreaRect(scaleVariables['contours'][scaleVariables['largestIndex']])
    # box used for finding midpoints and drawing
    #box = cv2.cv.BoxPoints(bounds) # note cv2.cv.BoxPoints(rect) will be removed in openCV 3
    #        cv2.boxPoints(bounds) - if openCV 3
    #box = np.int0(box)
    #cv2.drawContours(debugImage,[box],0,(0,0,255),1)
    #cv2.imwrite('debug.bmp',debugImage)
    #cv2.imshow('debugOutput',debugImage)
    #cv2.waitKey(0)
    #cv2.destroyWindow('debugOutput')
    #print(lengthModelpix)
    #print(widthModelpix)
    #print(lengthScaleFactor)
    #print(widthScaleFactor)

    return lengthScaleFactor,widthScaleFactor

def contourHitsEdge(index,contourlist,image):
    # returns a 1 or 0 that signifies that the given contour specified
    # by contourlist[index] hits the maximums (edges) of the image
    # this is made more difficult by our use of CHAIN_APPROX_SIMPLE when
    # saving the output coordinates of a contour
    #
    # inputs 
    #
    # outputs

    # iterate over outline and look for jumps at borders
    # borders
    x_left = 1
    x_right = image.shape[1]-2 # numpy arrays are strange?
    #print(x_right)
    y_top = 1
    y_bottom = image.shape[0]-2
    #print(y_bottom)
    # loop variables
    x_prev = 0
    y_prev = 0
    edgeConflicts = 0

    for each_pixel in contourlist[index]:
        #print(each_pixel)
        x = each_pixel[0][0]
        y = each_pixel[0][1]
        if (x == x_left or x == x_right) and (y > y_prev or y < y_prev):
            #print('case1')
            edgeConflicts+=1
        if (y == y_top or y == y_bottom) and (x > x_prev or x < x_prev):
            #print('case2')
            edgeConflicts+=1
        x_prev = x
        y_prev = y

    #print('edgeconflits = ' + str(edgeConflicts))
    if edgeConflicts >= 1:
        # we must be cutting something off from the image
        return 1
    return 0














