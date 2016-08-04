import numpy as np
from osgeo import gdal, gdalnumeric,ogr,osr
from osgeo.gdalconst import GA_ReadOnly
import Image, ImageDraw
import os, sys
gdal.UseExceptions()

# This function will convert the rasterized clipper shapefile
# to a mask for use within GDAL.
def imageToArray(i):
    """
    Converts a Python Imaging Library array to a
    gdalnumeric image.
    """
    a=gdalnumeric.fromstring(i.tostring(),'b')
    a.shape=i.im.size[1], i.im.size[0]
    return a


def arrayToImage(a):
    """
    Converts a gdalnumeric array to a
    Python Imaging Library Image.
    """
    i=Image.fromstring('L',(a.shape[1],a.shape[0]),
            (a.astype('b')).tostring())
    return i


def world2Pixel(geoMatrix, x, y):

    """
    Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
    the pixel location of a geospatial coordinate
    (source http://www2.geog.ucl.ac.uk/~plewis/geogg122/vectorMask.html)
    geoMatrix
    [0] = top left x (x Origin)
    [1] = w-e pixel resolution (pixel Width)
    [2] = rotation, 0 if image is "north up"
    [3] = top left y (y Origin)
    [4] = rotation, 0 if image is "north up"
    [5] = n-s pixel resolution (pixel Height)
    """

    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]
    rtnX = geoMatrix[2]
    rtnY = geoMatrix[4]
    pixel = np.round((x - ulX) / xDist).astype(np.int)
    line = np.round((ulY - y) / xDist).astype(np.int)

    return pixel, line


def genera_anomalia_globale(file_climate,file_current):

        climate_file = gdal.Open(file_climate)
        x_size_clim = climate_file.RasterXSize
        y_size_clim = climate_file.RasterYSize
        print "Size of climate raster X=%0.2f Y=%0.2f" % (x_size_clim, y_size_clim)


        geotransform_climate = climate_file.GetGeoTransform()
        originX_clim = geotransform_climate[0]
        originY_clim = geotransform_climate[3]
        pixelWidth_clim = geotransform_climate[1]
        pixelHeight_clim = geotransform_climate[5]
        print "Origin of climate file X=%0.2f Y=%0.2f" % (originX_clim,originY_clim)
        print "Size of pixel for climate raster Width=%0.2f and Height=%0.2f" % (pixelWidth_clim,pixelHeight_clim)

        banda_climate = climate_file.GetRasterBand(1)
        print "Tipo dato file climate %s" % banda_climate.DataType

        current_file = gdal.Open(file_current)
        x_size_curr = current_file.RasterXSize
        y_size_curr = current_file.RasterYSize
        print
        print "Size of current raster X=%0.2f Y=%0.2f" % (x_size_curr,y_size_curr)

        geotransform_current = current_file.GetGeoTransform()
        originX_curr = geotransform_current[0]
        originY_curr = geotransform_current[3]
        pixelWidth_curr = geotransform_current[1]
        pixelHeight_curr = geotransform_current[5]
        print "Origin of current file X=%0.2f Y=%0.2f" % (originX_curr, originY_curr)
        print "Size of pixel for current raster Width=%0.2f and Height=%0.2f" % (pixelWidth_curr, pixelHeight_curr)

        banda_current = current_file.GetRasterBand(1)
        print "Tipo dato file current %s" % banda_current.DataType

        type_banda_esempio = banda_current.DataType

        data_current = gdalnumeric.BandReadAsArray(banda_current)
        data_climate = gdalnumeric.BandReadAsArray(banda_climate, xoff=0, yoff=72, win_xsize=2880, win_ysize=1297)

        banda_anomala = np.subtract(data_current, data_climate)

        nome_tif_anomalie = "4_anomalies_3_minus_2/" + str(file_climate).split("/")[1].replace("mean","anm")

        # Write the out file
        driver = gdal.GetDriverByName("GTiff")
        raster_anomaly_from_bands = driver.Create(nome_tif_anomalie, x_size_curr, y_size_curr, 1, type_banda_esempio)
        gdalnumeric.CopyDatasetInfo(current_file, raster_anomaly_from_bands)
        banda_dove_scrivere_raster_anomaly = raster_anomaly_from_bands.GetRasterBand(1)

        try:
            gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_anomaly, banda_anomala)
            return "Mean raster exported in" + nome_tif_anomalie + "\n"
        except IOError as err:
            return str(err.message) + "\n"


