#-*- coding: utf-8 -*-
'''
Created on 16 déc. 2013

@author: yoann Moreau

All controls operations :
return true if control ok 
'''
import os
import errno
from datetime import date,datetime,timedelta
import ogr,osr
import re
import gdal
import osr
import numpy as np
import numpy.ma as ma
import subprocess
import shutil
import math
from pyspatialite._spatialite import Row
import scipy.ndimage as ndimage
    
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

def checkForStepValidity(listStep,typeData):
    
    validParameters=(0,3,6,9,12)
    if typeData=="forcast":
        if len(listStep)>0 and isinstance(listStep, list) and all([int(x) in validParameters for x in listStep]):
            listStep=[int(x) for x in listStep]
            return listStep
        else: 
            exit('step parameters not conform to eraInterim posibility : '+ ",".join([str(x) for x in validParameters]))
    else:
        if len(listStep)>0:
            exit('step parameters not conform to eraInterim posibility : '+ ",".join([str(x) for x in validParameters])+ 'for analyse')
        else:
            return listStep

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
    

def create_request_sfc(dateStart,dateEnd, timeList,stepList,grid,extent,paramList,output,typeData=None):
    """
        Genere la structure de requete sur les serveurs de l'ECMWF
        
        INPUTS:\n
        -date : au format annee-mois-jour\n
        -heure : au format heure:minute:seconde\n
        -coord : une liste des coordonnees au format [N,W,S,E]\n
        -dim_grille : taille de la grille en degre \n
        -output : nom & chemin du fichier resultat
    """
    
    if typeData=='analyse':
        typeD='an'
    else:
        typeD='fc'
    
    struct = {
    'dataset' : "interim",
    'date'    : dateStart.strftime("%Y-%m-%d")+"/to/"+dateEnd.strftime("%Y-%m-%d"),
    'time'    : "/".join(map(str, timeList)),
    'stream'  : "oper",
    'step'    : "/".join(map(str, stepList)),
    'levtype' : "sfc", #pl -> pressure level ,sfc -> surface
    'type'    : typeD, #fc -> forcast , an -> analyse
    'class'   : "ei",
    'param'   : ".128/".join(map(str, paramList))+'.128',
    'area'    : "/".join(extent),
    'grid'    : str(grid)+"/"+str(grid),
    'target'  : output,
    'format'  : 'netcdf'
    }
    
    return struct

def moveFile(inputImg,outputImg):
        "move a file to a directory"
        
        #TODO controls to check if exist
        #on déplace le fichier dans le bon répertoire
        shutil.move(inputImg, outputImg)

def reprojRaster(pathToImg,output,shape,pathToShape):
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(pathToShape, 0)
    layer = dataSource.GetLayer()
    srs = layer.GetSpatialRef()
    
    Xres=shape[1]
    Yres=shape[0]
    
    subprocess.call(["gdalwarp","-q","-s_srs","EPSG:4326","-t_srs",srs.ExportToWkt(),pathToImg,output,'-ts',str(Xres),str(Yres),'-overwrite','-dstnodata',"0"])
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

def  convertNETCDFtoDicArray(inputFile,format='float'):
    #--convert netCDF to numpy dico Array
    
    ds_in=gdal.Open('NETCDF:"'+inputFile+'"')
    metadata = ds_in.GetMetadata()
    for i in metadata.keys():
        if i.find('scale_factor')>0:
            scale=metadata[i]
        elif i.find('add_offset')>0:
            offset=metadata[i]
        elif i.find('_FillValue')>0:
            nodata=metadata[i]

    nbBand= ds_in.RasterCount
    dicoAray={}
    
    for b in range(1,nbBand+1):
        band = ds_in.GetRasterBand(b)
        
        arrayB = np.array(band.ReadAsArray(), dtype=format)
        np.putmask(arrayB,(arrayB==float(nodata)),0)
        #arrayB=numpy.multiply(arrayB, scale)+float(offset)
        trans_arrayB=arrayB*float(scale)+float(offset)
        np.putmask(trans_arrayB,(arrayB==float(nodata)+1),0)
        dicoAray[b]=trans_arrayB

    return dicoAray

