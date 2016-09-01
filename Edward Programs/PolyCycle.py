__author__ = 'Edward S Buckler V'
# The goal of this program is to automate the process of making polygons around corn plants that have been preprocessed
# by the CropDownCorn program. Using the the OSGeo4W shell is advisable to run this program
import os

from osgeo import gdal, ogr
# Asks user for path to TIFs
dirPath = raw_input("please enter in the path to the folder of tifs: ")
# Cycles through all TIFs in given path
for file in os.listdir(dirPath):
    if file.endswith(".tif"):
        print("on file: " + file)
        filePath = dirPath + "\\" + file
        tif = gdal.Open(filePath)
        band = tif.GetRasterBand(1)
        shpFile = filePath[:-4] + ".shp"
        shpDriver = ogr.GetDriverByName("ESRI Shapefile")
        outDataSource = shpDriver.CreateDataSource(shpFile)
        outLayer = outDataSource.CreateLayer(shpFile, geom_type=ogr.wkbLineString)
        gdal.Polygonize(band, None, outLayer, 1, [], callback=None)
