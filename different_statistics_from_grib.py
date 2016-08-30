from numpy import linspace
from numpy import meshgrid
import numpy as np
from osgeo import gdal, gdalnumeric
from osgeo.gdalconst import GA_ReadOnly
gdal.UseExceptions()
import glob
import os
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

from rasterstats import zonal_stats

def cumulated_means_10days(file_grib, parte_iso, parte_date, anni):

    ecmfwf_file_asRaster = gdal.Open(file_grib)
    x_size = ecmfwf_file_asRaster.RasterXSize
    y_size = ecmfwf_file_asRaster.RasterYSize
    numero_bande = ecmfwf_file_asRaster.RasterCount
    print "numero bande %d " % numero_bande
    banda_esempio = ecmfwf_file_asRaster.GetRasterBand(1)
    type_banda_esempio = banda_esempio.DataType
    driver = gdal.GetDriverByName("GTiff")

    conteggio = 0
    for anno in anni:
        print anno
        indice = anni.index(anno) + 1
        banda_somma_10gg = np.zeros((y_size, x_size,), dtype=np.float64)
        nome_tiff_cumulata = "5_tests/10_giorni/cumulated/cum_" + parte_iso + str(indice) + "_" + str(anno) \
                             + "_" + parte_date + ".tif"
        nome_tiff_average = "5_tests/10_giorni/averaged/mean_" + parte_iso + str(indice) + "_" + str(anno) \
                            + "_" + parte_date + ".tif"
        print "Sto lavorando sull'anno %d" % anno
        for giorno in range(1, 11):
            numero_banda = conteggio + giorno
            banda = ecmfwf_file_asRaster.GetRasterBand(numero_banda)
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


def anomalie_annue_10gg_cumulate(nome_current_TP):

    dir_differenza_attuale_passate = "C:/meteorological/ecmwf/5_tests/10_giorni/anm_annuali_su_cumulata/"

    os.chdir("C:/meteorological/ecmwf/5_tests/10_giorni/cumulated")
    cumulated_monthly_tifs = glob.glob("*.tif")

    file_template = cumulated_monthly_tifs[0]
    file_template_gdal = gdal.Open(file_template)
    x_size = file_template_gdal.RasterXSize
    y_size = file_template_gdal.RasterYSize
    banda_esempio = file_template_gdal.GetRasterBand(1)
    type_banda_esempio = banda_esempio.DataType

    current_file = gdal.Open(nome_current_TP)
    banda_corrente = current_file.GetRasterBand(1)
    dati_corrente = gdalnumeric.BandReadAsArray(banda_corrente)

    for cumulata_10_giorni in cumulated_monthly_tifs:
        file_anno = gdal.Open(cumulata_10_giorni)
        banda_anno= file_anno.GetRasterBand(1)
        dati_anno = gdalnumeric.BandReadAsArray(banda_anno, xoff=0, yoff=72, win_xsize=2880, win_ysize=1297)
        banda_anomala = np.subtract(dati_corrente, dati_anno)
        nome_tif_da_scrivere = dir_differenza_attuale_passate + "anm_" + \
                                str(cumulata_10_giorni).split("_")[3] + "_" + \
                                str(cumulata_10_giorni).split("_")[4]
        print nome_tif_da_scrivere

        driver = gdal.GetDriverByName("GTiff")
        raster_mean_from_bands = driver.Create(nome_tif_da_scrivere, x_size, y_size, 1, type_banda_esempio)
        gdalnumeric.CopyDatasetInfo(file_template_gdal, raster_mean_from_bands)
        banda_dove_scrivere_raster_mean = raster_mean_from_bands.GetRasterBand(1)

        try:
            gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_mean, banda_anomala)
        except IOError as err:
            return str(err.message) + "\n"

    return cumulated_monthly_tifs


