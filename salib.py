""" salib.py - Library of functions used in the script samain.py.

A library full of functions used in the main seed analyzing script.
Each function has an associated Docstring explaining the functionality.
Developed and tested with Python 2.7.x and OpenCV 2.4.x.

Written by Kevin Kreher (kmk279@cornell.edu).
"""

__author__ = 'Kevin Kreher'

import numpy as np
import cv2
import math
import glob
import copy

def rotateImage(src,angl,midpt):
	""" Returns an image rotated around a midpoint.

    src - The image to be rotated
    angl - the angle to rotate the image by around the midpoint
    midpt - midpoint to rotate about
    """
	rows,cols = src.shape[:2]
	M = cv2.getRotationMatrix2D((midpt[0],midpt[1]),angl,1)
	imgRot = cv2.warpAffine(src,M,(cols,rows))
	return imgRot

def findMaxSizeBounds(imgBW,thrVal):
    """ Returns the bounding info of the max sized object in the image.

    The bouding information is returned in a dictionary containing:
    'contourList' - a list containing the outer countours of objects
    in the image.
    'indexSeed' - the index position of the largest object in the image
    by area.
    The algorithm finds the object with the maximimum area by
    thresholding the given B/W image and searching through all found
    blobs in the image.

    imgBW - black and white image containing the seed
    thrVal - value to use for thresholding operation
    """
    x,imageThreshed = cv2.threshold(imgBW,thrVal,255,cv2.THRESH_BINARY)
    imageThreshed = erodeAndDilate(imageThreshed,np.ones((5,5)),1)
    imageContour = copy.copy(imageThreshed) # Copy for operating on
    contours, hierarchy = cv2.findContours(imageContour,cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)
    i = 0
    largest = 0
    largestIndex = 0
    while i < len(contours):
		area = cv2.contourArea(contours[i])
		if area > largest:
			largest = area
			largestIndex = i
		i += 1
    return {'seedIndex':largestIndex, 'contourList':contours}

def findLengthWidth(workingImgBW,thrVal):
    """ Returns information about the largest object in an image.

    The information returned is a list of info about the largest object
    in the image such as the length, width, angle, area, center point,
    index of largest contour and the images contour list.
    Note that the output if there is an error is all 1's except for
    angle and largestIndex which are 0.

    workingImgBW - B/W image with seed to find length and width of
    thrVal - value to use for thresholding operation
    """
    seedBounds = findMaxSizeBounds(workingImgBW,thrVal)
    largestIndex = seedBounds['seedIndex']
    contours = seedBounds['contourList']
    if len(contours) == 0:
        # Error catch if no contour is found.
        return {'length':1, 'width':1, 'angle':0,
                'center':(1,1), 'area':1, 'largestIndex':0,
                'contours':[np.array([[[1, 1]]], dtype=np.int32)]}
    bounds = cv2.minAreaRect(contours[largestIndex])
    box = cv2.cv.BoxPoints(bounds) # Create a rotated rectangle
    box = np.int0(box) # The box has four corners
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
    # Calculate geometry - length, width, area
    areaTop = cv2.contourArea(contours[largestIndex])
    distance1 = math.sqrt(math.pow(B[0]-D[0],2)+math.pow(B[1]-D[1],2))
    distance2 = math.sqrt(math.pow(A[0]-C[0],2)+math.pow(A[1]-C[1],2))
    if distance1 > distance2:
        length = distance1 # Length will be the longer distance always
        width = distance2
        rotateAngle = 90+bounds[2]
    else:
        length = distance2
        width = distance1
        rotateAngle = bounds[2]
    return {'length':length, 'width':width, 'angle':rotateAngle,
            'center':centerPoint, 'area':areaTop, 'largestIndex':largestIndex,
            'contours':contours}

