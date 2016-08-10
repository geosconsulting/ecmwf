#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

import datetime
import os
import sys
import json
import numpy as np
import gdal
from ftplib import FTP
gdal.UseExceptions()
from osgeo import osr

gdal.UseExceptions()
from osgeo import gdal, gdalnumeric
from osgeo.gdalconst import GA_ReadOnly

from ecmwfapi import ECMWFDataServer
server = ECMWFDataServer()

class GlobalAnomaliesProject(object):

    def __init__(self,anno_min=1979,anno_max=2015):

        self.anno_minimo = int(anno_min)
        self.anno_massimo = int(anno_max)

        self.DATE_DIR = "0_generated_date_files"
        self.GRIB_DIR = "1_gribs_from_ecmwf"
        self.MEAN_DIR = "2_mean_from_gribs"
        self.LAST_DIR = "3_ecmwf_ftp_wfp"
        self.ANOM_DIR = "4_anomalies_3_minus_2"
        self.GLOBAL_PREFIX = 'GLOBAL'

        self.range_anni = range(self.anno_minimo, self.anno_massimo)
        self.adesso = datetime.datetime.now()
        self.giorno_inizio = self.adesso.day
        self.mese_inizio = self.adesso.month
        self.in_che_anno_siamo = self.adesso.year
        self.lista_anni_correnti = list(range(self.anno_minimo, self.in_che_anno_siamo))
        self.SALTO = 10
        self.giorno_fine = self.giorno_inizio + self.SALTO

    def setYears(self, anno_minimo, anno_massimo):

        """Set the years for the calculation of the climatological mean.
            The years used if no minimum and aximum years are provided are
            1979 - 2015
        """
        self.anno_minimo = anno_minimo
        self.anno_massimo = anno_massimo

    def getYears(self):
        anno_minimo_calcolo = self.anno_minimo
        anno_massimo_calcolo = self.anno_massimo
        return anno_minimo_calcolo, anno_massimo_calcolo

    def check_files(self):

        self.file_climate_path = r'C:/meteorological/ecmwf/2_mean_from_gribs/mean_GLOBAL_1019_08_19792015.tif'
        self.current_file_path = r'C:/meteorological/ecmwf/3_ecmwf_ftp_wfp/TP_08100819.tif'


