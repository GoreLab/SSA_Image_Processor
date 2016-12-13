""" preproclib.py - Library of functions for pre-processing scripts.

Library of functions used by sapreproc.py and several other
scripts written by Edward Buckler. Developed and tested with Python
2.7.x and OpenCV 2.4.x.

Originally written by Edward Buckler.
"""

__author__ = 'Edward Buckler V'

import shutil
import os
import cv2
import numpy as np
from PIL import Image

def thresh_binary(image, threshold, maxVal):
	"""Turns a image into a binary image (black and white) if given
	the image and cut off for white values.
	"""
    imageCV2 = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    th, imageReturn = cv2.threshold(imageCV2, threshold, maxVal, cv2.THRESH_BINARY)
    return imageReturn

def erode(image, blockSize, iterationsNum):
	""" Erodes binary images if given the image, size of blocks to use
	to erodes, and times to repeat.
	"""
    kernel = np.ones((blockSize, blockSize), np.uint8)
    imageReturn = cv2.erode(image, kernel, iterations=iterationsNum)
    return imageReturn

def dilate(image, blockSize, iterationsNum):
	""" Dilates binary images if given the image, size of blocks to
	use to dilate, and times to repeat.
	"""
    kernel = np.ones((blockSize, blockSize), np.uint8)
    imageReturn = cv2.dilate(image, kernel, iterations=iterationsNum)
    return imageReturn

def write_file(path, fileName, saveFile, returnPath):
	""" Writes a given file to a certain path with a given file name
	and what is being saved and will return path if returnPath is
	true (1).
	"""
    cv2.imwrite(path + "\\" + fileName, saveFile)
    if returnPath == 1:
        return path + "\\" + fileName # Seriously?

def crop(imageFilePath, rmTop, rmRight, rmBottom, rmLeft, saveFilePath):
	""" Crops images if given image, take from left side, take from
	top, take from right side, and take from bottom.
    """
    with Image.open(imageFilePath) as im:
        imageWidth, imageHeight = im.size
    image = Image.open(imageFilePath)
    image.crop((rmLeft, rmTop, imageWidth - rmRight, imageHeight - rmBottom)).save(saveFilePath)

def test_pixel_by_row(image, RGBvals, rowToTest, imagePath):
	""" Tests for pixels of certain color value by row if given image,
	target color, and number of rows to test from top note if image is
	black and white the rgb value is only one channel.
	"""
    with Image.open(imagePath) as im:
        imageWidth, imageHeight = im.size
    returnArray = []
    for yVal in range(0, rowToTest):
        for xVal in range(0, imageWidth - 1):
            if RGBvals == image[yVal, xVal]:
                returnArray.append(xVal)
    return returnArray

def crop_to_plate(originalFilePath, imageBinary, imageBinaryPath, savepath):
	""" Crops down a binary back plate image.
	"""
    topWhitePixelsArray = test_pixel_by_row(imageBinary, 255, 10, imageBinaryPath)
    if len(topWhitePixelsArray) != 0:
        firstWhitePixel = min(topWhitePixelsArray)
        lastWhitePixel = max(topWhitePixelsArray)
        with Image.open(imageBinaryPath) as im:
            imageWidth, imageHeight = im.size
        crop(originalFilePath, 0, (imageWidth - lastWhitePixel), 0, firstWhitePixel, savepath)
    else:
        with Image.open(imageBinaryPath) as im:
            imageWidth, imageHeight = im.size
        crop(originalFilePath, 0,0, 0, 0, savepath)        

def plate_cleanup_file_creation(DirPath):
	""" Creates the file structure needed for Plate cleanup.
	"""
    # Output folder
    if not os.path.exists(DirPath + "\\Output"):
        os.makedirs(DirPath + "\\Output")
    # SeedImages folder:
    if not os.path.exists(DirPath + "\\SeedImages\\Side"):
        os.makedirs(DirPath + "\\SeedImages\\Side")
    if not os.path.exists(DirPath + "\\SeedImages\\Top"):
        os.makedirs(DirPath + "\\SeedImages\\Top")
    # Edited Folder:
    if not os.path.exists(DirPath + "\\Edited"):
        os.makedirs(DirPath + "\\Edited")
    if not os.path.exists(DirPath + "\\Edited\\Side"):
        os.makedirs(DirPath + "\\Edited\\Side")
    if not os.path.exists(DirPath + "\\Edited\\Top"):
        os.makedirs(DirPath + "\\Edited\\Top")
    # Plate folder:
    if not os.path.exists(DirPath + "\\Plate"):
        os.makedirs(DirPath + "\\Plate")
    if not os.path.exists(DirPath + "\\Plate\\BlackAndWhiteCleaned"):
        os.makedirs(DirPath + "\\Plate\\BlackAndWhiteCleaned")
    if not os.path.exists(DirPath + "\\Plate\\CroppedImages"):
        os.makedirs(DirPath + "\\Plate\\CroppedImages")
    for file in os.listdir(DirPath):
        imageFilePath = DirPath + "\\" + file
        if file.startswith("Side"):
            shutil.move(imageFilePath, DirPath + "\\SeedImages\\Side")
        if file.startswith("Top"):
            shutil.move(imageFilePath, DirPath + "\\SeedImages\\Top")