def pixelSizeCalibrate(imgBW,thrVal,modelLength,modelWidth):
    """ Returns conversion from pixel to centimeter lengths.

    Given an image with an appropriate model (commonly an all black
    rectangle against an all white background) this function returns
    two scaling factors - length, width (in cm/pixel) as a tuple.
    Be sure that length of model is always greater than width of model.
    
    imgBW - B/W image with a calibration rectangle
    thrVal - value to use for thresholding operation
    modelLegnth - must be in centimeters, measured length of "model"
    modelWidth - must be in centimeters, measured width of "model"
    """
    imgBW_inverted = cv2.bitwise_not(imgBW)
    calib_Variables  = findLengthWidth(imgBW_inverted,thrVal)
    lengthModelpix = calib_Variables['length'] # pix
    widthModelpix = calib_Variables['width'] # pix
    lengthModelcm = modelLength # cm
    widthModelcm = modelWidth # cm
    lengthScaleFactor = lengthModelcm/lengthModelpix #cm/pix
    widthScaleFactor = widthModelcm/widthModelpix # cm/pix
    return lengthScaleFactor,widthScaleFactor

def contourHitsEdge(index,contourlist,image):
    """ Indicates if a contour hits the image edge (0=No 1=Yes).

    Returns a 1 = conflict or 0 = no conflict that signifies that the
    given contour specified by contourlist[index] hits the maximums
    (edges) of the image.
    
    index - index of contour of interest
    contourlist - list of all contours detected in the image
    image - image that contours are being checked on
    """
    x_left = 1 # Find image borders
    x_right = image.shape[1]-2
    y_top = 1
    y_bottom = image.shape[0]-2
    x_prev = 0 # Loop variables, we check each x and y combination.
    y_prev = 0
    edgeConflicts = 0
    for each_pixel in contourlist[index]:
        x = each_pixel[0][0]
        y = each_pixel[0][1]
        if (x == x_left or x == x_right) and (y > y_prev or y < y_prev):
            edgeConflicts+=1
        if (y == y_top or y == y_bottom) and (x > x_prev or x < x_prev):
            edgeConflicts+=1
        x_prev = x
        y_prev = y
    if edgeConflicts >= 1:
        return 1
    return 0

def erodeAndDilate(image, kernel, timesRepeated):
    """ Returns the image after being eroded and dilated.

    Eroding has the effect of filtering 'peninsulas' or similar near
    the boundary of a contour. Strength depends on size of kernel.
    Dilate is the opposite of erosion and grows pixels near a boundary.

    image - input image, must have previously been thresholded (B/W)
    kernel - filter shape, see examples below
    timesRepeated - # of times to repeat each action (individually)

    Example kernels:
    Rectangular
    np.ones((5,5),np.uint8)

    Elliptical
    cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    array([[0, 0, 1, 0, 0],
           [1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1],
           [0, 0, 1, 0, 0]], dtype=uint8)
    """
    image1 = cv2.dilate(image, kernel, iterations = timesRepeated)
    image2 = cv2.erode(image1, kernel, iterations = timesRepeated)
    return image2

