__author__ = 'Edward Buckler V'
# Goal of this program was to take a very large image and cut it into quadrants so that easy pcc can deal with it more
# easily
import os
from PIL import Image
import cv2
from MyFunctions import *
# Asks user for path to all images that need to be cropped down
dirPath = "D:\work\TestTif"  # raw_input("please enter in the directory file path: ")
# cycles through each image in given path and crops 4 times (for each quadrant) and puts in a seperate folder
imageSizes = []
for file in os.listdir(dirPath):
    if not os.path.exists(dirPath + "\\CroppedImages"):
        os.makedirs(dirPath + "\\CroppedImages")
    if file.endswith(".tif") or file.endswith(".png") or file.endswith(".jpg"):
        with Image.open(dirPath + "\\" + file) as im:
            imageWidth, imageHeight = im.size
        imageSizes.append((imageWidth, imageHeight))
        image = Image.open(dirPath + "\\" + file)
        image.crop((imageWidth / 2, 0, imageWidth, imageHeight / 2)).save(dirPath + "\\CroppedImages\\1" + file)
        image.crop((0, 0, imageWidth / 2, imageHeight / 2)).save(dirPath + "\\CroppedImages\\2" + file)
        image.crop((0, imageHeight / 2, imageWidth / 2, imageHeight)).save(dirPath + "\\CroppedImages\\3" + file)
        image.crop((imageWidth / 2, imageHeight / 2, imageWidth, imageHeight)).save(
            dirPath + "\\CroppedImages\\4" + file)
        if not os.path.exists(dirPath + "\\EasyPCCIm"):
            os.makedirs(dirPath + "\\EasyPCCIm")
        if not os.path.exists(dirPath + "\\Output"):
            os.makedirs(dirPath + "\\Output")
qEasyPCCImList = []
easyPCCImList = []
for file in os.listdir(dirPath + "\\CroppedImages"):
    if file.endswith(".tif") or file.endswith(".png") or file.endswith(".jpg"):
        qEasyPCCImList.append(file)
designatedImages = []
for file in qEasyPCCImList:
    tempList = []
    for i, testing in enumerate(qEasyPCCImList):
        if i not in designatedImages:
            if testing[1:] == file[1:]:
                tempList.append(testing)
                designatedImages.append(i)
    if len(tempList) != 0:
        easyPCCImList.append(tempList)
count = 0
for file in easyPCCImList:
    with Image.open(dirPath + "\\CroppedImages\\" + file[1]) as im:
        imageWidth, imageHeight = im.size
    newIm = Image.new('RGB', (imageSizes[count]))
    count += 1
    imageQ1 = Image.open(dirPath + "\\CroppedImages\\" + file[0])
    imageQ2 = Image.open(dirPath + "\\CroppedImages\\" + file[1])
    imageQ3 = Image.open(dirPath + "\\CroppedImages\\" + file[2])
    imageQ4 = Image.open(dirPath + "\\CroppedImages\\" + file[3])

    newIm.paste(imageQ1, (imageWidth, 0))
    newIm.paste(imageQ2, (0, 0))
    newIm.paste(imageQ3, (0, imageHeight))
    newIm.paste(imageQ4, (imageWidth, imageHeight))
    savePath = dirPath + "\\Output\\" + file[0][1:]
    newIm.save(savePath, "TIFF")