def scan_directory_for_file(dirPath, fileType):
	""" Checks directory for file type and returns either 1 (present)
	or 0 (not found).
	"""
    fileTypeFound = 0
    for file in os.listdir(dirPath):
        if file.endswith(fileType):
            fileTypeFound = 1
    return fileTypeFound

def fill_holes(imageBinary):
	""" fills holes in binary pictures.
	"""
    imFloodfill = imageBinary.copy()
    h, w = imageBinary.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(imFloodfill, mask, (0, 0), 255)
    imFloodFillInv = cv2.bitwise_not(imFloodfill)
    returnImage = imageBinary | imFloodFillInv
    return returnImage

def makeBorder(image, size):
	""" Puts a border around an image.
	"""
    returnImage = cv2.copyMakeBorder(image, size, size, size, size, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    return returnImage

def alter_side(dirPath, saveDirPath):
	""" Removes the need to use IrfanView for the side image.
	"""
    for file in os.listdir(dirPath):
        if file.endswith(".png") or file.endswith(".jpg"):
            image = Image.open(dirPath + "\\" + file)
            image_cropped = image.crop((850, 0, 1000, 990))
            image_rotated = image_cropped.rotate(90,expand=True)
            image_rotated.save(saveDirPath + file)

def alter_top_crop(dirPath, saveDirPath):
	""" Removes the need to use IrfanView for the Top image.
	"""
    for file in os.listdir(dirPath):
        if file.endswith(".png") or file.endswith(".jpg"):
            filePath = dirPath + "\\" + file
            image = Image.open(filePath)
            with Image.open(filePath) as im:
                imageWidth, imageHeight = im.size
            # !!!! If the crop below is changed, the crop in samain.py
            #    that is passed to calcSideScaleFactor
            #    (a salib.py function) also needs to be changed!
            image.crop((300,300, imageWidth, imageHeight)).save(saveDirPath + file)

def alter_color_correction(dirPath, saveDirPath, blueOut, greenOut, redOut):
	""" Removes need to do custom color correction on images.
	"""
    for file in os.listdir(dirPath):
        if file.endswith(".png") or file.endswith(".jpg"):
            with Image.open(dirPath + file) as im:
                imageWidth, imageHeight = im.size
            cv2im = cv2.imread(dirPath + file)
            for xVal in range(0, imageWidth):
                for yVal in range(0, imageHeight):
                    # red correction
                    if redOut < 0:
                        if (cv2im.item(yVal, xVal, 2) + redOut) < 0:
                            cv2im.itemset((yVal, xVal, 2), 0)
                        else:
                            cv2im.itemset((yVal, xVal, 2), (cv2im.item(yVal, xVal, 2) + redOut))
                    else:
                        if cv2im.item(yVal, xVal, 2) < 255 - redOut:
                            cv2im.itemset((yVal, xVal, 2), (cv2im.item(yVal, xVal, 2) + redOut))
                        elif cv2im.item(yVal, xVal, 2) >= 255 - redOut:
                            cv2im.itemset((yVal, xVal, 2), 255)
                    # green correction
                    if greenOut < 0:
                        if (cv2im.item(yVal, xVal, 1) + greenOut) < 0:
                            cv2im.itemset((yVal, xVal, 1), 0)
                        else:
                            cv2im.itemset((yVal, xVal, 1), (cv2im.item(yVal, xVal, 1) + greenOut))
                    else:
                        if cv2im.item(yVal, xVal, 1) < 255 - greenOut:
                            cv2im.itemset((yVal, xVal, 1), (cv2im.item(yVal, xVal, 1) + greenOut))
                        elif cv2im.item(yVal, xVal, 1) >= 255 - greenOut:
                            cv2im.itemset((yVal, xVal, 1), 255)
                    # blue correction
                    if blueOut < 0:
                        if (cv2im.item(yVal, xVal, 0) + blueOut) < 0:
                            cv2im.itemset((yVal, xVal, 0), 0)
                        else:
                            cv2im.itemset((yVal, xVal, 0), (cv2im.item(yVal, xVal, 0) + blueOut))
                    else:
                        if cv2im.item(yVal, xVal, 0) < 255 - blueOut:
                            cv2im.itemset((yVal, xVal, 0), (cv2im.item(yVal, xVal, 0) + blueOut))
                        elif cv2im.item(yVal, xVal, 0) >= 255 - blueOut:
                            cv2im.itemset((yVal, xVal, 0), 255)
            cv2.imwrite(saveDirPath + file, cv2im)

def num_convert(num):
	""" Converts numbers.
	"""
    try:
        return int(num)
    except ValueError:
        return float(num)
