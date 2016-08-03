__author__ = 'Edward Buckler V'
# Goal of this program was to take a very large image and cut it into quadrants so that easy pcc can deal with it more
# easily
import os
from PIL import Image
# Asks user for path to all images that need to be cropped down
dirPath = raw_input("please enter in the directory file path: ")
# cycles through each image in given path and crops 4 times (for each quadrant) and puts in a seperate folder
for file in os.listdir(dirPath):
    if not os.path.exists(dirPath+"\\CroppedImages"):
        os.makedirs(dirPath+"\\CroppedImages")
    if file.endswith(".tif") or file.endswith(".png") or file.endswith(".jpg"):
        print(file)
        print(dirPath+"\\"+file)
        with Image.open(dirPath+"\\"+file) as im:
            imageWidth, imageHeight = im.size
        image = Image.open(dirPath+"\\"+file)
        image.crop((imageWidth/2, 0, imageWidth, imageHeight/2)).save(dirPath+"\\CroppedImages\\1"+file)
        image.crop((0, 0, imageWidth/2, imageHeight/2)).save(dirPath+"\\CroppedImages\\2"+file)
        image.crop((0, imageHeight/2, imageWidth/2, imageHeight)).save(dirPath+"\\CroppedImages\\3"+file)
        image.crop((imageWidth/2, imageHeight/2, imageWidth, imageHeight)).save(dirPath+"\\CroppedImages\\4"+file)