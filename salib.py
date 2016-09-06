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
    x,imageThreshed = cv2.threshold(imgBW,thrVal,255,cv2.THRESH_BINARY)
	# end threshold image


	# erode and dilate - removes small imperfections
    imageThreshed = erodeAndDilate(imageThreshed,np.ones((5,5),np.uint8),1)
	# end erode and dilate

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


def findLengthWidth(workingImg,thrVal):
    # find seed contour - at a certain index position in the list of contours found
    # workingImg - image with seed to find length and width of
    # thrVal - threshold value to be used
    #
    # returns a list of seed info (length, width, angle, area, center point, index of largest contour and contour list)
    # note the error output  is all 1


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
    # index - index of contour that traces seed
    # contourlist - list of all contours detected in the image
    # image - image that contours are being checked on (need for dimensions)
    #
    # returns a 1 or 0 indicating if the given contour hits the side of the image

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


def erodeAndDilate(image, kernel, timesRepeated):
    # erode: all the pixels near boundary will be discarded depending upon the size of kernel
    # dilate: pixels at a boundary will be dilated (opposite of erosion)

    # example kernels
    # Rectangular:
    # np.ones((5,5),np.uint8)
    #
    # Elliptical Kernel
    #cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    #array([[0, 0, 1, 0, 0],
    #   [1, 1, 1, 1, 1],
    #   [1, 1, 1, 1, 1],
    #   [1, 1, 1, 1, 1],
    #   [0, 0, 1, 0, 0]], dtype=uint8)
    image1 = cv2.dilate(image, kernel, iterations = timesRepeated)
    image2 = cv2.erode(image1, kernel, iterations = timesRepeated)
    return image2

def findVolume(topimage,sideimage,topImgVariables,sideImgVariables,threshSideVal,topScale,sideScale):
    # returns the volume in cm^3
    # algorithm: by using known seed paramters (angle,length,width) this
    # approximates an ellipse as the seed shape and
    # uses Riemann sums to give total value
    # V = sum( z , pi * x(z) * y(z) * dz )
    # where:
    # pi*a*b is the equation for area of an ellipse
    # z is length of seed in pixels (needs to be equal on both images)
    # x(z) is the top image seed width at pt z (in cm)
    # y(z) is the side image seed width at pt z (in cm)
    # dz is the width of each pixel (in cm)
    #
    # topimage - the top image of the seed
    # sideimage - the side image of the seed
    # topImgVariables - variables defining the top seed (passed through to save processing time)
    # sideImgVariables - variables defining the side seed (passed through to save processing time)
    # threshSideVal - the threshold value for the side image
    # topScale - scale factor for top image (cm/pixel)
    # sideScale - scale factor for side image (cm/pixel)
    #
    # returns the volume in cm^3

    #topImgVariables
    topLength = topImgVariables['length']
    topWidth = topImgVariables['width']
    topRotateAngle = topImgVariables['angle']
    topCenterPoint = topImgVariables['center']
    topArea = topImgVariables['area']
    topLargestIndex = topImgVariables['largestIndex'] 
    topContours = topImgVariables['contours']

    #sideImgVariables
    sideLength = sideImgVariables['length']
    sideWidth = sideImgVariables['width']
    #sideCenterPoint = sideImgVariables['center']

    # once we have length of top image seed and length of side image,
    # figure out scaling factor for side image sideLength*x=topLength where x = topLength/sideLength
    # resize side image and run findlengthwidth on it
    vol_length_SideScaleFactor = float(topLength)/float(sideLength) # pixels/pixels
    # assume length lies along x axis
    sideResizedImage = cv2.resize(sideimage,None,fx=vol_length_SideScaleFactor,fy=1)
    sideResizedImgVariables = findLengthWidth(sideResizedImage,threshSideVal)
    
    sideResizedLargestIndex = sideResizedImgVariables['largestIndex'] 
    sideResizedContours = sideResizedImgVariables['contours']
    sideResizedCenterPoint = sideResizedImgVariables['center']

    # debug check that the resize worked properly
    #print('sideimg angle = ' + str(sideResizedImgVariables['angle']))
    #print('sideimg resized length = ' + str(sideResizedImgVariables['length']))
    #print('sideimg resized width = ' + str(sideResizedImgVariables['width']))
    #print('topimg angle = ' + str(topRotateAngle))
    #print('topimg length = ' + str(topLength))
    #print('topimg width = ' + str(topWidth))


    # Create two mask images that contain the contours filled in - one for top one for side
    topimg = np.zeros_like(topimage)
    cv2.drawContours(topimg,topContours,topLargestIndex,255,-1)

    sideimg = np.zeros_like(sideResizedImage)
    cv2.drawContours(sideimg,sideResizedContours,sideResizedLargestIndex,255,-1)

    # rotate by 90 degrees so the numpy arrays are formatted more clearly (they
    # work with the ellipseAxes function as expected in the case of volume finding)
    topimg = cv2.transpose(topimg)
    sideimg = cv2.transpose(sideimg)

    # Access the image pixels and create a 1D numpy array then add to list
    topPts = np.where(topimg == 255)
    sidePts = np.where(sideimg == 255)
    #cv2.imshow('debug',topimg)
    #cv2.waitKey(0)
    #cv2.destroyWindow('debug')
    #cv2.imshow('debug side',sideimg)
    #cv2.waitKey(0)
    #cv2.destroyWindow('debug side')
    # (array([305, 305, 305, ..., 426, 426, 426]), array([507, 508, 509, ..., 707, 711, 712]))

    axesMeasurements = ellipseAxes(topPts,sidePts)
    # useful for debugging ellipseAxes
    #print('axes0 = ' + str(len(axesMeasurements[0])))
    #print('axes1 = ' + str(len(axesMeasurements[1])))

    dz = topScale # dz is ellipse width, we rescaled to use the topimage as the standard
    i = 0
    summation = 0
    integrate_over = 0

    # trying to use all available integration points
    # but in some cased the length rounds incorrectly
    # so we need to drop a shell of negligible size
    lenTop = len(axesMeasurements[0])
    lenSide = len(axesMeasurements[1])
    if lenSide < lenTop:
        integrate_over = lenSide
    else:
        integrate_over = lenTop


    while i < integrate_over:
        # scaling factors go in the line below
        ellipseArea = math.pi*(axesMeasurements[0][i]*topScale)*(axesMeasurements[1][i]*sideScale/vol_length_SideScaleFactor)
        summation += ellipseArea*dz
        i += 1

    return summation

