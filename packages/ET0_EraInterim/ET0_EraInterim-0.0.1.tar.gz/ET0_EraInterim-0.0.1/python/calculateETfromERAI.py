#-*- coding: utf-8 -*-
'''
Created on 25 mars. 2014

Toolbox for ET0 calculation based on EraInterim product
for real time purpose

@author: yoann Moreau
@author: vincent Rivallant
'''

import sys
import getopt
import os
import numpy as np
import math

from datetime import date,datetime,timedelta
import utils as utils
from ecmwfapi import ECMWFDataServer

def main(argv):

    try:
        opts,argv = getopt.getopt(argv,":h:i:e:s:E:o:g:P:t:f:r:",['help','[outFile]','code','[shapeFile]','start','end','[tr]'])
    except getopt.GetoptError:
        print 'error in parameter for eraInterimDownload. type eraInterimDownload.py -help for more detail on use '
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print 'eraInterimDownload.py  '
            print '    [mandatory] : '
            print '        --init <dateStart YYYY-MM-DD>'
            print '        --end <dateEnd YY-MM-DD>'
            print '        --shapefile <shapefile> OU -Extend < xmin,ymax,xmax,ymin>'
            print '    [optional] :'
            print '        --typeData  < analyse , forcast> (default forcast)'
            print '        --grid <EraInterim Time> (default 0.75)'
            print '        --outfile <outfolder> (default /home/user/eraInterim)'
            print '        --proxy <True/False> (default False)'
            print '        --temporaryFile <True/False> (default False)'
            print '        --result < TxtFile / RasterFile> default RasterFile'
            print ''
            sys.exit() 
        elif opt in ('-o','--outFolder'):
            oFolder = arg
        elif opt in ('-i','--start'):
            startDate = arg
        elif opt in ('-e','--end'):
            endDate = arg
        elif opt in ('-s','--shapefile'):
            pathToShapefile = arg
        elif opt in ('-E','--tr'):
            extend = arg.split(',')
        elif opt in ('-g','--grid'):
            grid = arg
        elif opt in ('-P','--proxy'):
            proxy = arg
        elif opt in ('-t','--typeData'):
            typeData = arg
        elif opt in ('-f','--temporaryFile'):
            temporaryFile = arg
        elif opt in ('-r','--result'):
            typeOutput = arg
    
    if len(sys.argv) < 7:
        print 'eraInterimDownload.py'
        print '    -i <dateStart YYYY-MM-DD> '
        print '    -e <dateEnd YY-MM-DD>'
        print '    -s <shapefile> '
        print '  or'
        print '    -E < xmin,ymax,xmax,ymin>]'
        print ''
        print '    [-t < analyse , forcast> (default analyse)]'
        print '    [-g <size of grid in 0.125/0.25/0.5/0.75/1.125/1.5/2/2.5/3> (default0.75)]'
        print '    [-o <outfolder> (default /home/user/eraInterim)]'
        print '    [-P <proxy : True/False> (default False)]'
        print '    [-f <temporaryFile : True/False> (default False)]'
        print '    [-r <resultOutput : TxtFile/RasterFile> (default RasterFile)]'
        print ''
        print 'For help on interimCode -help'
        sys.exit(2)
        
    try:
        oFolder
    except NameError:
        oFolder = os.path.expanduser('~')
        oFolder = oFolder + '/eraInterim'
        print "output folder not precised : downloaded eraInterim images on "+oFolder
    
    # verification du folder/or creation if not exists
    utils.checkForFolder(oFolder) 
        
    try:
        startDate
    except NameError:
        exit ('init Date not precised')
    # verification si sartDate est une date
    startDate=utils.checkForDate(startDate) 
    
    try:
        endDate
    except NameError:
        exit ('end Date not specified')
    # verification si sartDate est une date
    endDate=utils.checkForDate(endDate) 
    
    if (startDate>endDate):
        exit('startDate could not be greater than endDate')
    if (startDate>date(2014,12,31) or endDate>date(2014,12,31) ):
        exit('date could not exceed 2014-12-31')
    
    try:
        pathToShapefile
    except NameError:
        try:
            extend
        except NameError:
            exit ('no Area of interest have been specified. please use -shp or -tr to declare it')
    
    if 'pathToShapefile' in locals():
        extendArea=utils.convertShpToExtend(pathToShapefile)
    else:
        extendArea=extend

    extendArea=utils.checkForExtendValidity(extendArea)
      
    try:
        typeData
    except NameError:
        typeData='analyse'

    try:
        grid
    except NameError:
        grid='0.75'
    grid=utils.checkForGridValidity(grid)
            
    try:
        proxy
    except NameError:
        proxy=False

    #Proxy parameteres needed
    if(proxy):
        login = raw_input('login proxy : ')
        pwd = raw_input('password proxy :  : ')
        site = raw_input('site (surf.cnes.fr) : ')
        os.environ["http_proxy"] = "http://%s:%s@%s:8050"%(login,pwd,site)
        os.environ["https_proxy"] = "http://%s:%s@%s:8050"%(login,pwd,site)
    
    try:
        temporaryFile
    except NameError:
        temporaryFile=False
    
    try:
        typeOutput
    except NameError:
        typeOutput='RasterFile'
    """----------------------------------------"""
    
    
    #Create param if first Time
    if (not utils.checkForFile(os.path.expanduser('~')+'/.ecmwfapirc')):
        print ('for first connexion you have to define yout key and password on ecmwf')
        print ('cf  https://apps.ecmwf.int/auth/login/')
        print ('')
        u = raw_input('user (mail) : ')
        k = raw_input('keys : ')
        utils.createParamFile(os.path.expanduser('~')+'/.ecmwfapirc',u,k)
        
    delta = endDate - startDate
    nbDays = delta.days + float(delta.seconds) / 86400 + 1

    #--------------------------On charge les rasters
    if typeData == "analyse":
        time = ['00',"12","06","18"]
        step = []
        nbBandByDay=len(time)
    else:
        time = ['00',"12"]
        step = [3,6,9,12]
        nbBandByDay=(12*len(time))/(len(step))+1
    server = ECMWFDataServer()
    
    
    """ altitude de la grille EraInterim """
    # Only Forcast possiblet
    codeGeopot= [129]
    GeoFile = oFolder+"/129"+'_'+startDate.strftime('%Y%m%d')+'_'+endDate.strftime('%Y%m%d')+'.nc'
    struct=utils.create_request_sfc(startDate, endDate, time, step, grid, extendArea, codeGeopot, GeoFile,typeData)
    server.retrieve(struct)
    Geo = utils.convertNETCDFtoDicArray(GeoFile)
    Geo = utils.convertGeoToAlt(Geo)
    #un peu inutile car ne change pas ... mais bon! 
    Geo = utils.computeDailyMax(Geo, nbBandByDay, typeData)
    
    """ Vitesse du vent """
    codeVent= [165,166]
    vent={}
    ventFile=[]
    for i in codeVent:
        ventFile.append(oFolder+"/"+str(i)+'_'+startDate.strftime('%Y%m%d')+'_'+endDate.strftime('%Y%m%d')+'.nc')
        struct=utils.create_request_sfc(startDate, endDate, time, step, grid, extendArea, [i], ventFile[-1],typeData)
        server.retrieve(struct)
        vent[i]=utils.convertNETCDFtoDicArray(ventFile[-1])
    
     
    vent = utils.fusVentFromDict(vent,nbBandByDay)
    vent=utils.computeDailyMean(vent,nbBandByDay,typeData)

    """ Humidité relative """
    
    codePressure= [134]
    pressureFile = oFolder+"/134"+'_'+startDate.strftime('%Y%m%d')+'_'+endDate.strftime('%Y%m%d')+'.nc'

    struct=utils.create_request_sfc(startDate, endDate, time, step, grid, extendArea, codePressure, pressureFile,typeData)
    server.retrieve(struct)
    pressure = utils.convertNETCDFtoDicArray(pressureFile)
    #oulalal c'est moche
    pressureMean = utils.convertPaToKgPa(pressure)
    pressure = utils.convertToHectoPascal(pressure)
    pressureMean = utils.computeDailyMean(pressureMean,nbBandByDay,typeData)
    
    codeT2m= [167]
    T2mFile = oFolder+"/167"+'_'+startDate.strftime('%Y%m%d')+'_'+endDate.strftime('%Y%m%d')+'.nc'

    struct=utils.create_request_sfc(startDate, endDate, time, step, grid, extendArea, codeT2m, T2mFile,typeData)
    server.retrieve(struct)
    T2m = utils.convertNETCDFtoDicArray(T2mFile)

    Tmean = utils.computeDailyMean(T2m, nbBandByDay, typeData)
    Tmax = utils.computeDailyMax(T2m,nbBandByDay)
    Tmin = utils.computeDailyMin(T2m,nbBandByDay)
    
    T2m = utils.convertKToD(T2m)
    #T2m = utils.computeDailyMean(T2m,nbBandByDay,typeData)
    
    codeDewP= [168]
    DewPFile = oFolder+"/168"+'_'+startDate.strftime('%Y%m%d')+'_'+endDate.strftime('%Y%m%d')+'.nc'

    struct=utils.create_request_sfc(startDate, endDate, time, step, grid, extendArea, codeDewP, DewPFile,typeData)
    server.retrieve(struct)
    DewP = utils.convertNETCDFtoDicArray(DewPFile)
    DewP = utils.convertKToD(DewP)
    #DewP = utils.computeDailyMean(DewP,nbBandByDay,typeData)

    humidity = utils.ComputeHumidityFromPT(pressure,T2m,DewP)
    #humidity = utils.computeDailyMean(humidity,nbBandByDay,typeData)
    Hmax = utils.computeDailyMax(humidity,nbBandByDay)
    Hmin = utils.computeDailyMin(humidity,nbBandByDay)
    Hmean = utils.computeDailyMean(humidity,nbBandByDay,typeData)
    
    """ ONLY FORCAST FOR THESE VAR"""
    typeData="forcast"
    time = ['00',"12"]
    step = [3,6,9,12]
    nbBandByDay=(12*len(time))/(len(step))+1
    
    """ Precipitation """
    #NOT NEEDED FOR ETO BUT Exported
    
    utils.checkForTimeValidity(time)
    utils.checkForStepValidity(step,typeData)
    codePrecipitation= [228]
    precipitationFile = oFolder+"/228"+'_'+startDate.strftime('%Y%m%d')+'_'+endDate.strftime('%Y%m%d')+'.nc'

    struct=utils.create_request_sfc(startDate, endDate, time, step, grid, extendArea, codePrecipitation, precipitationFile)
    server.retrieve(struct)
    precipitation = utils.convertNETCDFtoDicArray(precipitationFile)
    precipitation=utils.computeDailyAccumulation(precipitation,nbBandByDay,typeData)
    
    
    """ Rayonnement global incident journalier """
    # Only Forcast possiblet
    codeRay= [176]
    RayFile = oFolder+"/176"+'_'+startDate.strftime('%Y%m%d')+'_'+endDate.strftime('%Y%m%d')+'.nc'
    struct=utils.create_request_sfc(startDate, endDate, time, step, grid, extendArea, codeRay, RayFile,typeData)
    server.retrieve(struct)
    Ray = utils.convertNETCDFtoDicArray(RayFile)
    Ray = utils.computeDailyMean(Ray,nbBandByDay,typeData)
    Ray = utils.convertWToMJ(Ray)
    
    """ Grid of latitude [0],longitude[1] in WGS84"""
    geoTransform=utils.getGeoTransform(RayFile)
    shape=Ray[0].shape
    latlon = utils.getCentroidLatFromArray(shape,geoTransform,grid)

    """ --------------------- Compute ET0---------------------- """
    
    ET0={}
    DoyList=[]
    DateList=[]
    
    for i in range(0,int(nbDays)):
        #jour Julien
        J = utils.doy(startDate,i)
        dateEnCours=startDate+ timedelta(days=i)
        DateList.append(dateEnCours)
        DoyList.append(J)
        Hmax[i] = np.where(Hmax[i]>100,100,Hmax[i])
        
        # --- Constants ---# 
        #Solar constant
        Gsc = 0.0820 # [MJ.m-2.min-1]
        #Albedo - grass reference crop
        a = 0.23
        #Ratio of molecular weight of water vapor/dry air
        epsilon=0.622 
        #Latente heat of vaporisation
        Lv=2.45 # [MJ.kg-1]
        # Specific heat at constant pressure
        Cp= 1.013e-3; # [MJ.kg-1.°C-1]
        # Stefan-Boltzmann constant [MJ.K-4.m-2.day-1]
        StefBoltz=4.903e-9; #FAO
        
        # --- Equations ---# 
        # Psychometric constant [kPa.°C-1]
        cte_psy = (Cp*pressureMean[i])/(epsilon*Lv) # Equation 8 Chap 3 FAO
        #Mean sturation vapor presure [kPa]
        es = (utils.esat(pressureMean[i],Tmax[i]) + utils.esat(pressureMean[i],Tmin[i]))/2;    #Equation 12 Chap 3
        # Slope of saturation vapour pressure curve at air temperature [kPa.°C-1]
        delta = utils.delta_calc(Tmean[i]);                    # Equation 13 Chap 3
        # Actual vapour pressure derived from relative humidity [kPa]
        ea = (utils.esat(pressureMean[i],Tmax[i])*(Hmax[i]/100) + utils.esat(pressureMean[i],Tmin[i])*(Hmin[i]/100))/2;      # Equation 17 Chap 3
        # Conversion of latitude from degrees to radians
        phi = (np.pi/180)* latlon[1];     
        # Relative distance Earth-Sun
        dr = 1 + 0.033*math.cos(2*math.pi*J/365);         # Equation 23 Chap 3
        # Solar declination
        d = 0.4093*math.sin(2*math.pi*J/365 - 1.39);      # Equation 24 Chap 3
        # sunset hour angle
        ws = np.arccos(-np.tan(phi)*math.tan(d));                # Equation 25 Chap 3
        # Extraterestrial radiation for daily periods
        Ra = (24.*60/np.pi)*Gsc*dr*(ws*np.sin(phi)*np.sin(d) + np.cos(phi)*np.cos(d)*np.sin(ws))    # Equation 21 Chap 3
        # Clear sky solar radiation [MJ.m-2.day-1]
        Rso = (0.75 + 2e-5*Geo[i])*Ra;                 # Equation 37 Chap 3
        # Net solar radiation [MJ.m-2.day-1]
        Rns = (1 - a)*Ray[i];                          # Equation 38 Chap 3
        #
        f=(1.35*(np.fmin(Ray[i]/Rso,1)) - 0.35);
        # Net longwave radiation [MJ.m-2.day-1]
        Rnl = StefBoltz*((Tmax[i]**4 + Tmin[i]**4)/2)*(0.34 - 0.14*np.sqrt(ea))*f; # Equation 39 Chap 3
        # Net Radiation [MJ.m-2.day-1]
        Rn = Rns - Rnl;                             # Equation 40 Chap 3
        # Soil heat flux at daily scale
        G = 0;                                      # Equation 42 Chap 3

        ET0[i] = ( 0.408*delta*( Rn-G )+ cte_psy*( 900/(Tmean[i] + 273) )*(es - ea)*vent[i] )/( delta + cte_psy*(1 + 0.34*vent[i]) );  # Equation 6 Chap 4
    
    if typeOutput=='RasterFile':
        #On ecrit le fichier ET0 
        geoTransform=utils.getGeoTransform(RayFile)
        shape=Ray[0].shape
        utils.writeTiffFromDicoArray(ET0,oFolder+"/tmp.tif",shape,geoTransform)
        if 'pathToShapefile' in locals():
            utils.reprojRaster(oFolder+"/tmp.tif", oFolder+"/ET0.tif",shape, pathToShapefile)
            os.remove(oFolder+"/tmp.tif")
        else : 
            utils.moveFile(oFolder+"/tmp.tif", oFolder+"/ET0.tif")

        #On écrit le fichier Precipitation
        geoTransform=utils.getGeoTransform(precipitationFile)
        shape=precipitation[0].shape
        utils.writeTiffFromDicoArray(precipitation,oFolder+"/tmp.tif",shape,geoTransform)
    
        if 'pathToShapefile' in locals():
            utils.reprojRaster(oFolder+"/tmp.tif", oFolder+"/precipitationAcc.tif",shape, pathToShapefile)
            os.remove(oFolder+"/tmp.tif")
        else : 
            utils.moveFile(oFolder+"/tmp.tif", oFolder+"/precipitationAcc.tif")
        
    else:
        #On ecrit le fichier au format Txt
        utils.WriteTxtFileForEachPixel(oFolder,ET0,DateList,DoyList,Ray,Tmean,Tmax,Tmin,Hmean,Hmax,Hmin,vent,precipitation,ET0,pressureMean,Geo,latlon)
        utils.WritePointList(oFolder,latlon)
    
    """ ------------------------------------------- """
    if(temporaryFile):
        #On ecrit le fichier latlon 
        geoTransform=utils.getGeoTransform(GeoFile)
        shape=Geo[0].shape
        utils.writeTiffFromDicoArray(Geo,oFolder+"/tmp.tif",shape,geoTransform)
    
        if 'pathToShapefile' in locals():
            utils.reprojRaster(oFolder+"/tmp.tif", oFolder+"/altitude.tif",shape, pathToShapefile)
            os.remove(oFolder+"/tmp.tif")
        else : 
            utils.moveFile(oFolder+"/tmp.tif", oFolder+"/altitude.tif")
    
        #On ecrit le fichier latlon 
        geoTransform=utils.getGeoTransform(RayFile)
        shape=Ray[0].shape
        utils.writeTiffFromDicoArray(latlon,oFolder+"/tmp.tif",shape,geoTransform)
    
        if 'pathToShapefile' in locals():
            utils.reprojRaster(oFolder+"/tmp.tif", oFolder+"/latLon.tif",shape, pathToShapefile)
            os.remove(oFolder+"/tmp.tif")
        else : 
            utils.moveFile(oFolder+"/tmp.tif", oFolder+"/latLon.tif")
        
        
        #On ecrit le fichier vent --> a enlever
        geoTransform=utils.getGeoTransform(ventFile[-1])
        shape=vent[0].shape
        utils.writeTiffFromDicoArray(vent,oFolder+"/tmp.tif",shape,geoTransform)
    
        if 'pathToShapefile' in locals():
            utils.reprojRaster(oFolder+"/tmp.tif", oFolder+"/ventMean.tif",shape, pathToShapefile)
            os.remove(oFolder+"/tmp.tif")
        else : 
            utils.moveFile(oFolder+"/tmp.tif", oFolder+"/ventMean.tif")
        
        #On ecrit le fichier Rhmin
        geoTransform=utils.getGeoTransform(pressureFile)
        shape=pressureMean[0].shape
        utils.writeTiffFromDicoArray(pressureMean,oFolder+"/tmp.tif",shape,geoTransform)
    
        if 'pathToShapefile' in locals():
            utils.reprojRaster(oFolder+"/tmp.tif", oFolder+"/pressureMean.tif",shape, pathToShapefile)
            os.remove(oFolder+"/tmp.tif")
        else : 
            utils.moveFile(oFolder+"/tmp.tif", oFolder+"/pressureMean.tif")
        
        #On ecrit le fichier Rhmax
        geoTransform=utils.getGeoTransform(pressureFile)
        shape=Hmax[0].shape
        utils.writeTiffFromDicoArray(Hmax,oFolder+"/tmp.tif",shape,geoTransform)
    
        if 'pathToShapefile' in locals():
            utils.reprojRaster(oFolder+"/tmp.tif", oFolder+"/humidityMax.tif",shape, pathToShapefile)
            os.remove(oFolder+"/tmp.tif")
        else : 
            utils.moveFile(oFolder+"/tmp.tif", oFolder+"/humidityMax.tif")
        
        #On ecrit le fichier Rhmin
        geoTransform=utils.getGeoTransform(pressureFile)
        shape=Hmin[0].shape
        utils.writeTiffFromDicoArray(Hmin,oFolder+"/tmp.tif",shape,geoTransform)
    
        if 'pathToShapefile' in locals():
            utils.reprojRaster(oFolder+"/tmp.tif", oFolder+"/humidityMin.tif",shape, pathToShapefile)
            os.remove(oFolder+"/tmp.tif")
        else : 
            utils.moveFile(oFolder+"/tmp.tif", oFolder+"/humidityMin.tif")
    
        #On ecrit le fichier Tmax
        geoTransform=utils.getGeoTransform(T2mFile)
        shape=Tmax[0].shape
        utils.writeTiffFromDicoArray(Tmax,oFolder+"/tmp.tif",shape,geoTransform)
    
        if 'pathToShapefile' in locals():
            utils.reprojRaster(oFolder+"/tmp.tif", oFolder+"/TemperatureMax.tif",shape, pathToShapefile)
            os.remove(oFolder+"/tmp.tif")
        else : 
            utils.moveFile(oFolder+"/tmp.tif", oFolder+"/TemperatureMax.tif")
    
        #On ecrit le fichier Tmin
        geoTransform=utils.getGeoTransform(T2mFile)
        shape=Tmin[0].shape
        utils.writeTiffFromDicoArray(Tmin,oFolder+"/tmp.tif",shape,geoTransform)
    
        if 'pathToShapefile' in locals():
            utils.reprojRaster(oFolder+"/tmp.tif", oFolder+"/TemperatureMin.tif",shape, pathToShapefile)
            os.remove(oFolder+"/tmp.tif")
        else : 
            utils.moveFile(oFolder+"/tmp.tif", oFolder+"/TemperatureMin.tif")
        
        #On ecrit le fichier Rayonnement
        geoTransform=utils.getGeoTransform(RayFile)
        shape=Ray[0].shape
        utils.writeTiffFromDicoArray(Ray,oFolder+"/tmp.tif",shape,geoTransform)
    
        if 'pathToShapefile' in locals():
            utils.reprojRaster(oFolder+"/tmp.tif", oFolder+"/RayonnementMean.tif",shape, pathToShapefile)
            os.remove(oFolder+"/tmp.tif")
        else : 
            utils.moveFile(oFolder+"/tmp.tif", oFolder+"/RayonnementMean.tif")
    
    #on supprime les fichier intermédiare !
    os.remove(pressureFile)
    os.remove(T2mFile)
    os.remove(DewPFile)
    os.remove(RayFile)
    os.remove(GeoFile)
    for i in ventFile:
        os.remove(i)
    os.remove(precipitationFile)
    
if __name__ == '__main__':
    main(sys.argv[1:])

    pass