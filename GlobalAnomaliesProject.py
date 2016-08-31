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
from osgeo import osr
gdal.UseExceptions()
from osgeo import gdal, gdalnumeric
from osgeo.gdalconst import GA_ReadOnly
from ecmwfapi import ECMWFDataServer
server = ECMWFDataServer()

class GlobalAnomaliesProject(object):

    def __init__(self, anno_min=1979, anno_max=2016):

        self.DATE_DIR = "0_generated_date_files"
        self.GRIB_DIR = "1_gribs_from_ecmwf"
        self.MEAN_DIR = "2_mean_from_gribs"
        self.LAST_DIR = "3_ecmwf_ftp_wfp"
        self.ANOM_DIR = "4_anomalies_3_minus_2"
        self.GLOBAL_PREFIX = 'GLOBAL'
        self.LEAP_DAYS = 10

        self.starting_year = int(anno_min)
        self.ending_year = int(anno_max)
        self.years_range = range(self.starting_year, self.ending_year)
        self.starting_year = min(self.years_range)
        self.ending_year = max(self.years_range)
        self.adesso = datetime.datetime.now()
        self.starting_day = self.adesso.day
        self.starting_month = self.adesso.month
        self.current_year = self.adesso.year
        self.list_years_range = list(range(self.starting_year, self.current_year))
        self.initial_date = datetime.date(int(self.starting_year), int(self.starting_month), int(self.starting_day))
        self.leap_days_date_format = datetime.timedelta(days=self.LEAP_DAYS)
        self.final_date_date_format = self.initial_date + self.leap_days_date_format
        self.initial_day_date_formatted = '{:02d}'.format(self.initial_date.day)
        self.final_day_date_formatted = '{:02d}'.format(self.final_date_date_format.day)
        self.initial_month_date_formatted = '{:02d}'.format(self.initial_date.month)
        self.final_month_date_formatted = '{:02d}'.format(self.final_date_date_format.month)
        if len(str(self.starting_day)) < 2:
            self.date_string_initial = str(self.starting_month) + str('0' + (str(self.starting_day)))
            self.date_string_final = str(self.starting_month) + str(int(self.starting_day + self.LEAP_DAYS))
        else:
            self.date_string_initial = self.final_month_date_formatted + self.initial_day_date_formatted
            self.date_string_final = self.final_month_date_formatted + self.final_day_date_formatted

    def setYears(self, anno_minimo, anno_massimo):

        """Set the years for the calculation of the climatological mean.
            The years used if no minimum and aximum years are provided are
            1979 - 2015
        """
        self.starting_year = anno_minimo
        self.ending_year = anno_massimo

    def getYears(self):
        anno_minimo_calcolo = self.starting_year
        anno_massimo_calcolo = self.ending_year
        return anno_minimo_calcolo, anno_massimo_calcolo


class HistoricalTrend(GlobalAnomaliesProject):

    def __init__(self):
        super(HistoricalTrend, self).__init__()
        days_part = str(self.initial_day_date_formatted) + str(self.final_day_date_formatted)
        months_part = str(self.initial_month_date_formatted) + str(self.final_month_date_formatted)
        years_part = str(self.starting_year) + str(self.ending_year)
        self.date_file_path = self.DATE_DIR + '/' +\
                              "req_" + str(days_part) + \
                              "_" + str(months_part) + \
                              "_" + str(years_part) + ".txt"
        if os.path.isfile(self.date_file_path):
            print "File containing dates has already been generated"

        self.dates_part = self.date_file_path.split(".")[0].split("req")[1]
        self.tif_mean_file = self.MEAN_DIR + "/mean_" + self.GLOBAL_PREFIX + self.dates_part + ".tif"
        self.file_climate_path = self.tif_mean_file

    def parameters_gathering(self):

        mese_str = str(self.starting_month)
        if len(mese_str) == 1:
            mese_str = "0" + mese_str

    def check_dates_before_creating_file(self):

        self.lista_mese_giorno = []
        lista_giorni = []

        self.lista_mese_giorno.append(str(self.initial_month_date_formatted) + "-" + str(self.initial_day_date_formatted))
        lista_giorni.append(self.initial_day_date_formatted)
        for indice in range(1, self.LEAP_DAYS):
            range_date = datetime.timedelta(days=indice)
            giorni_successivi = self.initial_date + range_date
            self.lista_mese_giorno.append(
                '{:02d}'.format(giorni_successivi.month) + "-" + '{:02d}'.format(giorni_successivi.day))
            lista_giorni.append(giorni_successivi)

    def create_dates_txt_file(self):

        lista_finale = []
        for anno in self.years_range:
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

        date = open(self.date_file_path)
        time_frame_json = json.load(date)

        grib_file = self.GRIB_DIR + "/" + self.GLOBAL_PREFIX + self.dates_part + ".grib"
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
        banda_esempio = ecmfwf_file_asRaster.GetRasterBand(1)
        type_banda_esempio = banda_esempio.DataType

        if os.path.isfile(self.tif_mean_file):
            mean_bande_climatology = gdal.Open(self.tif_mean_file)
        else:
            banda_somma = np.zeros((y_size, x_size,), dtype=np.float64)
            for i in range(1, numero_bande):
                print "Processing band %d of %d" % (i,numero_bande)
                banda = ecmfwf_file_asRaster.GetRasterBand(i)
                data = gdalnumeric.BandReadAsArray(banda)
                banda_somma = banda_somma + data

            mean_bande_climatology = (banda_somma / numero_bande)

            driver = gdal.GetDriverByName("GTiff")
            raster_mean_from_bands = driver.Create(self.tif_mean_file, x_size, y_size, 1, type_banda_esempio)
            gdalnumeric.CopyDatasetInfo(ecmfwf_file_asRaster, raster_mean_from_bands)
            banda_dove_scrivere_raster_mean = raster_mean_from_bands.GetRasterBand(1)

            try:
                gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_mean,mean_bande_climatology)
                print "Mean raster exported in" + self.tif_mean_file + "\n"
            except IOError as err:
                return str(err.message) + + "\n"


