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

    # lista_files = ftp.retrlines('LIST')
    # lista_files = ftp.dir()
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
            # stats = TPBand.GetStatistics(True, True)
            # if stats is None:
            #     pass
            # print "Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % (stats[0], stats[1], stats[2], stats[3])
            # print "NO DATA VALUE = ", TPBand.GetNoDataValue()
            # print "MIN = ", TPBand.GetMinimum()
            # print "MAX = ", TPBand.GetMaximum()
            # print "SCALE = ", TPBand.GetScale()
            # print "UNIT TYPE = ", TPBand.GetUnitType()
            break

    return NDV, xsize, ysize, GeoT, Projection, DataType, DataTypeTP, TPBand, DataTP, DataTypeTPInt


# Function to write a new file.
def CreateGeoTiffFromSelectedBand(Name, Array, driver, NDV, xsize, ysize, GeoT, Projection, DataType):

    if DataType == 'Float32':
        DataType = gdal.GDT_Float32
    elif DataType == 'Float64':
        DataType == gdal.GDT_Float64

    NewFileName = Name + '.tif'
    # Set nans to the original No Data Value
    Array[np.isnan(Array)] = NDV
    # Set up the dataset
    DataSet = driver.Create(NewFileName, xsize, ysize, 1, DataType)  # the '1' is for band 1.
    DataSet.SetGeoTransform(GeoT)
    DataSet.SetProjection(Projection.ExportToWkt())
    # Write the array
    DataSet.GetRasterBand(1).WriteArray(Array)
    if NDV:
        DataSet.GetRasterBand(1).SetNoDataValue(NDV)
    else:
        print "No Data None"

    return NewFileName


def EstrazioneBandaTP_hres(FileName, name_TP_tif_file):

    # FileName = "ecmwf_ftp_wfp/A1D12020000121200001.grib"
    # name_TP_tif_file = "ecmwf_ftp_wfp/TP_0212_2"

    DataSet = gdal.Open(FileName, GA_ReadOnly)
    # Get the first (and only) band.
    Band = DataSet.GetRasterBand(1)
    # Open as an array.
    Array = Band.ReadAsArray()
    # Get the No Data Value
    NDV = Band.GetNoDataValue()
    # Convert No Data Points to nans
    # Array[Array == NDV] = np.nan
    # Now I do some processing on Array, it's pretty complex
    # but for this example I'll just add 20 to each pixel.
    # NewArray = Array + 20  # If only it were that easy
    # Now I'm ready to save the new file, in the meantime I have
    # closed the original, so I reopen it to get the projection
    # information...
    NDV, xsize, ysize, GeoT, Projection, DataType, DataTypeTP, TPBand, DataTP, DataTypeTPInt = GetGeoInfo(FileName)
    # print NDV, xsize, ysize, GeoT, Projection, DataType , DataTypeTPInt
    # print DataTypeTP
    # print DataTP
    # Set up the GTiff driver
    driver = gdal.GetDriverByName('GTiff')

    CreateGeoTiffFromSelectedBand(name_TP_tif_file, DataTP, driver, NDV, xsize, ysize, GeoT, Projection, DataTypeTPInt)

# print FtpConnectionFilesGatheringIMERG()
# EstrazioneBandaTP_hres("ecmwf_ftp_wfp/18Jan_Rogerio/A1D01180000012800001.grib","ecmwf_ftp_wfp/18Jan_Rogerio/0118_0128_2016")