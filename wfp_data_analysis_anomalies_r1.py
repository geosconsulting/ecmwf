import numpy as np
from osgeo import gdal, gdalnumeric
gdal.UseExceptions()



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


def coordinate_immagini(raster_path):

        # Load the source data as a gdalnumeric array
        srcArray = gdalnumeric.LoadFile(raster_path)

        srcImage = gdal.Open(raster_path)
        x_size = srcImage.RasterXSize
        y_size = srcImage.RasterYSize

        geoTrans = srcImage.GetGeoTransform()

        minX = geoTrans[0]
        minY = geoTrans[3]
        pixelWidth = geoTrans[1]
        pixelHeight = geoTrans[5]
        maxX = minX + (x_size * pixelWidth)
        maxY = minY + (y_size * pixelHeight)

        return minX, minY, maxX, maxY


def taglio_raster_corrente_su_area_mean_partial(file_current_path, ulY, lrY, ulX, lrX, climate_file_path):

        climate_file = gdal.Open(climate_file_path)
        banda_climate = climate_file.GetRasterBand(1)
        x_size_clim = climate_file.RasterXSize
        y_size_clim = climate_file.RasterYSize

        current_file = gdal.Open(file_current_path)
        banda_current = current_file.GetRasterBand(1)
        data_current = gdalnumeric.BandReadAsArray(banda_current)

        clip_data_current = data_current[ulY:lrY,ulX:lrX]
        type_banda_esempio = banda_current.DataType

        # SOLO PER VEDERE I PASSI INTERMEDI
        # SOLO PER VEDERE I PASSI INTERMEDI
        file_name_clip = file_current_path.split("/")[1].split(".")[0] + "_clip.tif"
        path_tif_current_clip = "4_anomalies_3_minus_2/" + file_name_clip

        driver = gdal.GetDriverByName("GTiff")
        raster_anomaly_clip = driver.Create(path_tif_current_clip, x_size_clim, y_size_clim, 1, type_banda_esempio)
        gdalnumeric.CopyDatasetInfo(climate_file, raster_anomaly_clip)
        banda_dove_scrivere_raster_clip = raster_anomaly_clip.GetRasterBand(1)

        try:
            gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_clip, clip_data_current)
        except IOError as err:
            return str(err.message) + "\n"
        # SOLO PER VEDERE I PASSI INTERMEDI
        # SOLO PER VEDERE I PASSI INTERMEDI

        data_climate = gdalnumeric.BandReadAsArray(banda_climate)

        banda_sottrazione = np.subtract(clip_data_current, data_climate*10)
        nome_tif_anomalie = "4_anomalies_3_minus_2/" + str(climate_file_path).split("/")[1].split(".")[0].replace("mean","anm") + ".tif"
        print "nome anomalie generato %s " % nome_tif_anomalie

        driver = gdal.GetDriverByName("GTiff")
        raster_anomaly_from_bands = driver.Create(nome_tif_anomalie, x_size_clim, y_size_clim, 1, type_banda_esempio)
        gdalnumeric.CopyDatasetInfo(climate_file, raster_anomaly_from_bands)
        banda_dove_scrivere_raster_anomaly = raster_anomaly_from_bands.GetRasterBand(1)
        try:
            gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_anomaly, banda_sottrazione)
            return "Mean raster exported in" + nome_tif_anomalie + "\n"
        except IOError as err:
            print err.message
            # return str(err.message) + "\n"


def misura_immagini(raster_path):

        # Load the source data as a gdalnumeric array
        srcArray = gdalnumeric.LoadFile(raster_path)

        srcImage = gdal.Open(raster_path)
        x_size = srcImage.RasterXSize
        y_size = srcImage.RasterYSize

        geoTrans = srcImage.GetGeoTransform()

        minX = geoTrans[0]
        minY = geoTrans[3]
        pixelWidth = geoTrans[1]
        pixelHeight = geoTrans[5]
        maxX = minX + (x_size * pixelWidth)
        maxY = minY + (y_size * pixelHeight)

        # Convert the layer extent to image pixel coordinates
        ulX, ulY = world2Pixel(geoTrans, minX, maxY)
        lrX, lrY = world2Pixel(geoTrans, maxX, minY)

        # Calculate the pixel size of the new image
        pxWidth = abs(int(lrX - ulX))
        pxHeight = abs(int(lrY - ulY))

        return pxWidth,pxHeight


def coordinate_da_tagliare_sul_raster_precipitazione_globale(raster_path, minX, maxY, maxX, minY):

        # Load the source data as a gdalnumeric array
        srcArray = gdalnumeric.LoadFile(raster_path)
        srcImage = gdal.Open(raster_path)

        x_size = srcImage.RasterXSize
        y_size = srcImage.RasterYSize

        geoTrans = srcImage.GetGeoTransform()

        # Convert the layer extent to image pixel coordinates
        ulX, ulY = world2Pixel(geoTrans, minX, maxY)
        lrX, lrY = world2Pixel(geoTrans, maxX, minY)

        return ulY, lrY, ulX, lrX


    # if __name__ == '__main__':
    #
    #     file_current = "3_ecmwf_ftp_wfp/TP_803813.tif"
    #     file_climate = "2_mean_from_gribs/mean_GLOBAL_2806_07_08_19792015.tif"
    #     file_climate_partial = "2_mean_from_gribs/mean_Gua_0313_08_19792016.tif"    #
    #
    #     minX_clim_ar, maxY_clim_ar, maxX_clim_ar, minY_clim_ar = coordinate_immagini(file_climate_partial)
    #     print "Le coordinate di %s \nsono left %0.4f bottom %0.4f right %0.4f top %0.4f" %(
    #         file_climate_partial, minX_clim_ar, minY_clim_ar, maxX_clim_ar, maxY_clim_ar)
    #
    #     larghezza,altezza = misura_immagini(file_climate_partial)
    #     print "Le dimensioni della immagine %s \nsono larghezza %d altezza %d" % (file_climate_partial, larghezza, altezza)
    #     # taglio_raster_corrente_su_area_mean_partial(file_climate_partial, file_current,ulY,lrY,ulX,lrX)
    #
    #     print
    #     minX, maxY, maxX, minY = coordinate_immagini(file_current)
    #     print "Le coordinate di %s \nsono left %0.4f bottom %0.4f right %0.4f top %0.4f" % (file_current, minX, minY, maxX, maxY)
    #
    #     larghezza, altezza = misura_immagini(file_current)
    #     print "Le dimensioni della immagine %s \nsono larghezza %d altezza %d" % (file_current, larghezza, altezza)
    #     # taglio_raster_corrente_su_area_mean_partial(file_climate_partial, file_current,ulY,lrY,ulX,lrX)
    #
    #     ulY,lrY,lrX,ulX = coordinate_da_tagliare_sul_raster_precipitazione_globale(file_current, minX_clim_ar, maxY_clim_ar, maxX_clim_ar, minY_clim_ar)
    #     print
    #     print "Le coordinate di taglio per  %s inviate sono ulX %0.4f lrY %0.4f lrX %0.4f ulY %0.4f" % (
    #         file_climate_partial, minX_clim_ar, minY_clim_ar, maxX_clim_ar, maxY_clim_ar )
    #     print "Le coordinate di taglio derivate da %s \nsono ulX %0.4f lrY %0.4f lrX %0.4f ulY %0.4f" % (
    #     file_climate_partial, ulY, lrY, lrX, ulX)
    #     taglio_raster_corrente_su_area_mean_partial(file_current, ulY, lrY, lrX, ulX,file_climate_partial)