__author__ = 'Edward Buckler V'
# The goal of this program was to test if a seed is touching the side of the image by creating a black and white
# image then testing for white pixels at the left and right sides
from MyFunctions import *
import os, sys
import shutil

# Asks user to input the directory path with all images
dirPath = raw_input("input path of directory with images in it: ")
for file in os.listdir(dirPath):
    if file.endswith(".jpg") or file.endswith(".png"):
        # Opens image in pillow
        with Image.open(dirPath + "\\" + file) as im:
            imageWidth, imageHeight = im.size
        # Makes image into a binary
        image = thresh_binary(dirPath + "\\" + file, 1, 255)
        whitefound = 0
        # Tests both side of iamge
        for yVal in range(0, imageHeight - 1):
            if 255 == image[0, yVal]:
                whitefound = 1
                break
        for yVal in range(0, imageHeight - 1):
            if 255 == image[yVal, imageWidth - 1]:
                whitefound = 1
                break
        # if white was found to be touching the sides then it it placed in a folder
        if whitefound == 1:
            print(file)
            if not os.path.exists(dirPath + "\\TouchingSides"):
                os.makedirs(dirPath + "\\TouchingSides")
            shutil.move(dirPath + "\\" + file, dirPath + "\\TouchingSides")
