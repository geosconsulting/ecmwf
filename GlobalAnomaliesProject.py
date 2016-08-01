#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

import datetime
import os
import sys
import json
from ftplib import FTP
import numpy as np

import gdal
from osgeo.gdalconst import GA_ReadOnly
from ftplib import FTP
gdal.UseExceptions()
import gdal
from gdalconst import *
from osgeo import osr
import fiona
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
        self.GRIBS_DIR = "1_gribs_from_ecmwf"
        self.MEAN_DIR = "2_mean_from_gribs"
        self.LAST_DIR = "3_ecmwf_ftp_wfp"
        self.ANOM_DIR = "4_anomalies_3_minus_2"

        self.range_anni = range(self.anno_minimo, self.anno_massimo)
        self.adesso = datetime.datetime.now()
        self.giorno_inizio = self.adesso.day
        self.mese_inizio = self.adesso.month
        self.in_che_anno_siamo = self.adesso.year
        self.lista_anni_correnti = list(range(self.anno_minimo, self.in_che_anno_siamo))
        self.SALTO = 10

    def setYears(self, anno_minimo, anno_massimo):
        self.anno_minimo = anno_minimo
        self.anno_massimo = anno_massimo

    def getYears(self):
        anno_minimo_calcolo = self.anno_minimo
        anno_massimo_calcolo = self.anno_massimo
        return anno_minimo_calcolo, anno_massimo_calcolo


class HistoricalTrend(GlobalAnomaliesProject):

    def __init__(self):
        super(HistoricalTrend, self).__init__()

    def raccolta_parametri(self):

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

    def controlla_date(self): #,anno_inizio, mese_inizio, giorno_inizio, salto

        self.lista_mese_giorno = []
        lista_giorni = []
        data_iniziale = datetime.date(int(self.anno_minimo), int(self.mese_inizio), int(self.giorno_inizio))

        salto_giorni = datetime.timedelta(days=self.SALTO + 1)
        data_finale = data_iniziale + salto_giorni

        # MENO LEGGIBILE
        # lista_giorni_comprehension = [data_iniziale + salto_giorni for x in range(0, 8)]
        # print lista_giorni

        # PANDAS NON RIDUCE LA COMPLESSITA
        # datelist = pd.date_range(pd.datetime(int(anno_inizio), int(mese_inizio), int(giorno_inizio)), periods=8).tolist()

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

    def crea_file(self):

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
            print "FILE DATES ESISTENTE"

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

        parte_iso = 'GLOBAL'
        parte_date = self.date_file_path.split(".")[0].split("req")[1]

        date = open(self.date_file_path)
        time_frame_json = json.load(date)

        grib_file = "1_gribs_from_ecmwf/" + parte_iso + parte_date + ".grib"

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


        tif_mean_file = "2_mean_from_gribs/mean_" + parte_iso + parte_date + ".tif"

        ecmfwf_file_asRaster = gdal.Open(grib_file)
        x_size = ecmfwf_file_asRaster.RasterXSize
        y_size = ecmfwf_file_asRaster.RasterYSize
        numero_bande = ecmfwf_file_asRaster.RasterCount

        # print "Ci sono %d bande " % numero_bande
        banda_esempio = ecmfwf_file_asRaster.GetRasterBand(1)
        type_banda_esempio = banda_esempio.DataType

        banda_somma = np.zeros((y_size, x_size,), dtype=np.float64)
        for i in range(1, numero_bande):
            banda = ecmfwf_file_asRaster.GetRasterBand(i)
            # NON MI SERVE IN QUESTA FASE MA E' UTILE IN PROSPETTIVA
            # genera_statistiche_banda_grib(banda, i)
            data = gdalnumeric.BandReadAsArray(banda)
            banda_somma = banda_somma + data

        # mean_bande_in_mm = (banda_somma/numero_bande)*1000
        # CONFRONTANDO FORECAST CON FORECAST NON HO BISOGNO DI AVERLO IN MILLIMETRI LASCIO TUTTO IN METRI
        mean_bande_in_mm = (banda_somma / numero_bande)

        # Write the out file
        driver = gdal.GetDriverByName("GTiff")
        raster_mean_from_bands = driver.Create(tif_mean_file, x_size, y_size, 1, type_banda_esempio)
        gdalnumeric.CopyDatasetInfo(ecmfwf_file_asRaster, raster_mean_from_bands)
        banda_dove_scrivere_raster_mean = raster_mean_from_bands.GetRasterBand(1)

        try:
            gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_mean, mean_bande_in_mm)
            return "Mean raster exported in" + tif_mean_file + "\n"
        except IOError as err:
            return str(err.message) + + "\n"


