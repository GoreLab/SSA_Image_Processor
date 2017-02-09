""" saconfig.py - Configuration data for seed image analyzer scripts.

This file allows a seed analyzer script user to easily adjust
calibration and configuration variables across all relevant scripts
and libraries. Steps for inputting calibration data can
be found in the user guides on Google Drive. These variables are
responsible for converting from pixel length measurements made by the
script to real world distances. Units are indicated. It is useful to
record via a comment what data set the calibration data was taken from.

Specifics are explained below and in the documentation on Google Drive:

   	top_ScaleFactor - Measured manually at center of top images.
   								(units: centimeters/pixel)
	top_CameraDist_in - Distance in inches that side camera center
                            	line is out of the top image. See
                            	documentation.
                            	(units: inches)
    top_CameraDist_angle - Angle in degrees as measured from side
                               	camera center line to horizontal
                               	(x-axis) in the top image. See
                               	documentation.
                               	(units: degrees)
   	side_ScaleFactor_eqM - Using the Scaling Factor Calculator (see
                               	documentation) provides the user with
                               	two output variables describing a
                               	linear equation with M being the slope
                               	and B being the y-intercept.
    side_ScaleFactor_eqB - See side_ScaleFactor_eqM.
    side_ScaleFactor_intersectX - The x position where a line coming
                               	directly from the center of the
                               	side camera first intersects the
                               	top image. See documentation.

Advanced User Options:

	top_cropleft - When pre-processing the top image, this sets the
								number of columns to be cropped from
								the left side. It is referred to again
								later when calculating position for
								calibration calculations.
								(units: pixels)
	top_croptop - When pre-processing the top image, this sets the
								number of rows to be cropped from
								the top of the image. It is referred
								to again later when calculating
								position for calibration calculations.
								(units: pixels)
	debugmode - 1 for debug mode (shows images at each step), 0 for
								normal operation.

Developed and tested with Python 2.7.x and OpenCV 2.4.x.

Written by Kevin Kreher (kmk279@cornell.edu).
"""

__author__ = 'Kevin Kreher'

# !! Read documentation before making changes to this file !!
# MODIFY BELOW:
# Calibration data date: January 2, 2017
# Calibration data source: Oat calibration images
topScaleFactor = 0.002934381			# centimeters/pixel
topCameraDistin = 1.6875 			# inches
topCameraDistangle = 83.5 			# degrees
sideScaleFactoreqM = 0.0015
sideScaleFactoreqB = 0.0007
sideScaleFactorintersectX = 244

# ADVANCED USERS ONLY:
topCropleft = 300					# pixels
topCroptop = 300					# pixels
debugmode = 0
# add threshold
# add error levels
# !! Read documentation before making changes to this file !!