def findVolume(topimage,sideimage,topImgVariables,sideImgVariables,
               threshSideVal,topScale,sideScale):
    """ Returns the volume of a specified object in cm^3.

    The algorithm works by using known blob (seed) and image paramters
    (length,width,scale factors) to approximate a set of ellipses that
    estimate the blob (ssed) cross-section. These ellipses are then
    summed along the length of the blob (aka Riemann sum) to give
    the volume.

    This is expressed mathematically as:

    V = sum(z, pi * x(z)/2 * y(z)/2 * dz)

    where:
    pi*a*b is area of an ellipse (a and b being semi-major/minor axes)
    z is length of seed in pixels (necessarily the same for both views
                                   of the blob)
    x(z) is the top image blob width at pt z (in cm)
    y(z) is the side image blob width at pt z (in cm)
    dz is the width of each pixel (in cm)

    topimage - the top image of the seed
    sideimage - the side image of the seed
    topImgVariables - variables defining the top seed
    sideImgVariables - variables defining the side seed
    threshSideVal - value to use for thresholding operation
    topScale - scale factor for top image (cm/pixel)
    sideScale - scale factor for side image (cm/pixel)
    """
    topLength = topImgVariables['length']
    topWidth = topImgVariables['width']
    topRotateAngle = topImgVariables['angle']
    topCenterPoint = topImgVariables['center']
    topArea = topImgVariables['area']
    topLargestIndex = topImgVariables['largestIndex'] 
    topContours = topImgVariables['contours']
    sideLength = sideImgVariables['length']

    # Correct for different length of top and side image of blob or
    #    see by resizing the side image by a factor to make the
    #    lengths equal. Length is assumed to lie along the x-axis.
    #    Side variables are then recalculated.
    #    vol_length_SideScaleFactor - units are pixels/pixels
    vol_length_SideScaleFactor = float(topLength)/float(sideLength)
    sideResizedImage = cv2.resize(sideimage,None,
                                  fx=vol_length_SideScaleFactor,fy=1)
    sideResizedImgVariables = findLengthWidth(sideResizedImage,threshSideVal)
    sideResizedLargestIndex = sideResizedImgVariables['largestIndex'] 
    sideResizedContours = sideResizedImgVariables['contours']
    sideResizedCenterPoint = sideResizedImgVariables['center']

    # Mask images that contain the contours filled in (top and side).
    topimg = np.zeros_like(topimage) 
    cv2.drawContours(topimg,topContours,topLargestIndex,255,-1)
    sideimg = np.zeros_like(sideResizedImage)
    cv2.drawContours(sideimg,sideResizedContours,
                     sideResizedLargestIndex,255,-1)

    # Rotate by 90 degrees and create a list of pixels for clarity
    #    before passing to ellipseAxes.
    #    ellipseAxes() will return a list of blob (seed) cross-section
    #    measurements along both side and top image axes. If refering
    #    the simple equation for ellipse area above, this function is
    #    returning 2*a and 2*b for each ellipse that will be used in
    #    the summation.
    topimg = cv2.transpose(topimg)
    sideimg = cv2.transpose(sideimg)
    topPts = np.where(topimg == 255)
    sidePts = np.where(sideimg == 255)
    axesMeasurements = ellipseAxes(topPts,sidePts)

    # The algorithm uses all available integration points (pixels)
    #    but in some cased the length of either the top or
    #    resized side image rounds incorrectly and the lengths
    #    do not match - dropping a shell of negligible size at the far
    #    end of a blob (seed) fixes this. After this the loop variables
    #    used in the Riemann sum are declared.
    lenTop = len(axesMeasurements[0])
    lenSide = len(axesMeasurements[1])
    integrate_over = 0
    if lenSide < lenTop:
        integrate_over = lenSide
    else:
        integrate_over = lenTop
    dz = topScale # Pixel width, using topimage as the standard
    i = 0
    summation = 0.0
    while i < integrate_over:
        aaxis = axesMeasurements[0][i] # Top axis diameter in pixels
        baxis = axesMeasurements[1][i] # Side axis diameter in pixels
        ellipseArea = math.pi*(aaxis/2)*(baxis/2) # pixels
        ellipseArea_scaled = ellipseArea*topScale*sideScale # cm^2
        summation += ellipseArea_scaled*dz # cm^3
        i += 1
    return summation

def ellipseAxes(numpyTop,numpySide):
    """ Returns two lists containg lengths of a and b axes.

    Given two numpy arrays representing the blob (seed) ellipseAxes
    records the number of rows in each column for both arrays. When
    assuming the blob (seed) cross-section is an ellipse, this
    function returns the major and minor-axes measurements as pixel
    measurements. The algorithm works by following these steps:
    1. Start from the same side of the blob (seed) and determine the
           number of columns (width) at that point. Record this for
           both top and side.
    2. Step through each column (along the length) and record the
           the number of rows (width).
    An example working with actual arrays would be closer to:
    1. Where x[0]=x[1]=x[2], y[0] and y[2]. Thus the difference
           giving width is y[2]-y[0] = width[0].
    2. At x[3]: record y[3], when x[3]!=x[i] record y[i]. This
           difference y[i]-y[3] = width[1]. Continue until x[i] is
           exhausted.
    These steps are the same for both top and side. The returned value
    is a tuple saved as (top,side) containing the following:
    a list of x(z) values (ellipse a axis)/top - in pixels
    a list of y(z) values (ellipse b axis)/side - in pixels

    numpyTop - numpy arrays representing seed from the top
    numpySide - numpy arrays representing seed from the side
    
    example numpy array input:
    (array([305, 305, 305, ..., 426, 426, 426]),
     array([507, 508, 509, ..., 707, 711, 712]))
    or (array([656, 656, 656, ..., 732, 732, 733]),
        array([1073, 1074, 1075, ..., 1081, 1082, 1078]))
    """
    x = 0 # Indicate which part of the array is x or y axis.
    y = 1
    i = 0
    top = []
    prevTopPt = numpyTop[x][0]
    starty = numpyTop[y][0]
    while i < len(numpyTop[x]):
        # numpyTop[x] is the array of x values
        # numpyTop[y] is the array of y values
        if prevTopPt != numpyTop[x][i]:
            # If the x value changed, measure how much y has changed.
            endy = numpyTop[y][i-1]
            topCalculated = endy-starty
            top.append(topCalculated)
            starty = numpyTop[y][i]
            prevTopPt = numpyTop[x][i]
        i += 1
    i = 0
    side = []
    prevSidePt = numpySide[x][0]
    starty = numpySide[y][0]
    while i < len(numpySide[x]):
        # numpySide[x] is the array of x values
        # numpySide[y] is the array of y values
        if prevSidePt != numpySide[x][i]:
            # If the x value changed, measure how much y has changed.
            endy = numpySide[y][i-1]
            sideCalculated = endy-starty
            side.append(sideCalculated)
            starty = numpySide[y][i]
            prevSidePt = numpySide[x][i]
        i += 1
    return (top,side)