def convertKToD(dicoT):
    
    Degree={}
    
    for i in dicoT:
        mask=np.logical_not(dicoT[i] > 0).astype(int)
        DegreeArray=dicoT[i]-273.15
        np.putmask(DegreeArray,mask,np.nan)
        Degree[i]=DegreeArray
    return Degree

def convertToHectoPascal(dicoP):
    
    pressure= {}
    
    for i in dicoP:
        mask=np.logical_not(dicoP[i] > 0).astype(int)
        PArray=dicoP[i]/100
        np.putmask(PArray,mask,np.nan)
        pressure[i]=PArray
    return pressure

def convertPaToKgPa(dicoP):
    
    pressure= {}
    
    for i in dicoP:
        mask=np.logical_not(dicoP[i] > 0).astype(int)
        PArray=dicoP[i]/1000
        np.putmask(PArray,mask,np.nan)
        pressure[i]=PArray
    return pressure

def convertWToMJ(dicoRay):

    rayonnement={}
    for i in dicoRay:
        mask=np.logical_not(dicoRay[i] > 0).astype(int)
        RArray=(dicoRay[i]/(10**6))
        np.putmask(RArray,mask,np.nan)
        rayonnement[i]=RArray
        
    return rayonnement

def convertGeoToAlt(dicoGeo):
    
    def mean(values):
        return np.nanmean(values)
    
    Altitude={}
    cstGravit=9.80665 
    footprint = np.array([[0,1,0],
                          [1,0,1],
                          [0,1,0]])

    for i in dicoGeo:
        mask=np.logical_not(dicoGeo[i] > 0).astype(int)
        GeoArray=np.divide(dicoGeo[i],cstGravit)
        np.putmask(GeoArray,mask,np.nan)
        indices = np.where(np.isnan(GeoArray))
        results = ndimage.generic_filter(GeoArray, mean, footprint=footprint)
        for row, col in zip(*indices):
            GeoArray[row,col] = results[row,col]
        Altitude[i]=GeoArray
        
    return Altitude


def computeDailyAccumulation(dicoBand,nbBandByDay,typeData):
    
    accumulation={}
    for i in range(0,len(dicoBand.keys())/nbBandByDay):
        if (typeData == "analyse"):
            maxRange=nbBandByDay+i*nbBandByDay
        else:
            maxRange=nbBandByDay+i*nbBandByDay-1
            
        #on ne prend pas la dernière bande... correspondante à 00-->3h
        for j in range (i*nbBandByDay,maxRange):
            if "array" in locals():
                array=array+dicoBand.items()[j][1]
            else:
                array=dicoBand.items()[j][1]
        accumulation[i]=array
        del array
    
    return accumulation

def computeDailyMean(dicoBand,nbBandByDay,typeData):

    def meanCalc(values):
        return np.nanmean(values)

    mean={}
    footprint = np.array([[0,1,0],
                          [1,0,1],
                          [0,1,0]])
    
    for i in range(0,len(dicoBand.keys())/nbBandByDay):
        if (typeData == "analyse"):
            maxRange=nbBandByDay+i*nbBandByDay
        else:
            maxRange=nbBandByDay+i*nbBandByDay-1
        #on ne prend pas la dernière bande... correspondante à 00-->3h
        for j in range (i*nbBandByDay,maxRange):
            if "array" in locals():
                array=array+dicoBand.items()[j][1]
                np.putmask(dicoBand.items()[j][1], dicoBand.items()[j][1]==0, 0)
                mask=mask+(dicoBand.items()[j][1] > 0).astype(int)
            else:
                array=dicoBand.items()[j][1]
                np.putmask(dicoBand.items()[j][1], dicoBand.items()[j][1]==0, 0)
                mask=(dicoBand.items()[j][1] > 0).astype(int)

        mean[i]=array
        del array

        #utilisation de la fonction nanmean --> bcp plus simple
        mean[i]=mean[i]/mask
        indices = np.where(np.isnan(mean[i]))
        results = ndimage.generic_filter(mean[i], meanCalc, footprint=footprint)
        for row, col in zip(*indices):
            mean[i][row,col] = results[row,col]    
    
    return mean