def genera_istogramma_valori(rater_file_txt):



    ds = gdal.Open(rater_file_txt)
    data = ds.ReadAsArray()
    gt = ds.GetGeoTransform()
    proj = ds.GetProjection()

    xres = gt[1]
    yres = gt[5]

    xmin = gt[0] + xres * 0.5
    xmax = gt[0] + (xres * ds.RasterXSize) - xres * 0.5
    ymin = gt[3] + (yres * ds.RasterYSize) + yres * 0.5
    ymax = gt[3] - yres * 0.5
    x_center = (xmin + xmax) / 2
    y_center = (ymin + ymax) / 2

    data_transp = np.transpose(data)
    fig = plt.figure(figsize=(18, 10))
    ax = fig.add_subplot(111, axisbg='w', frame_on=True)
    plt.hist(data_transp,bins=25)
    plt.show()


def genera_mappa(rater_file_txt):

    # # Write the out file
    # driver = gdal.GetDriverByName("GTiff")
    # raster_file = gdal.Open(rater_file_txt)
    #
    # banda = raster_file.GetRasterBand(1)
    # data = gdalnumeric.BandReadAsArray(banda)
    # plt.plot(data,type='barplot')
    # plt.show()
    #################################################################################

    ds = gdal.Open(rater_file_txt)
    data = ds.ReadAsArray()
    gt = ds.GetGeoTransform()
    proj = ds.GetProjection()

    #################################################################################

    xres = gt[1]
    yres = gt[5]

    xmin = gt[0] + xres * 0.5
    xmax = gt[0] + (xres * ds.RasterXSize) - xres * 0.5
    # ymin = gt[3] + (yres * ds.RasterYSize) + yres * 0.5
    ymin = -90
    # ymax = gt[3] - yres * 0.5
    ymax=90

    x_center = (xmin + xmax) / 2
    y_center = (ymin + ymax) / 2
    #################################################################################

    fig = plt.figure(figsize=(18, 10))
    ax = fig.add_subplot(111, axisbg='w', frame_on=True)

    m = Basemap(llcrnrlon=xmin, llcrnrlat=ymin, urcrnrlon=xmax, urcrnrlat=ymax,
                projection='tmerc', lat_0=y_center, lon_0=x_center) #tmerc

    # parallels = np.arange(15., 30., 0.25)
    # m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=12, linewidth=0.4)
    #
    # meridians = np.arange(70., 90., 0.25)
    # m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=12, linewidth=0.4)

    x = linspace(0, m.urcrnrx, data.shape[1])
    y = linspace(0, m.urcrnry, data.shape[0])

    xx, yy = meshgrid(x, y)

    m.pcolormesh(xx, yy, data, cmap=plt.cm.jet)

    plt.show()
    # plt.savefig('Path\\To\\Save_Image.png', bbox_inches='tight', pad_inches=.2, dpi=600)


def genera_statistiche(vettori,raster):

    stats = zonal_stats(vettori,
                        raster,
                        geojson_out=True,
                        stats=['min', 'max', 'median', 'mean', 'range'],
                        copy_properties=True,
                        nodata_value="-999"
                        )

    for s in stats:
        print s['properties']['ADM2_CODE'], s['properties']['median'], s['properties']['mean']

nome_shp = "C:/sparc/input_data/countries/ethiopia.shp"
nome_tif = r"C:\meteorological\ecmwf\4_anomalies_3_minus_2\anm_GLOBAL_1626_8_19792015.tif"
current_TP = r"C:\meteorological\ecmwf\3_ecmwf_ftp_wfp\TP_08160826.tif"

# cumulated_means_10days("1_gribs_from_ecmwf/GLOBAL_1626_8_19792015.grib", "GLOBAL_", "1626", range(1979, 2015))

anomalie_annue_10gg_cumulate(current_TP)

# media_medie("C:/meteorological/ecmwf/5_tests/10_giorni/averaged/")
# media_cumulate("C:/meteorological/ecmwf/5_tests/10_giorni/cumulated/")

# genera_statistiche(nome_shp,nome_tif)
# genera_istogramma_valori(nome_tif)