def calcSideScaleFactor(centerpoint,cropleft,croptop,topScale,eqM,eqB,
                        xIntersect,distCamera_in,distCamera_angle,
                        seedAngle_deg,seedLength_top):
    """ Returns the side scale factor.

    Calculates the side scale factor (in units cm/pixel) given
    calibration data and the position of the blob (seed) in the top
    image. When calibrated correctly the script accurately finds the
    distance of the blob (seed) from the side camera. With this
    information and the equation variables (found externally with the
    calculator - see documentation on Google Drive) the side scale
    factor is calculated in the last step. If the top image is cropped
    before the centerpoint input is calculated, the script can account
    for this.
    
    centerpoint - (x,y) of seed center point
    cropleft - amount left side was cropped by (done in pre-processing)
                   by the function alter_top_crop (in preproclib.py).
    croptop - amount top was cropped by (done in pre-processing)
                  by the function alter_top_crop (in preproclib.py).
    topScale - topscale amount (cm/pixel)
    eqM - "distance from camera equation" slope
    eqB - "distance from camera equation" offset
    xIntersect - in pixels, where ruler exits bottom of image, 
                     intersect point in x (y=bottom row)
    distCamera_in - distance camera is from bottom of frame
    distCamera_angle - angle at which the distCamera was measured
    seedAngle_deg - calculated seed angle in degrees (0 being
                        lengthwise infront of side camera, 90 facing)
    seedLength_top - calculated seed length from top image in pixels
    """
    # Convert angle from degrees to radians
    distCamera_angle_rad = distCamera_angle*(math.pi/180)
    distCamera_cm = 2.54*distCamera_in
    distCamera = distCamera_cm/topScale
    distCamera_y_component = distCamera*math.sin(distCamera_angle_rad)

    # Use blob (seed) centerpoint to calculate the distance in pixels 
    #    from the lens to the blob (seed), saved as a.
    ximgsize = 1920-cropleft
    yimgsize = 1080-croptop
    X = abs(centerpoint[0]-xIntersect)
    Y = abs(yimgsize-centerpoint[1])
    y_x = Y*1.0/X
    phi = math.atan(y_x)
    a = math.sqrt((X)**2+(Y)**2) # pixels
    b_sqrd = (a)**2 + (distCamera_y_component)**2 - (2*a*distCamera_y_component*(math.cos(abs(phi)+(math.pi)/2)))
    b = math.sqrt(b_sqrd) # side b of triangle pixels
    b_cm = b*topScale # centimeters
    b_in = b_cm/2.54 # inches
    # For seeds (blobs) that are at extreme angles, the optics cause
    #    the widest part to be closer to the camera. The following
    #    correction is for seeds where this is the case, as it accounts
    #    for the optical skew of a blob (seed) where this is the case.
    if abs(seedAngle_deg) >= 45:
        lengthCorrFactor = seedLength_top/4
        lengthCorrFactor_cm = lengthCorrFactor*topScale # centimeters
        lengthCorrFactor_in = lengthCorrFactor_cm/2.54 # inches
        b_in = b_in+lengthCorrFactor_in
    # Given distance from side camera, use eqM and eqB (solved from
    #    topScale image with the external calcuator).
    scalefactor = b_in*eqM+eqB
    return scalefactor