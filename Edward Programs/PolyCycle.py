__author__ = 'Edward S Buckler V'
from osgeo import gdal, ogr
from gdalconst import *
import os

dirPath = raw_input("please enter in the path to the folder of tifs: ")
for file in os.listdir(dirPath):
    if file.endswith(".tif"):
        print("on file: " + file)
        filePath = dirPath + "\\" + file
        tif = gdal.open(filePath)
        band = tif.GetBandRaster(1)
        shpFile = file + "out.shp"
        shpDriver = ogr.GetDriverByName("ESRI Shapefile")
        outDataSource = shpDriver.CreateDataSource(shpFile)
        outLayer = outDataSource.CreateLayer(shpFile, geom_type=ogr.wkbLineString)
        gdal.Polygonize(band, None, outLayer, 1)
