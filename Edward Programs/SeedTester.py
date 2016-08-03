__author__ = 'Edward Buckler V'
# the goal of this program is to test if a seed image is empty by making it into a binary image then testing for
# white pixels by testing rows and columns spaced out by given values
from MyFunctions import *
import os, sys
import shutil

# Asks user for the the path of the images, space between rows/columns, and number of rows/columns allowed before
# flagging of image
dirPath = raw_input("input path of directory with images in it(file path): ")
spaceBetweenRows = input("what do you want the space between the rows to be?(integer): ")
numRowsExceptable = input("input number of rows with non-black pixels before possible error for HORIZONTAL(integer): ")
numColumnsExceptable = input(
    "input number of columns with non-black pixels before possible error for VERTICAL(integer): ")

# Cycles through all images in given directory
for file in os.listdir(dirPath):
    if file.endswith(".jpg") or file.endswith(".png"):
        # opens image with pillow
        with Image.open(dirPath + "\\" + file) as im:
            imageWidth, imageHeight = im.size
        # makes the image into black and white
        image = thresh_binary(dirPath + "\\" + file, 1, 255)
        whitefound = 0
        rowsToTest = [0]
        columnToTest = [0]
        # Creates a list of all rows/columns to test
        while (rowsToTest[-1] <= imageHeight - spaceBetweenRows):
            rowsToTest.append((rowsToTest[-1] + spaceBetweenRows))
        while (columnToTest[-1] <= imageWidth - spaceBetweenRows):
            columnToTest.append((columnToTest[-1] + spaceBetweenRows))
        # Tests rows
        rowsPositiveHorizontal = 0
        for row in rowsToTest:
            for xVal in range(0, imageWidth - 1):
                if 255 == image[row - 1, xVal]:
                    whitefound = 1
                    rowsPositiveHorizontal += 1
                    break
        columnsPositiveVertical = 0
        # Tests colums
        for column in columnToTest:
            for yVal in range(0, imageHeight - 1):
                if 255 == image[yVal, row - 1]:
                    whitefound = 1
                    columnsPositiveVertical += 1
                    break
        # Places all images that had to many rows/columns in a seperate image
        if rowsPositiveHorizontal > numRowsExceptable or columnsPositiveVertical > numColumnsExceptable:
            print("File taken out and put in possible errors: " + file)
            if not os.path.exists(dirPath + "\\PossibleError"):
                os.makedirs(dirPath + "\\PossibleError")
            shutil.move(dirPath + "\\" + file, dirPath + "\\PossibleError")
            print("the number of pos rows is:", rowsPositiveHorizontal)
            print("the number of pos columns is:", columnsPositiveVertical)
        # If an image has no white pixels it's placed in another folder
        if whitefound == 0:
            print(file)
            if not os.path.exists(dirPath + "\\BlackImages"):
                os.makedirs(dirPath + "\\BlackImages")
            shutil.move(dirPath + "\\" + file, dirPath + "\\BlackImages")