class PresentConditions(GlobalAnomaliesProject):

    def __init__(self):
        super(PresentConditions, self).__init__()

        self.file_current_path = self.LAST_DIR + "/TP_" + self.date_string_initial + self.date_string_final
        self.extracted_total_precipitation = self.file_current_path + '.tif'
        self.lista_files_ECMWF = []

    def ftp_connection_files_gathering(self):

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

        data_iniziale = datetime.date(int(self.starting_year), int(self.starting_month), int(self.starting_day))

        # DA RIMUOVERE PASSATO FEBBRAIO
        salto_giorni = datetime.timedelta(days=self.LEAP_DAYS - 1)
        data_finale = data_iniziale + salto_giorni

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

        Array[np.isnan(Array)] = NDV

        DataSet = driver.Create(self.extracted_total_precipitation, xsize, ysize, 1, DataType)
        DataSet.SetGeoTransform(GeoT)
        DataSet.SetProjection(Projection.ExportToWkt())
        # Write the array
        DataSet.GetRasterBand(1).WriteArray(Array)
        if NDV:
            DataSet.GetRasterBand(1).SetNoDataValue(NDV)
        else:
            print "No Data None"

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
            for file_disponibile in self.lista_files_ECMWF:
                lista_ftp.append(file_disponibile)
                if self.date_string_initial and self.date_string_final in file_disponibile:
                    file_scelto = file_disponibile

            self.file_gribs_ftp_da_trasferire = self.LAST_DIR + "/" + file_scelto
            self.ftp_connection_files_retrieval(file_scelto)
            self.current_band = self.exctract_tp_band()


class AnomaliesCalculation(HistoricalTrend,PresentConditions):

    def __init__(self):
        super(AnomaliesCalculation, self).__init__()

        self.nome_tif_anomalie = "4_anomalies_3_minus_2/" + str(self.file_climate_path).split("/")[1].replace("mean", "anm")
        print self.nome_tif_anomalie

    def calculate_global_anomalies(self):

        climate_file = gdal.Open(self.file_climate_path)
        banda_climate = climate_file.GetRasterBand(1)

        current_file = gdal.Open(self.extracted_total_precipitation)
        x_size_curr = current_file.RasterXSize
        y_size_curr = current_file.RasterYSize
        banda_current = current_file.GetRasterBand(1)
        type_banda_esempio = banda_current.DataType

        data_current = gdalnumeric.BandReadAsArray(banda_current)
        data_climate = gdalnumeric.BandReadAsArray(banda_climate, xoff=0, yoff=72, win_xsize=2880, win_ysize=1297)
        banda_anomala = np.subtract(data_current, data_climate*10)

        # Write the out file
        driver = gdal.GetDriverByName("GTiff")
        raster_anomaly_from_bands = driver.Create(self.nome_tif_anomalie,
                                                  x_size_curr, y_size_curr, 1, type_banda_esempio)
        gdalnumeric.CopyDatasetInfo(current_file, raster_anomaly_from_bands)
        banda_dove_scrivere_raster_anomaly = raster_anomaly_from_bands.GetRasterBand(1)

        try:
            gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_anomaly, banda_anomala)
            return "Mean raster exported in" + self.nome_tif_anomalie + "\n"
        except IOError as err:
            return str(err.message) + "\n"


if __name__ == '__main__':

    # ### HISTORICAL TRENDS
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
    print anom_calc.file_current_path
    print anom_calc.file_climate_path
    anom_calc.calculate_global_anomalies()