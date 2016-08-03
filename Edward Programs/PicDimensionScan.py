__author__ = 'Edward Buckler V'
# Program made in response to many of the images from ImageCleaner not being cropped correctly. Has two functions
# getting the average dimensions of images in a directory and placing all images over a set value pixels
import cv2
import os, sys
import shutil
# Asks user for the directory containing the images and what process should be run
dirPath = raw_input("input path of directory with images in it: ")
programToRun = raw_input("Which program to run average (average) or flag (find ones which are too large)?: ")
# If "flag" has been choosen as the function to run then the user is prompted to input the max width
if programToRun == "flag":
    maxWidth = input("please enter in the value at which images will be flagged (550 advised)(integer): ")
# Variables generally used in getting average
widthTotal = 0
heightTotal = 0
# If the user inputed something other than "flag" or "average" an error is thrown
if programToRun != "flag" and programToRun != "average":
    sys.exit("please put in average or flag (case counts!) for what program to run!")
# Main functions of program
else:
    count = 0
    for file in os.listdir(dirPath):
        # If the function chosen was "average"
        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg") and programToRun == "average":
            image = cv2.imread(dirPath + "\\" + file)
            X = (len(image))
            Y = (len(image[0,]))
            widthTotal += X
            heightTotal += Y
            count += 1
        # If the function chosen was "flag"
        if file.endswith(".jpg") or file.endswith(".png") and programToRun == "flag":
            image = cv2.imread(dirPath + "\\" + file)
            X = (len(image))
            Y = (len(image[0,]))
            if Y >= maxWidth:
                if not os.path.exists(dirPath + "\\FlaggedImages"):
                    os.makedirs(dirPath + "\\FlaggedImages")
                shutil.move(dirPath + "\\" + file, dirPath + "\\FlaggedImages")
                print(dirPath + "\\" + file)
# Prints results if the "average" was run
if programToRun == "average":
    averageHeight = widthTotal / count
    averageWidth = heightTotal / count
    print("average height", averageHeight)
    print("average width", averageWidth)
