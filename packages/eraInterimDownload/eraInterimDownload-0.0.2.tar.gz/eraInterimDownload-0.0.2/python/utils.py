#-*- coding: utf-8 -*-
'''
Created on 16 déc. 2013

@author: yoann Moreau

RMQ pas vraiment utile

All controls operations :
return true if control ok 
'''
import os
import errno
from datetime import date,datetime
import ogr,osr
import re
import gdal
import osr
import numpy as np
import subprocess
    
def checkForFile(pathToFile):
    if os.path.isfile(pathToFile):
        return True
    else:
        return False

def createParamFile(pathFile,user,key):
    
    f = open(pathFile, 'w+')
    f.write("{\n")
    f.write(' "url"   : "https://api.ecmwf.int/v1",\n')
    f.write('"key"   : "'+key+'",\n')
    f.write('"email" : "'+user+'"\n')
    f.write("}")
    f.close()
    

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def checkForFolder(pathToFolder):
    try:
        os.makedirs(pathToFolder)
    except OSError as exception:
        if exception.errno != errno.EEXIST:            
            exit('Path for downloaded Era Interim could not be create. Check your right on the parent folder...')
            
def checkForDate(dateC):
    #convert string to date from YYYY-MM-DD

    if len(dateC)==10:
        YYYY=dateC[0:4]
        MM=dateC[5:7]
        DD=dateC[8:10]
        if (YYYY.isdigit() and MM.isdigit()  and DD.isdigit()):
            try:
                date(int(YYYY),int(MM),int(DD))
            except ValueError:
                exit('Error on Date Format... please give a date in YYYY-MM-DD format')
            
            return date(int(YYYY),int(MM),int(DD))

        else:
            exit('Error on Date Format... please give a date in YYYY-MM-DD format')
    else: 
        exit('Error on Date Format... please give a date in YYYY-MM-DD format')

def convertShpToExtend(pathToShp):
    """
    reprojette en WGS84 et recupere l'extend
    """ 
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataset = driver.Open(pathToShp)
    if dataset is not None:
        # from Layer
        layer = dataset.GetLayer()
        spatialRef = layer.GetSpatialRef()
        # from Geometry
        feature = layer.GetNextFeature()
        geom = feature.GetGeometryRef()
        spatialRef = geom.GetSpatialReference()
        
        #WGS84
        outSpatialRef = osr.SpatialReference()
        outSpatialRef.ImportFromEPSG(4326)

        coordTrans = osr.CoordinateTransformation(spatialRef, outSpatialRef)

        env = geom.GetEnvelope()

        pointMAX = ogr.Geometry(ogr.wkbPoint)
        pointMAX.AddPoint(env[1], env[3])
        pointMAX.Transform(coordTrans)
        
        pointMIN = ogr.Geometry(ogr.wkbPoint)
        pointMIN.AddPoint(env[0], env[2])
        pointMIN.Transform(coordTrans)


        return [pointMAX.GetPoint()[1],pointMIN.GetPoint()[0],pointMIN.GetPoint()[1],pointMAX.GetPoint()[0]]
    else:
        exit(" shapefile not found. Please verify your path to the shapefile")


def is_float_re(element):
    _float_regexp = re.compile(r"^[-+]?(?:\b[0-9]+(?:\.[0-9]*)?|\.[0-9]+\b)(?:[eE][-+]?[0-9]+\b)?$").match
    return True if _float_regexp(element) else False


def checkForExtendValidity(extendList):
    
    if len(extendList)==4 and all([is_float_re(str(x)) for x in extendList]) and extendList[0]>extendList[2] and extendList[1]<extendList[3]:
        if float(extendList[0]) > -180 and float(extendList[2]) <180 and float(extendList[1]) <90 and  float(extendList[3]) > -90:
            extendArea=[str(x) for x in extendList]
            return extendArea
        else:
            exit('Projection given is not in WGS84. Please verify your -t parameter')
    else:
        exit('Area scpecified is not conform to a  ymax xmin ymin xmax  extend. please verify your declaration')