def computeDailyMax(dicoBand,nbBandByDay,typeData=None):
    maxB={}
    for i in range(0,len(dicoBand.keys())/nbBandByDay):
        if (typeData == "analyse"):
            maxRange=nbBandByDay+i*nbBandByDay
        else:
            maxRange=nbBandByDay+i*nbBandByDay-1
        #on ne prend pas la dernière bande... correspondante à 00-->3h si 
        for j in range (i*nbBandByDay,maxRange):
            if "array" in locals():
                array=np.fmax(array,dicoBand.items()[j][1])
            else:
                array=dicoBand.items()[j][1]
        maxB[i]=array 
        del array
    
    return maxB

def computeDailyMin(dicoBand,nbBandByDay,typeData=None):
    minB={}
    for i in range(0,len(dicoBand.keys())/nbBandByDay):
        if (typeData == "analyse"):
            maxRange=nbBandByDay+i*nbBandByDay
        else:
            maxRange=nbBandByDay+i*nbBandByDay-1
        #on ne prend pas la dernière bande... correspondante à 00-->3h
        for j in range (i*nbBandByDay,maxRange):
            np.putmask(dicoBand.items()[j][1],dicoBand.items()[j][1]==0,np.nan)
            if "array" in locals():
                array=np.fmin(array,dicoBand.items()[j][1])
            else:
                array=dicoBand.items()[j][1]
        minB[i]=array 
        del array
    
    return minB
            
def fusVentFromDict(dicToFus,nbBandByDay,zmesure=10):
    """ Wind profile relationship [m.s-1]
        Estimate wind speed at 2m
        uz wind speed at height zmesure above ground surface
        
        wind is the norm of U and V direction speed
    """
    wind={}
    keys=dicToFus.keys()
    if (len(dicToFus)==2):
        for i in dicToFus[keys[0]]:
            #Math.log = ln 
            u=dicToFus[keys[0]][i]*4.87/math.log(67.8*zmesure-5.42);
            v=dicToFus[keys[1]][i]*4.87/math.log(67.8*zmesure-5.42);
            wind[i]=np.sqrt(pow(u,2)+pow(v,2))
    
    return wind

def ComputeHumidityFromPT(pressureDico,TDico,DewDico):
    """ Compute Humidity for each Band and each day based on pressure,Temperature and Dew Point"""
    Humidity={}
    
    for i in pressureDico:
        Humidity[i]=esat(pressureDico[i],DewDico[i])/esat(pressureDico[i],TDico[i])*100
        np.putmask(Humidity[i], pressureDico[i]==0, 0)
        np.putmask(Humidity[i], DewDico[i]==0, 0)
        np.putmask(Humidity[i], TDico[i]==0, 0)
    
    return Humidity
    
    
def esat(pressure,T):
    """ Compute partial presure depending on P and T
        P(T)=0.61121*exp(17.502*T/(T+240.97))*(1.00072+pression*(3.2+0.00059*temperature²)/100000.0)
    
        From Wexler and al. 1976
        Pressure en hpa --> convert to kPa
        T en °C
    """

    pressure=pressure/10
    d_es = 0.61121*np.exp(np.multiply(T,17.502)/(T+240.97))
    d_f = 1.00072+pressure*(3.2+0.00059*pow(T,2))/100000.0
                        
    return d_es*d_f

def delta_calc(T):
    # Slope of saturation vapour pressure curve at air temperature [kPa.°C-1]
    # T air temperature in °C
    # Equation 13 FAO
    delta=4098*(0.6108*np.exp(17.27*T/(T+237.3)))/(T+237.3)**2;
    return delta

def doy(datetoConvert,deltaDays):
    
    deltaJ=timedelta(days=deltaDays)
    datetoConvert=datetoConvert+deltaJ
    J = datetoConvert.timetuple().tm_yday
    
    return J

def getGeoTransform(pathToImg):
        
    srcImage = gdal.Open(pathToImg)
    geoTrans = srcImage.GetGeoTransform()
    
    xOrigin = geoTrans[0]
    yOrigin = geoTrans[3]
    pixelWidth = geoTrans[1]
    pixelHeight = geoTrans[5]

    return (xOrigin,yOrigin,pixelWidth,pixelHeight)
     
def getProj(pathToShape):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(pathToShape, 0)
    layer = dataSource.GetLayer()
    srs = layer.GetSpatialRef()
    
    return srs.ExportToWkt()    

def getShape(pathToImg):
        
    raster = gdal.Open(pathToImg)
    
    transform = raster.GetGeoTransform()
    pixelWidth = transform[1]
    pixelHeight = transform[5]
    
    return (pixelWidth,pixelHeight)