class HistoricalTrend(GlobalAnomaliesProject):

    def __init__(self):
        super(HistoricalTrend, self).__init__()

    def parameters_gathering(self):

        anno_minimo = int(self.anno_minimo)
        anno_massimo = int(int(self.anno_massimo))
        self.lista_anni = range(anno_minimo, anno_massimo + 1)
        numero_anni = anno_massimo - anno_minimo
        mese = self.mese_inizio
        mese_str = str(self.mese_inizio)
        if len(mese_str) == 1:
            mese_str = "0" + mese_str
        giorno_inizio = self.giorno_inizio
        giorno_fine = giorno_inizio + self.SALTO

    def check_dates_before_creating_file(self):

        self.lista_mese_giorno = []
        lista_giorni = []
        data_iniziale = datetime.date(int(self.anno_minimo), int(self.mese_inizio), int(self.giorno_inizio))

        salto_giorni = datetime.timedelta(days=self.SALTO + 1)
        data_finale = data_iniziale + salto_giorni

        giorno_data_iniziale = '{:02d}'.format(data_iniziale.day)
        giorno_data_finale = '{:02d}'.format(data_finale.day)
        mese_data_inziale = '{:02d}'.format(data_iniziale.month)
        mese_data_finale = '{:02d}'.format(data_finale.month)

        self.lista_mese_giorno.append(str(mese_data_inziale) + "-" + str(giorno_data_iniziale))
        lista_giorni.append(giorno_data_iniziale)
        for indice in range(1, self.SALTO):
            range_date = datetime.timedelta(days=indice)
            giorni_successivi = data_iniziale + range_date
            self.lista_mese_giorno.append(
                '{:02d}'.format(giorni_successivi.month) + "-" + '{:02d}'.format(giorni_successivi.day))
            lista_giorni.append(giorni_successivi)

    def create_dates_txt_file(self):

        lista_finale = []
        for anno in self.lista_anni:
            for giorno in self.lista_mese_giorno:
                lista_finale.append(str(anno) + "-" + str(giorno))

        imesi = [i.split('-', 1)[0] for i in self.lista_mese_giorno]
        mese_minimo = min(imesi)
        mese_massimo = max(imesi)
        if mese_minimo == mese_massimo:
            igiorni = [i.split('-', 1)[1] for i in self.lista_mese_giorno]
            giorno_minimo = min(igiorni)
            giorno_massimo = max(igiorni)
            mese = mese_minimo
        else:
            igiorni_a = [i.split(str(mese_massimo), 1)[0] for i in self.lista_mese_giorno]
            solo_valori_igiorni_prima = filter(None, [i.split('-', 0)[0] for i in igiorni_a])
            igiorni_prima = [i.split('-', 1)[1] for i in solo_valori_igiorni_prima]
            igiorni_b = [i.split(str(mese_minimo), 1)[0] for i in self.lista_mese_giorno]
            solo_valori_igiorni_dopo = filter(None, [i.split('-', 0)[0] for i in igiorni_b])
            igiorni_dopo = [i.split('-', 1)[1] for i in solo_valori_igiorni_dopo]
            giorno_minimo_a = min(igiorni_prima)
            giorno_massimo_b = max(igiorni_dopo)
            giorno_minimo = giorno_minimo_a
            giorno_massimo = giorno_massimo_b
            mese = str(mese_minimo) + "_" + str(mese_massimo)

        anno_minimo = min(self.lista_anni)
        anno_massimo = max(self.lista_anni)

        prima_parte = str(giorno_minimo) + str(giorno_massimo)
        seconda_parte = str(anno_minimo) + str(anno_massimo)
        self.date_file_path = '0_generated_date_files/' + "req_" + str(prima_parte) + "_" + str(mese) + "_" + str(
            seconda_parte) + ".txt"
        if os.path.isfile(self.date_file_path):
            print "File containing dates has already been generated"

        nuovo = open(self.date_file_path, mode='w')
        nuovo.write('"')
        lunghezza_lista = len(lista_finale)
        contatore = 1

        for illo in sorted(lista_finale):
            contatore += 1
            if contatore <= lunghezza_lista:
                nuovo.write(illo + "/")
            else:
                nuovo.write(illo)
        nuovo.write('"')
        nuovo.close()

    def mean_from_historical_forecasts(self):

        parte_date = self.date_file_path.split(".")[0].split("req")[1]

        date = open(self.date_file_path)
        time_frame_json = json.load(date)

        grib_file = "1_gribs_from_ecmwf/" + self.GLOBAL_PREFIX + parte_date + ".grib"
        if os.path.isfile(grib_file):
            fileSize = os.path.getsize(grib_file)
            print "File is %d" % fileSize
            ecmfwf_file_asRaster = gdal.Open(grib_file)
        else:
            server.retrieve({
                "class": "ei",
                "dataset": "interim",
                "date": time_frame_json,
                "expver": "1",
                "grid": "0.125/0.125",
                "levtype": "sfc",
                "param": "228.128",
                "step": "24",
                "stream": "oper",
                "target": grib_file,
                "time": "12",
                "type": "fc",
            })
            ecmfwf_file_asRaster = gdal.Open(grib_file)

        x_size = ecmfwf_file_asRaster.RasterXSize
        y_size = ecmfwf_file_asRaster.RasterYSize
        numero_bande = ecmfwf_file_asRaster.RasterCount

        print "Number of bands %d " % numero_bande
        banda_esempio = ecmfwf_file_asRaster.GetRasterBand(1)
        type_banda_esempio = banda_esempio.DataType

        tif_mean_file = "2_mean_from_gribs/mean_" + self.GLOBAL_PREFIX + parte_date + ".tif"
        if os.path.isfile(tif_mean_file):
            mean_bande_climatology = gdal.Open(tif_mean_file)
        else:
            banda_somma = np.zeros((y_size, x_size,), dtype=np.float64)
            for i in range(1, numero_bande):
                print "Processing band %d of %d" % (i,numero_bande)
                banda = ecmfwf_file_asRaster.GetRasterBand(i)
                data = gdalnumeric.BandReadAsArray(banda)
                banda_somma = banda_somma + data

            mean_bande_climatology = (banda_somma / numero_bande)

            # Write the out file
            driver = gdal.GetDriverByName("GTiff")
            raster_mean_from_bands = driver.Create(tif_mean_file, x_size, y_size, 1, type_banda_esempio)
            gdalnumeric.CopyDatasetInfo(ecmfwf_file_asRaster, raster_mean_from_bands)
            banda_dove_scrivere_raster_mean = raster_mean_from_bands.GetRasterBand(1)

            try:
                gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_mean,mean_bande_climatology)
                print "Mean raster exported in" + tif_mean_file + "\n"
            except IOError as err:
                return str(err.message) + + "\n"

        self.file_climate_path = tif_mean_file

