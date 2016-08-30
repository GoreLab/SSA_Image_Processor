__author__ = 'Edward Buckler V'
# Goal of this program was to take a very large image and cut it into quadrants so that easy pcc can deal with it more
# easily
import os
from PIL import Image
import cv2
from MyFunctions import *
# Asks user for path to all images that need to be cropped down
dirPath = raw_input("please enter in the directory file path: ")
# cycles through each image in given path and crops 4 times (for each quadrant) and puts in a separate folder
imageSizes = []
for file in os.listdir(dirPath):
    # File creation
    if not os.path.exists(dirPath + "\\EasyPCCIm"):
        os.makedirs(dirPath + "\\EasyPCCIm")
    if not os.path.exists(dirPath + "\\Output"):
        os.makedirs(dirPath + "\\Output")
    if not os.path.exists(dirPath + "\\OutputPNG"):
        os.makedirs(dirPath + "\\OutputPNG")
    if not os.path.exists(dirPath + "\\CroppedImages"):
        os.makedirs(dirPath + "\\CroppedImages")
    # makes sure that the file being tested is in fact a acceptable image
    if file.endswith(".tfw"):
        shutil.copy2(dirPath + "\\" + file, dirPath + "\\Output\\" + file)
    if file.endswith(".tif") or file.endswith(".png") or file.endswith(".jpg"):
        # gets the image size
        print(file)
        with Image.open(dirPath + "\\" + file) as im:
            imageWidth, imageHeight = im.size
        # adds the image size to a list
        imageSizes.append((imageWidth, imageHeight))
        image = Image.open(dirPath + "\\" + file)
        # crops the image by quadrant
        image.crop((imageWidth / 2, 0, imageWidth, imageHeight / 2)).save(dirPath + "\\CroppedImages\\1" + file)
        image.crop((0, 0, imageWidth / 2, imageHeight / 2)).save(dirPath + "\\CroppedImages\\2" + file)
        image.crop((0, imageHeight / 2, imageWidth / 2, imageHeight)).save(dirPath + "\\CroppedImages\\3" + file)
        image.crop((imageWidth / 2, imageHeight / 2, imageWidth, imageHeight)).save(
            dirPath + "\\CroppedImages\\4" + file)


# waits for the user to do the Easy pcc step
holdHere = raw_input("type in anything when easy PCC is done processing the cropped images: ")
qEasyPCCImList = []
easyPCCImList = []
# creates a list of all images modified by Easy pcc
for file in os.listdir(dirPath + "\\EasyPCCIm"):
    if file.endswith(".tif") or file.endswith(".png") or file.endswith(".jpg"):
        qEasyPCCImList.append(file)

designatedImages = []
# makes a list with each element being the file name for each quadrant of the original images
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
# stitches all images back together and saves them as a tif
for file in easyPCCImList:
    with Image.open(dirPath + "\\EasyPCCIm\\" + file[1]) as im:
        imageWidth, imageHeight = im.size
    newIm = Image.new('RGB', (imageSizes[count]))
    count += 1
    imageQ1 = Image.open(dirPath + "\\EasyPCCIm\\" + file[0])
    imageQ2 = Image.open(dirPath + "\\EasyPCCIm\\" + file[1])
    imageQ3 = Image.open(dirPath + "\\EasyPCCIm\\" + file[2])
    imageQ4 = Image.open(dirPath + "\\EasyPCCIm\\" + file[3])
    newIm.paste(imageQ1, (imageWidth, 0))
    newIm.paste(imageQ2, (0, 0))
    newIm.paste(imageQ3, (0, imageHeight))
    newIm.paste(imageQ4, (imageWidth, imageHeight))
    # newIm = newIm.convert('1') #this has been taken out as it makes a checker board pattern
    savePathTIF = dirPath + "\\Output\\" + file[0][1:-4] + ".tif"
    savePathPNG = dirPath + "\\OutputPNG\\" + file[0][1:-4] + ".png"
    newIm.save(savePathPNG, "PNG")
    newImCV2 = cv2.imread(savePathPNG)
    newImCV2 = cv2.cvtColor(newImCV2, cv2.COLOR_BGR2GRAY)
    th, newImCV2 = cv2.threshold(newImCV2, 1, 255, cv2.THRESH_BINARY)
    newImCV2 = fill_holes(newImCV2)
    cv2.imwrite(savePathPNG, newImCV2)
    convertIm = Image.open(savePathPNG)
    convertIm.save(savePathTIF, "TIFF")