def getCentroidLatFromArray(shape,geotransform,grid):

    lat = np.zeros(shape)
    lon = np.zeros(shape)

    originX =  geotransform[0]
    originY =  geotransform[1]
    
    for index in np.ndenumerate(lat):
        lat.itemset(index[0], float(originX)+float(index[0][0])*float(grid)+(float(grid)/2))
        lon.itemset(index[0], float(originY)-float(index[0][1])*float(grid)-(float(grid)/2))

    
    dicoLatLong={}
    dicoLatLong[0]=lat
    dicoLatLong[1]=lon
    
    return dicoLatLong

def writeTiffFromDicoArray(DicoArray,outputImg,shape,geoparam,proj=None,format=gdal.GDT_Float32):
    
    gdalFormat = 'GTiff'
    driver = gdal.GetDriverByName(gdalFormat)

    dst_ds = driver.Create(outputImg, shape[1], shape[0], len(DicoArray), format)
    
    j=1
    for i in DicoArray.values():
        dst_ds.GetRasterBand(j).WriteArray(i, 0)
        band = dst_ds.GetRasterBand(j)
        band.SetNoDataValue(0)
        j+=1
    
    originX =  geoparam[0]
    originY =  geoparam[1]
    pixelWidth = geoparam[2]
    pixelHeight  = geoparam[3]

    
    dst_ds.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))

def WriteTxtFileForEachPixel(outputFolder,et0,DateList,DoyList,Ray,Tmean,Tmax,Tmin,Hmean,Hmax,Hmin,vent,precipitation,ET0,pressure,Geo,latlon):
    """ Write a Txtfile """
    
    
    for i in range(0,et0[0].shape[0]):
        for j in range(0,et0[0].shape[1]):
            lat=latlon[0][i][j]
            lon=latlon[1][i][j]
            numero = str(round(lat,2)).replace('.','')+str(round(lon,2)).replace('.','')
            
            pathTodateFolder=outputFolder+'/POINT_'+numero+'.txt'
            f = open(pathTodateFolder,'w+')
            f.write('numero;altitude;lat/lon(WGS84)\n')
            f.write(str(numero)+'\t ; '+str(Geo[0][i][j])+'\t ; '+str(lat)+'/'+str(lon)+'\n')
            f.write('ANNEE MOIS JOUR DOY RGCUM TAMEAN TAMAX TAMIN RHMEAN RHMAX RHMIN VUMEAN PRESSURE PRECIP ET0FAO56\n')
            f.write('[YYYY] [MM] [DD] [1-365] [MJ.m-2.jour-1] [Kelvin] [Kelvin] [Kelvin] [%] [%] [%] [m.s-1] [mm.d-1] [mm.d-1] [kPa] [mm.d-1]\n')
            for d in range(0,len(DateList)):
                year=DateList[d].year
                month=DateList[d].month
                day=DateList[d].day
                f.write(str(year)+'\t'+str(month)+'\t'+str(day)+'\t'+ str(DoyList[d])+'\t'+str(Ray[d][i][j])+'\t'+str(Tmean[d][i][j])+'\t'+str(Tmax[d][i][j])+'\t'+str(Tmin[d][i][j])+'\t'+str(Hmean[d][i][j])+'\t'+str(Hmax[d][i][j])+'\t'+str(Hmin[d][i][j])+'\t'+ str(vent[d][i][j])+'\t'+str(precipitation[d][i][j])+'\t'+str(pressure[d][i][j])+'\t'+str(et0[d][i][j])+'\n')
            f.close()
    return pathTodateFolder
    
def WritePointList(outputFolder,latlon):
    
    pathTodateFolder=outputFolder+'/ListeStations.txt'
    f = open(pathTodateFolder,'w+')
    f.write('numero;lat/lon(WGS84)\n')
    for i in range(0,latlon[0].shape[0]):
        for j in range(0,latlon[0].shape[1]):
            lat=latlon[0][i][j]
            lon=latlon[1][i][j]
            numero = str(round(lat,2)).replace('.','')+str(round(lon,2)).replace('.','')
            f.write(str(numero)+';'+str(lat)+';'+str(lon)+'\n')
    f.close()