class PresentConditions(GlobalAnomaliesProject):

    def __init__(self):
        super(PresentConditions, self).__init__()

    def ftp_connection_files_gathering(self):

        self.lista_files_ECMWF = []

        try:
            ftp = FTP('ftp.wfp.org')
            ftp.login('WFP_GISviewer', 'FTPviewer')
            messaggioServerFTP = str(ftp.getwelcome()) + "\n"
        except:
            pass

        for file in ftp.nlst():
            filename, file_extension = os.path.splitext(file)
            if file_extension == '' and len(file) == 20:
                self.lista_files_ECMWF.append(filename)
        ftp.close()

        print messaggioServerFTP

    def ftp_connection_files_retrieval(self, nomefile):

        try:
            ftp = FTP('ftp.wfp.org')
            ftp.login('WFP_GISviewer', 'FTPviewer')
            messaggioServerFTP = str(ftp.getwelcome()) + "\n"
            print messaggioServerFTP
        except:
            pass

        gFile = open(self.LAST_DIR + "/" + nomefile, "wb")
        ftp.retrbinary("RETR " + nomefile, gFile.write)
        gFile.close()
        ftp.quit

    def check_dates_wfp_ftp(self):

        data_iniziale = datetime.date(int(self.anno_minimo), int(self.mese_inizio), int(self.giorno_inizio))

        # DA RIMUOVERE PASSATO FEBBRAIO
        salto_giorni = datetime.timedelta(days=self.SALTO - 1)
        data_finale = data_iniziale + salto_giorni

        self.giorno_data_iniziale = '{:02d}'.format(data_iniziale.day)
        self.giorno_data_finale = '{:02d}'.format(data_finale.day)
        self.mese_data_inziale = '{:02d}'.format(data_iniziale.month)
        self.mese_data_finale = '{:02d}'.format(data_finale.month)

    def get_geo_info(self, filename):

        SourceDS = gdal.Open(filename, GA_ReadOnly)
        NDV = SourceDS.GetRasterBand(1).GetNoDataValue()
        xsize = SourceDS.RasterXSize
        ysize = SourceDS.RasterYSize
        GeoT = SourceDS.GetGeoTransform()
        Projection = osr.SpatialReference()
        Projection.ImportFromWkt(SourceDS.GetProjectionRef())
        DataType = SourceDS.GetRasterBand(1).DataType
        DataTypeName = gdal.GetDataTypeName(DataType)

        NunBandsInGRIB = SourceDS.RasterCount

        for numero_banda in range(1, NunBandsInGRIB + 1):
            TPBand = SourceDS.GetRasterBand(numero_banda)
            metadati = TPBand.GetMetadata()
            if (metadati['GRIB_ELEMENT'] == 'TP'):
                DataTypeTPInt = TPBand.DataType
                DataTypeTP = gdal.GetDataTypeName(DataTypeTPInt)
                DataTP = TPBand.ReadAsArray()
                break

        return NDV, xsize, ysize, GeoT, Projection, DataType, DataTypeTP, TPBand, DataTP, DataTypeTPInt

    def create_geo_tiff_from_selected_band(self, Array, driver, NDV, xsize, ysize, GeoT, Projection, DataType):

        if DataType == 'Float32':
            DataType = gdal.GDT_Float32
        elif DataType == 'Float64':
            DataType == gdal.GDT_Float64

        extracted_total_precipitation = self.nome_file_estratto_TotalPrecipitation + '.tif'

        Array[np.isnan(Array)] = NDV

        DataSet = driver.Create(extracted_total_precipitation, xsize, ysize, 1, DataType)
        DataSet.SetGeoTransform(GeoT)
        DataSet.SetProjection(Projection.ExportToWkt())
        # Write the array
        DataSet.GetRasterBand(1).WriteArray(Array)
        if NDV:
            DataSet.GetRasterBand(1).SetNoDataValue(NDV)
        else:
            print "No Data None"

        return extracted_total_precipitation

    def exctract_tp_band(self):

        DataSet = gdal.Open(self.file_gribs_ftp_da_trasferire, GA_ReadOnly)
        Band = DataSet.GetRasterBand(1)
        Array = Band.ReadAsArray()
        NDV = Band.GetNoDataValue()
        NDV, xsize, ysize, GeoT, Projection, DataType, \
        DataTypeTP, TPBand, DataTP, DataTypeTPInt = self.get_geo_info(self.file_gribs_ftp_da_trasferire)

        driver = gdal.GetDriverByName('GTiff')

        extracted_total_precipitation_tif = self.create_geo_tiff_from_selected_band(DataTP, driver,
                                                                                NDV, xsize, ysize, GeoT,
                                                                                Projection, DataTypeTPInt)

        return extracted_total_precipitation_tif

    def extract_precipitation_from_last_forecast(self):

        if len(self.lista_files_ECMWF) > 0:
            lista_ftp = []

            if len(str(self.giorno_inizio)) < 2:
                stringa1 = str(self.mese_inizio) + str('0' + (str(self.giorno_inizio)))
                stringa2 = str(self.mese_inizio) + str(int(self.giorno_inizio + self.SALTO))
            else:

                stringa1 = self.mese_data_inziale + self.giorno_data_iniziale
                stringa2 = self.mese_data_finale + self.giorno_data_finale

            for file_disponibile in self.lista_files_ECMWF:
                lista_ftp.append(file_disponibile)
                if stringa1 and stringa2 in file_disponibile:
                    file_scelto = file_disponibile

            self.file_gribs_ftp_da_trasferire = self.LAST_DIR + "/" + file_scelto
            self.nome_file_estratto_TotalPrecipitation = self.LAST_DIR + "/TP_" + stringa1 + stringa2
            self.ftp_connection_files_retrieval(file_scelto)
            self.current_band = self.exctract_tp_band()

