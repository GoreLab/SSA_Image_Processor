__author__ = 'Edward Buckler V'
# The goal of this program is to grab all the images from one folder that match the image names in another note that
# the output of the cart images will have to be renamed as it includes the date it was run on. Also all images must be 
# of .png file type
# in future I will try to work around this and make the program more versatile
import os
import shutil

# Asks user for botht the directory of the black images and the original images
dirPathOriginal = raw_input("input path of directory with images of seeds in it: ")
dirPathFind = raw_input("input path of directory with images of black in it: ")

# Finds and copies images in the original dir path that match the name of the images in the second folder
for file in os.listdir(dirPathFind):
    if file.endswith(".jpg") or file.endswith(".png"):
        if not os.path.exists(dirPathFind + "\\TestOriginal"):
            os.makedirs(dirPathFind + "\\TestOriginal")
        targetSeed = dirPathOriginal + "\\" + file[:14] + ".png"
        shutil.copy2(dirPathOriginal + "\\" + file[:14] + ".png", dirPathFind + "\\TestOriginal")