def ellipseAxes(numpyTop,numpySide):
    # Given two numpy arrays, solves for the pixel length of the axes of the ellipses.
    # this is used in the actual calculation step of the volume function
    #
    # inputs
    # numpy arrays representing seed from the top
    # numpy arrays representing seed from the side
    # example:
    # (array([305, 305, 305, ..., 426, 426, 426]), array([507, 508, 509, ..., 707, 711, 712]))
    # or (array([656, 656, 656, ..., 732, 732, 733]), array([1073, 1074, 1075, ..., 1081, 1082, 1078]))
    # output
    # list of x(z) values (ellipse a axis) - in pixels
    # list of y(z) values (ellipse b axis) - in pixels

    # start from the same side of the seed (verify this) and determine the width at that point
    #   TOP:
    # - at start of x: record 507... end of x record 509
    # - difference 509-507 = height[0]
    # - at x+1: record 506... end of x+1 record 510
    # - difference 510-506 = height[1]
    # - end case
    #   SIDE:
    # - at start of x: record 100... end of x record 103
    # - see above

    x = 0
    y = 1

    # debug outputs
    #print('TOPxlen = ' + str(len(numpyTop[x])))
    #print('TOPylen = ' + str(len(numpyTop[y])))
    #print('SIDExlen = ' + str(len(numpySide[x])))
    #print('SIDEylen = ' + str(len(numpySide[y])))
    #np.set_printoptions(threshold=np.inf) #show the whole numpy array (CAN BE HUGE)
    #print(numpyTop)
    #print(numpySide)

    i = 0
    n = 0
    top = []
    prevTopPt = numpyTop[x][0]
    starty = numpyTop[y][0]
    while i < len(numpyTop[x]):
        # numpyTop[x] is the array of x values
        # numpyTop[y] is the array of y values
        if prevTopPt != numpyTop[x][i]:
            # aka if the x value changes, we know to measure how much y has changed
            endy = numpyTop[y][i-1]
            topCalculated = endy-starty
            top.append(topCalculated)
            #print('top[n] = ' + str(top[n]))
            n += 1
            # we have moved over one in the seed, calculate the last difference
            # save it as a top[n] and move on
            starty = numpyTop[y][i]
            prevTopPt = numpyTop[x][i]
        i += 1

    i = 0
    m = 0
    side = []
    prevSidePt = numpySide[x][0]
    starty = numpySide[y][0]
    while i < len(numpySide[x]):
        # numpySide[x] is the array of x values
        # numpySide[y] is the array of y values
        if prevSidePt != numpySide[x][i]:
            # aka if the x value changes, we know to measure how much y has changed
            endy = numpySide[y][i-1]
            sideCalculated = endy-starty
            side.append(sideCalculated)
            #print('top[m] = ' + str(top[m]))
            m += 1
            starty = numpySide[y][i]
            prevSidePt = numpySide[x][i]
        i += 1


    return (top,side)



