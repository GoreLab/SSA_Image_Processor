__author__ = 'Edward Buckler V'
# Find copies is the response to the possibility that there may be images of the same seed from the same day which was
# thought to be a the reason for the extra seed images on both may 15th and may 17th.
from MyFunctions import *

# Asks user for the path to the txt file that matches the SSA data spreadsheet
# Asks user for the path to all images from the day in question
userInput = raw_input("please enter text file path: ")
dirPath = raw_input("please enter the folder with the images: ")

# Creates a list of all lines in the test document
with open(userInput) as userInputList:
    nList = []
    for line in userInputList:
        nList.append(line)

# Splits the previous list up by whenever a tab is seen
twoDimUserIn = []
for element in nList:
    twoDimUserIn.append(element.split("\t"))

# takes the two dimensional array from previous and creates a one dimensional array
oneDimUserIn = []
for element in twoDimUserIn:
    for things in element:
        oneDimUserIn.append(things)

# Makes lists with all the elements containing .txt for the get the image path, 0.0 to get the weight (no weight
# is above .09), and * to get the position of the seed
textFiles = []
weightsList = []
posList = []
for element in oneDimUserIn:
    if element.endswith(".txt"):
        textFiles.append(element)
    if element.startswith("0.0") or element == "Error":
        weightsList.append(element)
    if element.find("*") != -1:
        posList.append(element)

# factors in tolerance by editing the weight list and rounding them to the accepted tolerance of the scale.
for index, element in enumerate(weightsList):
    if element != "Error":
        element = num_convert(element)
        modNum = element % 0.001
        if modNum == 0:
            continue
        else:
            if (element + modNum) % .001 == 0:
                weightsList[index] = (element + modNum)
            else:
                weightsList[index] = (element - modNum)

# Turns the weightsList list back into a list of string to be manipulated later
for index, element in enumerate(weightsList):
    element = str(element)
    weightsList[index] = element

# Makes a list of all unique elements in weightsList
individualElementList = []
for element in weightsList:
    if element not in individualElementList:
        individualElementList.append(element)

# makes a list of all weights in weightsList along with all indexes associated with them
weightIndexList = []
for element in individualElementList:
    weightIndexList.append([element, [i for i, x in enumerate(weightsList) if x == element]])

# Places all images in a file structure with the rounded weights of the seeds as the name of the folder (with
#  no decimal)
checkWeights = []
checkDir = []
checkFile = []
# File that all images that may have an error are places
if not os.path.exists(dirPath + "\\PossibleError"):
    os.makedirs(dirPath + "\\PossibleError")
for element in weightIndexList:
    weight = element[0]
    current = element[1]
    if len(current) > 1:
        if weight != "Error":
            a, tempWeight = weight.split(".")
        # creation of files for manual checking. One for files that may be of the same seed, one for files with
        # possible copies, and one for files without copied seed images
        if not os.path.exists(dirPath + "\\PossibleError\\Unknown"):
            os.makedirs(dirPath + "\\PossibleError\\Unknown")
        if not os.path.exists(dirPath + "\\PossibleError\\Possible"):
            os.makedirs(dirPath + "\\PossibleError\\Possible")
        if not os.path.exists(dirPath + "\\PossibleError\\NotSame"):
            os.makedirs(dirPath + "\\PossibleError\\NotSame")
        # makes a list of all individual positions recorded for each seed of the same weight
        tempList = []
        for i in range(0, len(current)):
            if posList[current[i]] not in tempList:
                tempList.append(posList[current[i]])
        # If there are less than two starting postions (meaning a seed of the same weight came from the same position
        # meaning a good chance of it being a copy) then the image is copied into a new folder
        if len(tempList) < 2:
            for i in range(0, len(current)):
                if not os.path.exists(dirPath + "\\PossibleError\\" + tempWeight):
                    os.makedirs(dirPath + "\\PossibleError\\" + tempWeight)
                a, b, tempDirName, temp = (textFiles[current[i]]).split("\\")
                a, imNumtxt = temp.split("-")
                imNum, a = imNumtxt.split(".")
                imName = "TopImage-" + imNum + ".png"
                originNum = tempDirName[5:]
                shutil.copy2((dirPath + "\\" + tempDirName + "\\" + imName),
                             (dirPath + "\\PossibleError\\" + tempWeight + "\\" + originNum + imName))
