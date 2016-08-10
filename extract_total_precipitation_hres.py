import os
import numpy as np
import gdal
from gdalconst import *
from osgeo import osr
from osgeo.gdalconst import GA_ReadOnly
from ftplib import FTP
gdal.UseExceptions()

def FtpConnectionFilesGathering():

    lista_files_ECMWF = []

    try:
        ftp = FTP('ftp.wfp.org')
        ftp.login('WFP_GISviewer','FTPviewer')
        messaggioServerFTP = str(ftp.getwelcome()) + "\n"
    except:
        pass

    for file in ftp.nlst():
        filename, file_extension = os.path.splitext(file)
        if file_extension == '' and len(file) == 20:
            lista_files_ECMWF.append(filename)
    ftp.close()

    return messaggioServerFTP, lista_files_ECMWF


def FtpConnectionFilesRetrieval(ecmwf_dir, nomefile):

    lista_files_ECMWF = []

    try:
        ftp = FTP('ftp.wfp.org')
        ftp.login('WFP_GISviewer','FTPviewer')
        messaggioServerFTP = str(ftp.getwelcome()) + "\n"
    except:
        pass

    gFile = open(ecmwf_dir + nomefile, "wb")
    ftp.retrbinary("RETR " + nomefile, gFile.write)
    gFile.close()
    ftp.quit

    return messaggioServerFTP, lista_files_ECMWF


# Function to read the original file's projection:
def GetGeoInfo(FileName):

    SourceDS = gdal.Open(FileName, GA_ReadOnly)
    NDV = SourceDS.GetRasterBand(1).GetNoDataValue()
    xsize = SourceDS.RasterXSize
    ysize = SourceDS.RasterYSize
    GeoT = SourceDS.GetGeoTransform()
    Projection = osr.SpatialReference()
    Projection.ImportFromWkt(SourceDS.GetProjectionRef())
    DataType = SourceDS.GetRasterBand(1).DataType
    DataTypeName = gdal.GetDataTypeName(DataType)
    print "Data Type Name : " + str(DataTypeName)

    NunBandsInGRIB = SourceDS.RasterCount

    for numero_banda in range(1, NunBandsInGRIB + 1):
        TPBand = SourceDS.GetRasterBand(numero_banda)
        metadati = TPBand.GetMetadata()
        if(metadati['GRIB_ELEMENT'] == 'TP'):
            print metadati
            DataTypeTPInt = TPBand.DataType
            DataTypeTP = gdal.GetDataTypeName(DataTypeTPInt)
            DataTP = TPBand.ReadAsArray()
            break

    return NDV, xsize, ysize, GeoT, Projection, DataType, DataTypeTP, TPBand, DataTP, DataTypeTPInt


# Function to write a new file.
def CreateGeoTiffFromSelectedBand(Name, Array, driver, NDV, xsize, ysize, GeoT, Projection, DataType):

    if DataType == 'Float32':
        DataType = gdal.GDT_Float32
    elif DataType == 'Float64':
        DataType == gdal.GDT_Float64

    NewFileName = Name
    Array[np.isnan(Array)] = NDV
    DataSet = driver.Create(NewFileName, xsize, ysize, 1, DataType)  # the '1' is for band 1.
    DataSet.SetGeoTransform(GeoT)
    DataSet.SetProjection(Projection.ExportToWkt())
    DataSet.GetRasterBand(1).WriteArray(Array)
    if NDV:
        DataSet.GetRasterBand(1).SetNoDataValue(NDV)
    else:
        print "No Data None"
    return NewFileName


def EstrazioneBandaTP_hres(FileName, name_TP_tif_file):

    DataSet = gdal.Open(FileName, GA_ReadOnly)
    Band = DataSet.GetRasterBand(1)
    Array = Band.ReadAsArray()
    NDV = Band.GetNoDataValue()
    NDV, xsize, ysize, GeoT, Projection, DataType, DataTypeTP, TPBand, DataTP, DataTypeTPInt = GetGeoInfo(FileName)
    driver = gdal.GetDriverByName('GTiff')

    CreateGeoTiffFromSelectedBand(name_TP_tif_file, DataTP, driver, NDV, xsize, ysize, GeoT, Projection, DataTypeTPInt)

