__author__ = 'Edward Buckler V'
# functions to make life easier used in many of my programs
import shutil
import os
import cv2
import numpy as np
from PIL import Image


# Turns a image into a binary image (black and white) if given the image and cut off for
# for white values
def thresh_binary(image, threshold, maxVal):
    imageCV2 = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    th, imageReturn = cv2.threshold(imageCV2, threshold, maxVal, cv2.THRESH_BINARY)
    return imageReturn


# Erodes binary images if given the image, size of blocks to use to erodes, and times to
# repeat
def erode(image, blockSize, iterationsNum):
    kernel = np.ones((blockSize, blockSize), np.uint8)
    imageReturn = cv2.erode(image, kernel, iterations=iterationsNum)
    return imageReturn


# Dilates binary images if given the image, size of blocks to use to dilate, and times to
# repeat
def dilate(image, blockSize, iterationsNum):
    kernel = np.ones((blockSize, blockSize), np.uint8)
    imageReturn = cv2.dilate(image, kernel, iterations=iterationsNum)
    return imageReturn


# Writes a given file to a certain path with a given file name and what is being saved and will return
# path if returnPath is true (1)
def write_file(path, fileName, saveFile, returnPath):
    cv2.imwrite(path + "\\" + fileName, saveFile)
    if returnPath == 1:
        return path + "\\" + fileName


# Crops images if given image, take from left side, take from top, take from right side,
# and take from bottom
def crop(imageFilePath, rmTop, rmRight, rmBottom, rmLeft, saveFilePath):
    with Image.open(imageFilePath) as im:
        imageWidth, imageHeight = im.size
    image = Image.open(imageFilePath)
    image.crop((rmLeft, rmTop, imageWidth - rmRight, imageHeight - rmBottom)).save(saveFilePath)


# Tests for pixels of certain color value by row if given image, target color, and number of rows
# to test from top
# note if image is black and white the rgb value is only one channel
def test_pixel_by_row(image, RGBvals, rowToTest, imagePath):
    with Image.open(imagePath) as im:
        imageWidth, imageHeight = im.size
    returnArray = []
    for yVal in range(0, rowToTest):
        for xVal in range(0, imageWidth - 1):
            if RGBvals == image[yVal, xVal]:
                returnArray.append([xVal, yVal])
    return returnArray


# Crops down a binary back plate image
def crop_to_plate(originalFilePath, imageBinary, imageBinaryPath, savepath):
    topWhitePixelsArray = test_pixel_by_row(imageBinary, 255, 1, imageBinaryPath)
    if len(topWhitePixelsArray) != 0:
        firstWhitePixel = topWhitePixelsArray[0][0]
        lastWhitePixel = topWhitePixelsArray[(len(topWhitePixelsArray) - 1)][0]
        with Image.open(imageBinaryPath) as im:
            imageWidth, imageHeight = im.size
        crop(originalFilePath, 0, (imageWidth - lastWhitePixel), 0, firstWhitePixel, savepath)


# Creates the file structure needed for Plate cleanup
def plate_cleanup_file_creation(DirPath):
    # Output folder
    if not os.path.exists(DirPath + "\\Output\\Side"):
        os.makedirs(DirPath + "\\Output\\Side")
    if not os.path.exists(DirPath + "\\Output\\Top"):
        os.makedirs(DirPath + "\\Output\\Top")
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


# Checks directory for file type and returns either 1 (present) or 0 (not found)
def scan_directory_for_file(dirPath, fileType):
    fileTypeFound = 0
    for file in os.listdir(dirPath):
        if file.endswith(fileType):
            fileTypeFound = 1
    return fileTypeFound


# fills holes in binary pictures
def fill_holes(imageBinary):
    imFloodfill = imageBinary.copy()
    h, w = imageBinary.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(imFloodfill, mask, (0, 0), 255)
    imFloodFillInv = cv2.bitwise_not(imFloodfill)
    returnImage = imageBinary | imFloodFillInv
    return returnImage


# puts a border around an image
def makeBorder(image, size):
    returnImage = cv2.copyMakeBorder(image, size, size, size, size, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    return returnImage


# Removes the need to use IrfanView for the side image
def alter_side(dirPath, saveDirPath):
    for file in os.listdir(dirPath):
        if file.endswith(".png") or file.endswith(".jpg"):
            image = Image.open(dirPath + "\\" + file)
            image.crop((850, 0, 1000, 990)).save(saveDirPath + file)
            image = Image.open(saveDirPath + file)
            image.rotate(90).save(saveDirPath + file)


# Removes the need to use IrfanView for the Top image
def alter_top_crop(dirPath, saveDirPath):
    for file in os.listdir(dirPath):
        if file.endswith(".png") or file.endswith(".jpg"):
            filePath = dirPath + "\\" + file
            image = Image.open(filePath)
            with Image.open(filePath) as im:
                imageWidth, imageHeight = im.size
            image.crop((200, 200, imageWidth, imageHeight)).save(saveDirPath + file)


# Removes need to do custom color correction on images
def alter_color_correction(dirPath, saveDirPath, blueOut, greenOut, redOut):
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


# converts numbers
def num_convert(num):
    try:
        return int(num)
    except ValueError:
        return float(num)