class PresentConditions(GlobalAnomaliesProject):

    def __init__(self):
        super(PresentConditions, self).__init__()

    def FtpConnectionFilesGathering(self):

        self.lista_files_ECMWF = []

        try:
            ftp = FTP('ftp.wfp.org')
            ftp.login('WFP_GISviewer', 'FTPviewer')
            messaggioServerFTP = str(ftp.getwelcome()) + "\n"
        except:
            pass

        # lista_files = ftp.retrlines('LIST')
        # lista_files = ftp.dir()
        for file in ftp.nlst():
            filename, file_extension = os.path.splitext(file)
            if file_extension == '' and len(file) == 20:
                self.lista_files_ECMWF.append(filename)
        ftp.close()

        print messaggioServerFTP

    def FtpConnectionFilesRetrieval(self, nomefile):

        try:
            ftp = FTP('ftp.wfp.org')
            ftp.login('WFP_GISviewer', 'FTPviewer')
            messaggioServerFTP = str(ftp.getwelcome()) + "\n"
        except:
            pass

        gFile = open(self.LAST_DIR + "/" + nomefile, "wb")
        ftp.retrbinary("RETR " + nomefile, gFile.write)
        gFile.close()
        ftp.quit

    def controlla_date_ftp(self): #,anno_inizio, mese_inizio, giorno_inizio, salto

        data_iniziale = datetime.date(int(self.anno_minimo), int(self.mese_inizio), int(self.giorno_inizio))

        # DA RIMUOVERE PASSATO FEBBRAIO
        salto_giorni = datetime.timedelta(days=self.SALTO - 1)
        data_finale = data_iniziale + salto_giorni

        self.giorno_data_iniziale = '{:02d}'.format(data_iniziale.day)
        self.giorno_data_finale = '{:02d}'.format(data_finale.day)
        self.mese_data_inziale = '{:02d}'.format(data_iniziale.month)
        self.mese_data_finale = '{:02d}'.format(data_finale.month)

        # return giorno_data_iniziale, mese_data_inziale, giorno_data_finale, mese_data_finale

    def GetGeoInfo(self,filename):

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

    # Function to write a new file.
    def CreateGeoTiffFromSelectedBand(self, Array, driver, NDV, xsize, ysize, GeoT, Projection, DataType):

        if DataType == 'Float32':
            DataType = gdal.GDT_Float32
        elif DataType == 'Float64':
            DataType == gdal.GDT_Float64

        NewFileName = self.nome_file_estratto_TotalPrecipitation + '.tif'
        # Set nans to the original No Data Value
        Array[np.isnan(Array)] = NDV
        # Set up the dataset
        DataSet = driver.Create(NewFileName, xsize, ysize, 1, DataType)
        DataSet.SetGeoTransform(GeoT)
        DataSet.SetProjection(Projection.ExportToWkt())
        # Write the array
        DataSet.GetRasterBand(1).WriteArray(Array)
        if NDV:
            DataSet.GetRasterBand(1).SetNoDataValue(NDV)
        else:
            print "No Data None"

        return NewFileName

    def EstrazioneBandaTP_hres(self):

        DataSet = gdal.Open(self.file_gribs_ftp_da_trasferire, GA_ReadOnly)
        Band = DataSet.GetRasterBand(1)
        Array = Band.ReadAsArray()
        NDV = Band.GetNoDataValue()
        NDV, xsize, ysize, GeoT, Projection, DataType, DataTypeTP, TPBand, DataTP, DataTypeTPInt = self.GetGeoInfo(self.file_gribs_ftp_da_trasferire)

        driver = gdal.GetDriverByName('GTiff')

        self.CreateGeoTiffFromSelectedBand(DataTP, driver, NDV, xsize, ysize, GeoT, Projection, DataTypeTPInt)

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

            # extract_total_precipitation_hres.FtpConnectionFilesRetrieval(ecmwf_dir, file_scelto)
            # extract_total_precipitation_hres.EstrazioneBandaTP_hres(file_ftp, nome_file_estratto_TP)
            self.FtpConnectionFilesRetrieval(file_scelto)
            self.EstrazioneBandaTP_hres()


class AnomaliesCalculation(GlobalAnomaliesProject):

    def __init__(self):
        super(AnomaliesCalculation, self).__init__()

if __name__=="__main__":

    ### HISTORICAL TRENDS
    # hist_trends = HistoricalTrend()
    # # hist_trends.setYears(sys.argv[1], sys.argv[2])
    # parametri_date = hist_trends.raccolta_parametri()
    # date_verificate = hist_trends.controlla_date()
    # hist_trends.crea_file()
    # hist_trends.mean_from_historical_forecasts()

    ### PRESENT CONDITIONS
    pres_conds = PresentConditions()
    # pres_conds.setYears(sys.argv[1], sys.argv[2])
    pres_conds.FtpConnectionFilesGathering()
    pres_conds.controlla_date_ftp()
    pres_conds.extract_precipitation_from_last_forecast()

    # anom_calc = AnomaliesCalculation().setYears(sys.argv[1], sys.argv[2])

