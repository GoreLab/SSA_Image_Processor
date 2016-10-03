__author__ = 'Edward Buckler V'
# The goal of this program is to take side and top images and crop them down so that the CART algorithm
# can actually find the seed rather then picking up all the noise/inclusions. Also it helps in speeding up the
# whole process
# because the color correction takes so long on this it is advised that you use something like IrfanView to do that step
# it is still of course still possible to do that through this program it just may add quite a lot of time
# cropping on the other hand is quite fast so using this program to do that is still reasonably fast
from MyFunctions import *

# Asking user what needs to be done in terms of set up note inputs are not required to be capital 
DirPath = raw_input("What is the directory path(Directory with all images)?")
filesMade = raw_input("Has the correct file structure been made?(Y/N): ")
correctionCropDone = raw_input("Have all images already been edited and only the auto crop needs to run?(Y/N):")
if correctionCropDone == "n" or correctionCropDone == "N":
    imagesAltered = raw_input("are the images cropped and corrected?(Y/N): ")
    # Creating file structure is specified that it hasn't been done already
    if filesMade == "n" or filesMade == "N":
        plate_cleanup_file_creation(DirPath)
    # Does color correction to images by asking the user for the chanel values found from the color correction card and then
    # after discerning what the correction value should be uses the function to run the correction
    if imagesAltered == "n" or imagesAltered == "N":
        ColorCorrectionDone = raw_input("was color correction done on the top and side images? (Y/N)")
        if ColorCorrectionDone == "n" or ColorCorrectionDone == "N":
            redIn = input("please input the red value from the 'gray 3 square': ")
            red = 120
            redOut = red - redIn
            print("change in red will be: " + str(redOut))
            greenIn = input("please input the green value from the 'gray 3 square': ")
            green = 120
            greenOut = green - greenIn
            print("change in green will be: " + str(greenOut))
            blueIn = input("please input the blue value from the 'gray 3 square': ")
            blue = 120
            blueOut = blue - blueIn
            print("change in blue will be: " + str(blueOut))
            # Runs color correction on both side and top images this is dependant heavily on images being in the right
            # files if images are out of place this will cause problems
            alter_color_correction((DirPath + "\\SeedImages\\Top\\"), (DirPath + "\\Edited\\Top\\"), blueOut, greenOut,
                                   redOut)
            alter_color_correction((DirPath + "\\SeedImages\\Side\\"), (DirPath + "\\Edited\\Side\\"), redOut, greenOut,
                                   blueOut)
            # Runs the cropping of all images this is done so that processing time during use of the CART algorithms doesn't
            # take as long
            print("working...")
            alter_side((DirPath + "\\Edited\\Side\\"), (DirPath + "\\Edited\\Side\\"))
            alter_top_crop((DirPath + "\\Edited\\Top\\"), (DirPath + "\\Edited\\Top\\"))
        else:
        	print("working...")
        	alter_side((DirPath + "\\SeedImages\\Side\\"), (DirPath + "\\Edited\\Side\\"))
        	alter_top_crop((DirPath + "\\SeedImages\\Top\\"), (DirPath + "\\Edited\\Top\\"))
# Creation of variables used in the auto cropping of the side images
CARTDirPath = DirPath + "\\Plate"
originalDirPathSide = DirPath + "\\Edited\Side"
newPathBW = CARTDirPath + "\BlackAndWhiteCleaned"
newPathCropped = CARTDirPath + "\CroppedImages"
# Making the user run the "Plate" CART algorithm on the edited side images
plateCARTMade = "notDone"
while plateCARTMade != "Y" or plateCARTMade != "y":
    plateCARTMade = raw_input(
        "please type in 'Y' when you have completed running the plate CART algorithm on the images in edited/side and placed the output in the plate folder")
    if plateCARTMade == "Y" or plateCARTMade == "y":
    	break
# Auto Cropping of side images note that it skips over the 0 image as that was simply a starting image and never
# has a seed in it
for file in os.listdir(CARTDirPath):
    if file.endswith(".jpg") and file.find("SideImage000.") == -1:
        imageFilePath = CARTDirPath + "\\" + file
        imageBinary = thresh_binary(imageFilePath, 1, 255)
        imageBinaryBorder = makeBorder(imageBinary, 5)
        imageBinaryFilled = fill_holes(imageBinaryBorder)
        imageErode = erode(imageBinaryFilled, 5, 6)
        imageDilate = dilate(imageErode, 5, 6)
        imageDilate = imageDilate[5:155, 5:995]
        imageBinaryPath = write_file(newPathBW, file, imageDilate, 1)
        originalFileName = file[:(len(file) - 16)]
        print(originalFileName)
        originalFileName += ".jpg"
        originalFilePath = originalDirPathSide + "\\" + originalFileName
        croppedImage = crop_to_plate(originalFilePath, imageDilate, imageBinaryPath,
                                     newPathCropped + "\\" + originalFileName)
print("now run the side and top CART algorithms to get the output")
exit()