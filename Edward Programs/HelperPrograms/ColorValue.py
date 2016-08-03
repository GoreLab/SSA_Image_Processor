__author__ = 'Edward Buckler V'
# very simple program that when given the values found from the gray three square on the color correction card outputs
# the value that the image needs to be corrected to by chanel

# Asks user for chanel values
redIn = input("please input the red value: ")
greenIn = input("please input the green value")
blueIn = input("please input the blue value")
red = 120
green = 120
blue = 120
redOut = red - redIn
greenOut = green - greenIn
blueOut = blue - blueIn

print "red change val: ", redOut, "green change val: ", greenOut, "blue change val: ", blueOut