def coordinate_da_tagliare_sul_raster_precipitazione_globale(file_climate):

    climate_file = gdal.Open(file_climate)
    x_size_clim = climate_file.RasterXSize
    y_size_clim = climate_file.RasterYSize

    geotransform_climate = climate_file.GetGeoTransform()
    originX_clim = geotransform_climate[0]
    originY_clim = geotransform_climate[3]
    pixelWidth_clim = geotransform_climate[1]
    pixelHeight_clim = geotransform_climate[5]

    return originX_clim,originY_clim


def genera_anomalia_partial(file_current,ulY,lrY,ulX,lrX):

    climate_file = gdal.Open(file_climate)
    x_size_clim = climate_file.RasterXSize
    y_size_clim = climate_file.RasterYSize
    print "Size of climate raster X=%0.4f Y=%0.4f" % (x_size_clim, y_size_clim)

    geotransform_climate = climate_file.GetGeoTransform()
    originX_clim = geotransform_climate[0]
    originY_clim = geotransform_climate[3]
    pixelWidth_clim = geotransform_climate[1]
    pixelHeight_clim = geotransform_climate[5]
    print "Origin of climate file X=%0.4f Y=%0.4f" % (originX_clim, originY_clim)
    print "Size of pixel for climate raster Width=%0.4f and Height=%0.4f" % (pixelWidth_clim, pixelHeight_clim)

    banda_climate = climate_file.GetRasterBand(1)
    print "Tipo dato file climate %s" % banda_climate.DataType

    current_file = gdal.Open(file_current)
    x_size_curr = current_file.RasterXSize
    y_size_curr = current_file.RasterYSize
    print "Size of current raster X=%0.4f Y=%0.4f" % (x_size_curr, y_size_curr)

    geotransform_current = current_file.GetGeoTransform()
    originX_curr = geotransform_current[0]
    originY_curr = geotransform_current[3]
    pixelWidth_curr = geotransform_current[1]
    pixelHeight_curr = geotransform_current[5]
    print "Origin of current file X=%0.2f Y=%0.2f" % (originX_curr, originY_curr)
    print "Size of pixel for current raster Width=%0.4f and Height=%0.4f" % (pixelWidth_curr, pixelHeight_curr)

    banda_current = current_file.GetRasterBand(1)
    print "Tipo dato file current %d" % banda_current.DataType

    # ulX = int((originX_clim - originX_curr)/pixelWidth_clim)
    # ulY = int((originY_clim - originY_curr)/pixelHeight_clim)
    # print ("Sopra ulX: %d ulY: %d") % (ulX, ulY)
    #
    # lrX = int(ulX + x_size_clim)
    # lrY = int(ulY - y_size_clim)
    # print ("Sotto lrX: %d lrY: %d") % (lrX,lrY)
    #
    # # banda_sottrazione = np.zeros((y_size_clim, x_size_clim,), dtype=np.float64)
    #
    # originX_curr_cut = geotransform_climate[0]
    # originY_curr_cut = geotransform_climate[3]
    # endX_clim = originX_curr_cut + (x_size_clim*pixelWidth_clim)
    # endY_clim = originY_curr_cut + (y_size_clim * pixelHeight_clim)

    data_current = gdalnumeric.BandReadAsArray(banda_current)
    clip_data_current = data_current[ulY:lrY, ulX:lrX]
    # clip_data_current = data_current[originX_curr_cut:endY_clim,originY_curr_cut:endY_clim ]

    type_banda_esempio = banda_climate.DataType

   #SOLO PER VEDERE I PASSI INTERMEDI
    nome_tif_current_clip = "4_anomalies_3_minus_2/TP_07280806_clip.tif"

    driver = gdal.GetDriverByName("GTiff")
    raster_anomaly_clip = driver.Create(nome_tif_current_clip, x_size_clim, y_size_clim, 1, type_banda_esempio)
    gdalnumeric.CopyDatasetInfo(climate_file, raster_anomaly_clip)
    banda_dove_scrivere_raster_clip = raster_anomaly_clip.GetRasterBand(1)

    try:
        gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_clip, clip_data_current)
    except IOError as err:
        return str(err.message) + "\n"
    # SOLO PER VEDERE I PASSI INTERMEDI

    data_climate = gdalnumeric.BandReadAsArray(banda_climate)

    # # banda_sottrazione = clip_data_current - data_climate
    # banda_sottrazione = np.subtract(clip_data_current,data_climate)
    #
    # # nome_tif_anomalie = "4_anomalies_3_minus_2/anm_piccolo_test.tif"
    # nome_tif_anomalie = "4_anomalies_3_minus_2/" + str(file_climate).split("/")[1].replace("mean","anm")
    #
    # driver = gdal.GetDriverByName("GTiff")
    # raster_anomaly_from_bands = driver.Create(nome_tif_anomalie, x_size_clim, y_size_clim, 1, type_banda_esempio)
    # gdalnumeric.CopyDatasetInfo(climate_file, raster_anomaly_from_bands)
    # banda_dove_scrivere_raster_anomaly = raster_anomaly_from_bands.GetRasterBand(1)
    #
    # try:
    #     gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_anomaly, banda_sottrazione)
    #     return "Mean raster exported in" + nome_tif_anomalie + "\n"
    # except IOError as err:
    #     return str(err.message) + "\n"