def calcSideScaleFactor(centerpoint,cropleft,croptop,topScale,eqM,eqB,xIntersect,distCamera_in,distCamera_angle,seedAngle_deg,seedLength_top):
    # set side scale factor (cm/pixel) based on center point
    # can work with a preexisting crop on the images (given as variables)
    # 
    # args:
    # centerpoint - (x,y) of seed center point
    # cropleft - amount left side was cropped by, a modification would be made if right crop
    # croptop - amount top was cropped by, a modification would be made if bottom crop
    # topScale - topscale amount (cm/pixel)
    # eqM - "distance from camera equation" slope
    # eqB - "distance from camera equation" offset
    # xIntersect - in pixels, where ruler exits bottom of image, intersect point in x (y=bottom row)
    # distCamera_in - distance camera is from bottom of frame
    # distCamera_angle - angle at which the distCamera was measured
    # seedAngle_deg - calculated seed angle in degrees (0 being lengthwise infront of side camera, 90 facing)
    # seedLength_top - calculated seed length from top image in pixels
    # 
    #
    # returns:
    # calculates sideScaleFactor for use in samain script

    distCamera_angle_rad = distCamera_angle*(math.pi/180) # convert to radians for math fncs

    # given x and y in inches that the side camera is out of the topImage shot
    distCamera_cm = 2.54*distCamera_in
    distCamera = distCamera_cm/topScale
    distCamera_y_component = distCamera*math.sin(distCamera_angle_rad)

    # use centerpoint to calculate the distance in pixels from the lens itself
    ximgsize = 1920-cropleft
    yimgsize = 1080-croptop

    X = abs(centerpoint[0]-xIntersect)
    Y = abs(yimgsize-centerpoint[1])
    y_x = Y*1.0/X
    #print('y_x = '+str(y_x))

    phi = math.atan(y_x)
    #print('phi = ' + str(phi))
    a = math.sqrt((X)**2+(Y)**2)

    #print('a = '+str(a))

    b_sqrd = (a)**2 + (distCamera_y_component)**2 - (2*a*distCamera_y_component*(math.cos(abs(phi)+(math.pi)/2)))
    b = math.sqrt(b_sqrd) # pixels
    b_cm = b*topScale # centimeters
    b_in = b_cm/2.54 # inches

    #print('b pixels = '+str(b))

    # for seeds that are at extreme angles, the optics cause the widest part to be closer to the camera
    # the following is for seeds where this is the case, as it accounts for the optical skew of a seed
    # with its length perpendicular to the camera lens
    if abs(seedAngle_deg) >= 45:
        lengthCorrFactor = seedLength_top/4
        lengthCorrFactor_cm = lengthCorrFactor*topScale # centimeters
        lengthCorrFactor_in = lengthCorrFactor_cm/2.54
        print('lengthCorrFactor_in = ' + str(lengthCorrFactor_in))
        b_in = b_in+lengthCorrFactor_in

    # given distance from side camera, use eqM and eqB (solved from topScale image)
    print('b_in = '+str(b_in))
    scalefactor = b_in*eqM+eqB

    return scalefactor