class AnomaliesCalculation(HistoricalTrend,PresentConditions):

    def __init__(self):
        super(AnomaliesCalculation, self).__init__()
        super(AnomaliesCalculation, self).__init__()

    def calculate_global_anomalies(self):

        climate_file = gdal.Open(self.file_climate_path)
        x_size_clim = climate_file.RasterXSize
        y_size_clim = climate_file.RasterYSize
        print "Size of climate raster X=%0.2f Y=%0.2f" % (x_size_clim, y_size_clim)

        geotransform_climate = climate_file.GetGeoTransform()
        originX_clim = geotransform_climate[0]
        originY_clim = geotransform_climate[3]
        pixelWidth_clim = geotransform_climate[1]
        pixelHeight_clim = geotransform_climate[5]
        print "Origin of climate file X=%0.2f Y=%0.2f" % (originX_clim, originY_clim)
        print "Size of pixel for climate raster Width=%0.2f and Height=%0.2f" % (pixelWidth_clim, pixelHeight_clim)

        banda_climate = climate_file.GetRasterBand(1)
        print "Tipo dato file climate %s" % banda_climate.DataType

        current_file = gdal.Open(self.nome_file_estratto_TotalPrecipitation)
        x_size_curr = current_file.RasterXSize
        y_size_curr = current_file.RasterYSize
        print
        print "Size of current raster X=%0.2f Y=%0.2f" % (x_size_curr, y_size_curr)

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

        nome_tif_anomalie = "4_anomalies_3_minus_2/" + str(self.file_climate_path).split("/")[4].replace("mean", "anm")

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

if __name__ == '__main__':

    ### HISTORICAL TRENDS
    hist_trends = HistoricalTrend()
    num_par = len(sys.argv)
    if num_par > 1:
        hist_trends.setYears(sys.argv[1], sys.argv[2])
    parametri_date = hist_trends.parameters_gathering()
    date_verificate = hist_trends.check_dates_before_creating_file()
    hist_trends.create_dates_txt_file()
    climate_mean = hist_trends.mean_from_historical_forecasts()
    print climate_mean

    ### PRESENT CONDITIONS
    pres_conds = PresentConditions()
    if num_par > 1:
        pres_conds.setYears(sys.argv[1], sys.argv[2])
    pres_conds.ftp_connection_files_gathering()
    pres_conds.check_dates_wfp_ftp()
    pres_conds.extract_precipitation_from_last_forecast()

    ### ANOMALIES
    anom_calc = AnomaliesCalculation()
    if num_par > 1:
        anom_calc.setYears(sys.argv[1], sys.argv[2])
    anom_calc.calculate_global_anomalies()