def analisi_raster_con_GDALNUMERICS(grib_file):

    grib_file_aperto = gdal.Open(grib_file, GA_ReadOnly)

    x_size = grib_file_aperto.RasterXSize
    y_size = grib_file_aperto.RasterYSize
    numero_bande = grib_file_aperto.RasterCount

    for numero_banda in range(1, numero_bande+1):
        banda_corrente = grib_file_aperto.GetRasterBand(numero_banda)
        metadati = banda_corrente.GetMetadata()

    return x_size, y_size, numero_bande


def coordinate_immagini(raster_path):

    # Load the source data as a gdalnumeric array
    srcArray = gdalnumeric.LoadFile(raster_path)

    srcImage = gdal.Open(raster_path)
    geoTrans = srcImage.GetGeoTransform()

    # Convert the layer extent to image pixel coordinates
    minX, maxX, minY, maxY = 32.9375,18.0625,51.0625,-2.0625
    ulX, ulY = world2Pixel(geoTrans, minX, maxY)
    lrX, lrY = world2Pixel(geoTrans, maxX, minY)

    # Calculate the pixel size of the new image
    pxWidth = int(lrX - ulX)
    pxHeight = int(lrY - ulY)

    return ulY,lrY,ulX,lrX


if __name__ == '__main__':

    file_current = "3_ecmwf_ftp_wfp/TP_07280806.tif"
    file_climate = "2_mean_from_gribs/mean_GLOBAL_2806_07_08_19792015.tif"

    # genera_anomalia_globale(file_climate,file_current)

    file_climate_partial = "2_mean_from_gribs/mean_DjiEriEthSom_2806_07_08_19792016.tif"
    origine_file_mean = coordinate_da_tagliare_sul_raster_precipitazione_globale(file_climate_partial)
    print origine_file_mean

    ulY, lrY, ulX, lrX = coordinate_immagini("3_ecmwf_ftp_wfp/TP_07280806.tif")
    # genera_anomalia_partial(file_climate_partial, file_current,ulY,lrY,ulX,lrX)
