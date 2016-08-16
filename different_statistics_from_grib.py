import numpy as np
from osgeo import gdal, gdalnumeric
from osgeo.gdalconst import GA_ReadOnly
gdal.UseExceptions()
import glob
import os

from rasterstats import zonal_stats

def cumulated_means_10days(file_grib, parte_iso, parte_date, anni):

    print "ECMWF file exists calculating statistics"

    ecmfwf_file_asRaster = gdal.Open(file_grib)
    x_size = ecmfwf_file_asRaster.RasterXSize
    y_size = ecmfwf_file_asRaster.RasterYSize
    numero_bande = ecmfwf_file_asRaster.RasterCount

    # print "Ci sono %d bande " % numero_bande
    banda_esempio = ecmfwf_file_asRaster.GetRasterBand(1)
    type_banda_esempio = banda_esempio.DataType

    # Write the out file
    driver = gdal.GetDriverByName("GTiff")

    conteggio = 0
    for anno in anni:
        print anno
        indice = anni.index(anno) + 1
        banda_somma_10gg = np.zeros((y_size, x_size,), dtype=np.float64)
        nome_tiff_cumulata = "5_tests/10_giorni/cumulated/cum_" + parte_iso + "_" + str(indice) + "_" + str(anno) \
                             + "_" + parte_date + ".tif"
        nome_tiff_average = "5_tests/10_giorni/averaged/mean_" + parte_iso + "_" + str(indice) + "_" + str(anno) \
                            + "_" + parte_date + ".tif"
        # print nome_tiff_average
        # print nome_tiff_cumulata
        print "Sto lavorando sull'anno %d" % anno
        for giorno in range(1, 11):
            numero_banda = conteggio + giorno
            # print giorno, anno
            banda = ecmfwf_file_asRaster.GetRasterBand(numero_banda)
            # genera_statistiche_banda_grib(banda, numero_banda)
            data = gdalnumeric.BandReadAsArray(banda)
            cumulata_10gg = banda_somma_10gg + data
            mean_10gg = (cumulata_10gg / 10)

        raster_cum_from_bands = driver.Create(nome_tiff_cumulata, x_size, y_size, 1, type_banda_esempio)
        gdalnumeric.CopyDatasetInfo(ecmfwf_file_asRaster, raster_cum_from_bands)
        banda_dove_scrivere_raster_cum = raster_cum_from_bands.GetRasterBand(1)

        raster_mean_from_bands = driver.Create(nome_tiff_average, x_size, y_size, 1, type_banda_esempio)
        gdalnumeric.CopyDatasetInfo(ecmfwf_file_asRaster, raster_mean_from_bands)
        banda_dove_scrivere_raster_mean = raster_mean_from_bands.GetRasterBand(1)

        try:
            gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_cum, cumulata_10gg)
            gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_mean, mean_10gg)
            print "Raster calculated \n"
        except IOError as err:
            # return str(err.message) + + "\n"
            print str(err.message) + + "\n"

        raster_cum_from_bands = None
        raster_mean_from_bands = None

        conteggio += 1

def media_medie(dir_medie):

    os.chdir(dir_medie)
    medie_monthly_tifs = glob.glob("*.tif")

    file_template = dir_medie + medie_monthly_tifs[0]
    file_template_gdal = gdal.Open(file_template)
    x_size = file_template_gdal.RasterXSize
    y_size = file_template_gdal.RasterYSize
    banda_esempio = file_template_gdal.GetRasterBand(1)
    type_banda_esempio = banda_esempio.DataType

    banda_somma = np.zeros((y_size, x_size,), dtype=np.float64)
    for media_10_giorni in medie_monthly_tifs:
        # print media_10_giorni
        current_file = gdal.Open(dir_medie + media_10_giorni)
        banda = current_file.GetRasterBand(1)
        data = gdalnumeric.BandReadAsArray(banda)
        banda_somma = banda_somma + data

    mean_bande_in_mm = (banda_somma / 37)*1000

    nome_tif_mean = "C:/meteorological/ecmwf/5_tests/10_giorni/averaged/mean_of_means.tif"

    # Write the out file
    driver = gdal.GetDriverByName("GTiff")
    raster_mean_from_bands = driver.Create(nome_tif_mean, x_size, y_size, 1, type_banda_esempio)
    gdalnumeric.CopyDatasetInfo(file_template_gdal, raster_mean_from_bands)
    banda_dove_scrivere_raster_mean = raster_mean_from_bands.GetRasterBand(1)

    try:
        gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_mean, mean_bande_in_mm)
        return "Mean raster exported in" + nome_tif_mean + "\n"
    except IOError as err:
        return str(err.message) + + "\n"

    return medie_monthly_tifs

def media_cumulate(dir_cumulate):

    os.chdir(dir_cumulate)
    cumulated_monthly_tifs = glob.glob("*.tif")

    file_template = dir_cumulate + cumulated_monthly_tifs[0]
    file_template_gdal = gdal.Open(file_template)
    x_size = file_template_gdal.RasterXSize
    y_size = file_template_gdal.RasterYSize
    banda_esempio = file_template_gdal.GetRasterBand(1)
    type_banda_esempio = banda_esempio.DataType

    banda_somma = np.zeros((y_size, x_size,), dtype=np.float64)
    for media_10_giorni in cumulated_monthly_tifs:
        # print media_10_giorni
        current_file = gdal.Open(dir_cumulate + media_10_giorni)
        banda = current_file.GetRasterBand(1)
        data = gdalnumeric.BandReadAsArray(banda)
        banda_somma = banda_somma + data

        # mean_bande_in_mm = (banda_somma/numero_bande)*1000
        # CONFRONTANDO FORECAST CON FORECAST NON HO BISOGNO DI AVERLO IN MILLIMETRI LASCIO TUTTO IN METRI
    mean_bande_in_mm = (banda_somma / 37)*1000

    nome_tif_mean = "C:/meteorological/ecmwf/5_tests/10_giorni/cumulated/mean_of_cumulated.tif"

    # Write the out file
    driver = gdal.GetDriverByName("GTiff")
    raster_mean_from_bands = driver.Create(nome_tif_mean, x_size, y_size, 1, type_banda_esempio)
    gdalnumeric.CopyDatasetInfo(file_template_gdal, raster_mean_from_bands)
    banda_dove_scrivere_raster_mean = raster_mean_from_bands.GetRasterBand(1)

    try:
        gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_mean, mean_bande_in_mm)
        return "Mean raster exported in" + nome_tif_mean + "\n"
    except IOError as err:
        return str(err.message) + + "\n"

    return cumulated_monthly_tifs

def genera_distribuzione_valori(immagine):
    pass

stats = zonal_stats('C:/sparc/input_data/countries/ethiopia.shp',
                    'C:/meteorological/ecmwf/2_mean_from_gribs/mean_GLOBAL_1222_8_19792014.tif',
                    geojson_out=True,
                    # stats="mean",
                    stats=['min', 'max', 'median', 'mean', 'range'],
                    copy_properties=True)

for s in stats:
    print s['properties']['ADM2_CODE'], s['properties']['ADM2_NAME'], s['properties']['mean']

# cumulated_means_10days("1_gribs_from_ecmwf/DjiEriEthSom_2806_07_08_19792016.grib", "DjiEriEthSom", "2806", range(1979, 2016))

# media_medie("C:/meteorological/ecmwf/5_tests/10_giorni/averaged/")
# media_cumulate("C:/meteorological/ecmwf/5_tests/10_giorni/cumulated/")