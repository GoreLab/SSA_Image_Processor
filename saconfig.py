""" saconfig.py - Configuration data for seed image analyzer scripts.

This file allows a seed analyzer script user to easily adjust
calibration and configuration variables across all relevant scripts
and libraries. Steps for inputting calibration data can
be found in the user guides on Google Drive. These variables are
responsible for converting from pixel length measurements made by the
script to real world distances. Units are indicated. It is useful to
record via a comment what data set the calibration data was taken from.

Specifics are explained below and in the documentation on Google Drive:

   	topScaleFactor - Measured manually at center of top images.
   								(units: centimeters/pixel)
    topCameraDistin - Distance in inches that side camera center
                            	line is out of the top image. See
                            	documentation.
                            	(units: inches)
    topCameraDistangle - Angle in degrees as measured from side
                               	camera center line to horizontal
                               	(x-axis) in the top image. See
                               	documentation.
                               	(units: degrees)
   	sideScaleFactoreqM - Using the Scaling Factor Calculator (see
                               	documentation) provides the user with
                               	two output variables describing a
                               	linear equation with M being the slope
                               	and B being the y-intercept.
    sideScaleFactoreqB - See sideScaleFactoreqM.
    sideScaleFactorintersectX - The x position where a line coming
                               	directly from the center of the
                               	side camera first intersects the
                               	top image. See documentation.
    debugmode - 1 for debug mode (shows images at each step), 0 for
								normal operation. Slows process.

Advanced User Options:

	topCropleft - When pre-processing the top image, this sets the
								number of columns to be cropped from
								the left side. It is referred to again
								later when calculating position for
								calibration calculations.
								(units: pixels)
	topCroptop - When pre-processing the top image, this sets the
								number of rows to be cropped from
								the top of the image. It is referred
								to again later when calculating
								position for calibration calculations.
								(units: pixels)
  sideCropxpos - Used when pre-processing the side image, this sets
                the x position representing the left side of the crop. Cropping
                the side image speeds up processing.
  sideCropypos - Used when pre-processing the side image, this sets
                the y position representing the bottom of the crop. Cropping
                the side image speeds up processing.
  sideCropwidth - Used when pre-processing the side image, this sets
                the width (x axis) of the crop. Cropping the side 
                image speeds up processing.
  sideCropheight - Used when pre-processing the side image, this sets
                the height (y axis) of the crop. Cropping the side 
                image speeds up processing.

Developed and tested with Python 2.7.x and OpenCV 2.4.x.

Written by Kevin Kreher (kmk279@cornell.edu).
"""

__author__ = 'Kevin Kreher'

# !! Read documentation before making changes to this file !!
# MODIFY BELOW:

# Calibration data date: January 2, 2017
# Calibration data source: Oat calibration images
topScaleFactor = 0.002934381		# centimeters/pixel
topCameraDistin = 1.6875 			# inches
topCameraDistangle = 83.5 			# degrees
sideScaleFactoreqM = 0.0015
sideScaleFactoreqB = 0.0007
sideScaleFactorintersectX = 244		#pixels
debugmode = 0

# ADVANCED USERS:
# Top image crops (referenced by samain.py and preproclib.py)
topCropleft = 300         # pixels
topCroptop = 300          # pixels
# Side image crops (referenced by preproclib.py - alter_side)
sideCropxpos = 850        # pixels
sideCropypos = 0          # pixels
sideCropwidth = 1000      # pixels
sideCropheight = 990      # pixels
# Error trigger values (referenced by samain.py)
topAreamaxerror = 40000 		# Top Area >= top_Area_max_error
topAreaminerror = 100 			# Top Area <= top_Area_min_error
topAnglemaxerror = 80 			# Top Angle > top_Angle_max_error
sideAreamaxerror = 16000 		# Side Area >= side_Area_max_error
sideAreaminerror = 100 			# Side Area <= side_Area_min_error
# Image binary threshold (used with OpenCV function cv2.threshold)
topthreshValue = 60
sidethreshVal = 15
# !! Read documentation before making changes to this file !!