def checkForTimeValidity(listTime):
    
    validParameters=('00','06','12','18')
    
    if len(listTime)>0 and isinstance(listTime, list) and all([x in validParameters for x in listTime]):
        return listTime
    else: 
        exit('time parameters not conform to eraInterim posibility : '+ ",".join(validParameters))

def checkForStepValidity(listStep):
    
    validParameters=(0,3,6,9,12)
    
    if len(listStep)>0 and isinstance(listStep, list) and all([int(x) in validParameters for x in listStep]):
        listStep=[int(x) for x in listStep]
        return listStep
    else: 
        exit('step parameters not conform to eraInterim posibility : '+ ",".join([str(x) for x in validParameters]))

def checkForGridValidity(grid):
    
    if (is_float_re(grid)):
        grid=float(grid)
        validParameters=(0.125,0.25,0.5,0.75,1.125,1.5,2,2.5,3)
        
        if grid in validParameters:
            return grid
        else:
            exit('grid parameters not conform to eraInterim posibility : '+ ",".join([str(x) for x in validParameters]))
    else:
        exit('grid parameters not conform to eraInterim posibility : '+ ",".join([str(x) for x in validParameters]))
    

def create_request_sfc(dateStart,dateEnd, timeList,stepList,grid,extent,paramList,output):
    """
        Genere la structure de requete sur les serveurs de l'ECMWF
        
        INPUTS:\n
        -date : au format annee-mois-jour\n
        -heure : au format heure:minute:seconde\n
        -coord : une liste des coordonnees au format [N,W,S,E]\n
        -dim_grille : taille de la grille en degre \n
        -output : nom & chemin du fichier resultat
    """
    
    struct = {
    'dataset' : "interim",
    'date'    : dateStart.strftime("%Y-%m-%d")+"/to/"+dateEnd.strftime("%Y-%m-%d"),
    'time'    : "/".join(map(str, timeList)),
    'stream'  : "oper",
    'step'    : "/".join(map(str, stepList)),
    'levtype' : "sfc",
    'type'    : "fc",
    'class'   : "ei",
    'param'   : ".128/".join(map(str, paramList))+'.128',
    'area'    : "/".join(extent),
    'grid'    : str(grid)+"/"+str(grid),
    'target'  : output,
    'format'  : 'netcdf'
    }
    
    return struct

def reprojRaster(pathToImg,output,pathToShape):
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(pathToShape, 0)
    layer = dataSource.GetLayer()
    srs = layer.GetSpatialRef()
    print ["gdalwarp","-q","-s_srs","EPSG:4326","-t_srs",srs.ExportToWkt(),pathToImg,output,'-overwrite','-dstnodata',"0"]
    subprocess.call(["gdalwarp","-q","-s_srs","EPSG:4326","-t_srs",srs.ExportToWkt(),pathToImg,output,'-overwrite','-dstnodata',"0"])
    return output

def convertNETCDFtoTIF(inputFile,outputFile,format='float'):
    #--convert netCDF to tif
    
    ds_in=gdal.Open('NETCDF:"'+inputFile+'"')
    metadata = ds_in.GetMetadata()

    scale=metadata['tp#scale_factor']
    offset=metadata['tp#add_offset']
    nodata=metadata['tp#_FillValue']

    cols = ds_in.RasterXSize
    rows = ds_in.RasterYSize
    geotransform = ds_in.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    nbBand= ds_in.RasterCount
    
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(outputFile, cols, rows, nbBand, gdal.GDT_Float32)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))

    
    for b in range(1,nbBand+1):
        band = ds_in.GetRasterBand(b)
        
        arrayB = np.array(band.ReadAsArray(), dtype=format)
        np.putmask(arrayB,(arrayB==float(nodata)),0)
        #arrayB=numpy.multiply(arrayB, scale)+float(offset)
        trans_arrayB=arrayB*float(scale)+float(offset)
        np.putmask(trans_arrayB,(arrayB==float(nodata)+1),0)
        outband = outRaster.GetRasterBand(b)

        outband.WriteArray(trans_arrayB)
    
    outband.FlushCache()


