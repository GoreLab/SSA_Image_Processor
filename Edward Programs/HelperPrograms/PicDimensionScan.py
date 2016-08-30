__author__ = 'Edward Buckler V'
# Program made in response to many of the images from ImageCleaner not being cropped correctly. Has two functions
# getting the average dimensions of images in a directory and placing all images over a set value pixels
import cv2
import os, sys
import shutil
# Asks user for the directory containing the images and what process should be run
dirPath = raw_input("input path of directory with images in it: ")
programToRun = raw_input("Which program to run average (average) or flag (find ones which are too large)?: ")

if programToRun == "flag":
    maxWidth = input("please enter in the value at which images will be flagged (550 advised)(integer): ")
widthTotal = 0
heightTotal = 0
count = 0
if programToRun != "flag" and programToRun != "average":
    sys.exit("please put in average or flag (case counts!) for what program to run!")
else:
    count = 0
    for file in os.listdir(dirPath):
        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg") or file.endswith(".tif") and programToRun == "average":
            print(file)
            image = cv2.imread(dirPath + "\\" + file)
            X = (len(image))
            Y = (len(image[0,]))
            widthTotal += X
            heightTotal += Y

            count += 1
        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".tif") and programToRun == "flag":
            image = cv2.imread(dirPath + "\\" + file)
            X = (len(image))
            Y = (len(image[0,]))
            if Y >= 550:
                if not os.path.exists(dirPath + "\\FlaggedImages"):
                    os.makedirs(dirPath + "\\FlaggedImages")
                shutil.move(dirPath + "\\" + file, dirPath + "\\FlaggedImages")
                print(dirPath + "\\" + file)
                count += 1
if programToRun == "average":
    averageHeight = widthTotal / count
    averageWidth = heightTotal / count
    print("average height", averageHeight)
    print("average width", averageWidth)
