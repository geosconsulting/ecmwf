from ecmwfapi import ECMWFDataServer
server = ECMWFDataServer()

import calculate_time_window_date


import json
import fiona
import numpy as np
from osgeo import gdal, gdalnumeric
import sys
gdal.UseExceptions()

def Usage():

    print("example run : $ python ecmwf_data_analysis.py country name")
    sys.exit(1)

def Shp_BBox(file_shp):

    ilVettore = fiona.open(file_shp)
    laProiezioneDelVettore = ilVettore.crs
    laBoundingBox = ilVettore.bounds

    return laProiezioneDelVettore, laBoundingBox

def fetch_ECMWF_ReForecast(file_output): # hdate and date and dict_area_richiesta

    # date = open(time_frame)
    # time_frame_json = json.load(date)
    #
    # north = round(float(dict_area_richiesta['ymax'])*2/2)
    # west = round(float(dict_area_richiesta['xmin'])*2/2)
    # south = round(float(dict_area_richiesta['ymin'])*2/2)
    # east = round(float(dict_area_richiesta['xmax'])*2/2)
    # area_ecmwf_bbox = str(north) + "/" + str(west) + "/" + str(south) + "/" + str(east)

    # request WFP ReForecast CALUM
    # server.retrieve({
    #     "number": "1/2/3/4/5/6/7/8/9/10",
    #     "time": "00:00:00",
    #     "date": "20160121",
    #     "stream": "enfh",
    #     "step": "432",
    #     "levtype": "sfc",
    #     "expver": "1",
    #     "class": "od",
    #     "type": "pf",
    #     "hdate": "19960121",
    #     "param": "228.128",
    #     "area": "40/-20/-40/60",
    #     "field": "pf1_total",
    #     "target": file_output
    # })

    # request WFP ReForecast Cristian-Pappemberger
    server.retrieve({
        'origin': "ecmf",
        # 'hdate': "2014-05-14", # ECMWF real-time examples before 14 May 2014
        'target': "frcst_46gg_21Mar_1.grib",
        'stream': "enfh",
        'levtype': "sfc",
        'expver': "prod",
        'dataset': "s2s",
        'padding': "0",
        'step': "0/to/1104/by/24",
        # 'step': "1104",
        'expect': "any",
        'time': "00",
        # 'date': "2015-05-14",
        'date': "2016-03-21",
        # 'param': "165",
        'param': "228",
        'type': "cfmars",
        'class': "s2",
    })

    #1. Re- forecasts: 1 param, 1 date
    #Retrieving  1 field (10m U wind) for all time steps and for the 14 May 2014
    # server.retrieve({
    #     "class": "s2",
    #     "dataset": "s2s",
    #     "date": "2015-12-03/2015-12-07/2015-12-10/2015-12-14/2015-12-17/2015-12-21/2015-12-24/2015-12-28/2015-12-31/2016-01-04/2016-01-07/2016-01-11/2016-01-14/2016-01-18",
    #     "expver": "prod",
    #     "levtype": "sfc",
    #     "origin": "ecmf",
    #     "param": "228228",
    #     "step": "0/to/1104/by/24",
    #     "stream": "enfo",
    #     "target": "reforecast_1_0.grib",
    #     "time": "00",
    #     "type": "cf",
    # })
    #
    # server.retrieve({
    #     "class": "s2",
    #     "dataset": "s2s",
    #     "hdate": "2014-05-14",
    #     "date": "2015-05-14",
    #     "expver": "prod",
    #     "levtype": "sfc",
    #     "origin": "ecmf",
    #     "param": "165",
    #     "step": "0/to/1104/by/24",
    #     "stream": "enfh",
    #     "target": "reforecast_1_1.grib",
    #     "time": "00",
    #     "number": "1/to/10",
    #     "type": "pf",
    # })

    #2. Re- forecasts used to calibrate a  real-time forecast:
    #Retrieving  1 param (10m U wind) for all time steps and used to calibrate the 14 May 2015 real-time forecast.
    # server.retrieve({
    #     "class": "s2",
    #     "dataset": "s2s",
    #     "hdate": "1995-05-14/1996-05-14/1997-05-14/1998-05-14/1999-05-14/2000-05-14/2001-05-14/2002-05-14/2003-05-14/2004-05-14/2005-05-14/2006-05-14/2007-05-14/2008-05-14/2009-05-14/2010-05-14/2011-05-14/2012-05-14/2013-05-14/2014-05-14",
    #     "date": "2015-05-14",
    #     "expver": "prod",
    #     "levtype": "sfc",
    #     "origin": "ecmf",
    #     "param": "165",
    #     "step": "0/to/1104/by/24",
    #     "stream": "enfh",
    #     "target": "reforecast_2_0.grib",
    #     "time": "00",
    #     "type": "cf",
    # })
    #
    # server.retrieve({
    #     "class": "s2",
    #     "dataset": "s2s",
    #     "hdate": "1995-05-14/1996-05-14/1997-05-14/1998-05-14/1999-04-14/2000-05-14/2001-05-14/2002-05-14/2003-05-14/2004-05-14/2005-05-14/2006-05-14/2007-05-14/2008-05-14/2009-05-14/2010-05-14/2011-05-14/2012-05-14/2013-05-14/2014-05-14",
    #     "date": "2015-05-14",
    #     "expver": "prod",
    #     "levtype": "sfc",
    #     "origin": "ecmf",
    #     "param": "165",
    #     "step": "0/to/1104/by/24",
    #     "stream": "enfh",
    #     "target": "reforecast_2_1",
    #     "number": "1/to/10",
    #     "time": "00",
    #     "type": "pf",
    # })

    # 1. Real-time forecasts: 1 param, 1 date
    # Retrieving one field (10 meter U wind here) for all time steps and  for the forecast starting on 1st January 2015:

    # server.retrieve({
    #     "class": "s2",
    #     "dataset": "s2s",
    #     "date": "2015-01-01",
    #     "expver": "prod",
    #     "levtype": "sfc",
    #     "origin": "ecmf",
    #     "param": "165",
    #     "step": "0/to/1104/by/24",
    #     "stream": "enfo",
    #     "target": "realtime_1_0.grib",
    #     "time": "00",
    #     "type": "cf",
    # })
    #
    # server.retrieve({
    #     "class": "s2",
    #     "dataset": "s2s",
    #     "date": "2015-01-01",
    #     "expver": "prod",
    #     "levtype": "sfc",
    #     "origin": "ecmf",
    #     "param": "165",
    #     "step": "0/to/1104/by/24",
    #     "stream": "enfo",
    #     "target": "realtime_1_1.grib",
    #     "time": "00",
    #     "number": "1/to/50",
    #     "type": "pf",
    # })

    #2. Real-time forecasts: 1 param, series of dates
    #Retrieving  1 field (10m U wind) for all time steps and for the whole January 2015.

    # server.retrieve({
    #     "class": "s2",
    #     "dataset": "s2s",
    #     "date": "2015-01-01/2015-01-05/2015-01-08/2015-01-12/2015-01-15/2015-01-19/2015-01-22/2015-01-26/2015-01-29",
    #     "expver": "prod",
    #     "levtype": "sfc",
    #     "origin": "ecmf",
    #     "param": "165",
    #     "step": "0/to/1104/by/24",
    #     "stream": "enfo",
    #     "target": "realtime_2_0.grib",
    #     "time": "00",
    #     "type": "cf",
    # })
    #
    # server.retrieve({
    #     "class": "s2",
    #     "dataset": "s2s",
    #     "date": "2015-01-01/2015-01-05/2015-01-08/2015-01-12/2015-01-15/2015-01-19/2015-01-22/2015-01-26/2015-01-29",
    #     "expver": "prod",
    #     "levtype": "sfc",
    #     "origin": "ecmf",
    #     "param": "165",
    #     "step": "0/to/1104/by/24",
    #     "stream": "enfo",
    #     "target": "realtime_2_1.grib",
    #     "time": "00",
    #     "number": "1/to/50",
    #     "type": "pf",
    # })
    #
    # server.retrieve({
    #     "class": "s2",
    #     "dataset": "s2s",
    #     "date": "2015-11-02/2015-11-05/2015-11-09/2015-11-12/2015-11-16/2015-11-19/2015-11-23/2015-11-26/2015-11-30/2015-12-03/2015-12-07/2015-12-10/2015-12-14/2015-12-17/2015-12-21/2015-12-24/2015-12-28/2015-12-31/2016-01-04/2016-01-07/2016-01-11/2016-01-14/2016-01-18",
    #     "expver": "prod",
    #     "levtype": "sfc",
    #     "origin": "ecmf",
    #     "param": "43/121/122/134/146/147/151/165/166/169/172/175/176/177/179/180/181/174008/228002/228143/228144/228205/228228",
    #     "step": "0/to/1104/by/24",
    #     "stream": "enfo",
    #     "target": "realtime_1_0_all.grib",
    #     "time": "00",
    #     "type": "cf",
    # })

    # server.retrieve({
    #     "class": "s2",
    #     "dataset": "s2s",
    #     "date": "2015-01-01",
    #     "expver": "prod",
    #     "levtype": "sfc",
    #     "origin": "ecmf",
    #     "param": "165",
    #     "step": "0/to/1104/by/24",
    #     "stream": "enfo",
    #     "target": "realtime_1_0_wind.grib",
    #     "time": "00",
    #     "type": "cf",
    # })
    #
    # server.retrieve({
    #     "class": "s2",
    #     "dataset": "s2s",
    #     "date": "2015-01-01",
    #     "expver": "prod",
    #     "levtype": "sfc",
    #     "origin": "ecmf",
    #     "param": "228",
    #     "step": "0/to/1104/by/24",
    #     "stream": "enfo",
    #     "target": "realtime_1_0_prec.grib",
    #     "time": "00",
    #     "type": "cf",
    # })


def genera_statistiche_banda_grib(banda, indice):

    print
    print "DATA FOR BAND", indice
    stats = banda.GetStatistics(True, True)
    if stats is None:
        pass

    print "Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % (stats[0], stats[1], stats[2], stats[3])
    print "NO DATA VALUE = ", banda.GetNoDataValue()
    print "MIN = ", banda.GetMinimum()
    print "MAX = ", banda.GetMaximum()
    print "SCALE = ", banda.GetScale()
    print "UNIT TYPE = ", banda.GetUnitType()


# if __name__ == '__main__':

    # if len(sys.argv) < 1:
    #     Usage()
    #     sys.exit(1)
    #
    # vector_file = "c:/sparc/input_data/countries/" + sys.argv[1] + ".shp"
    # paese = vector_file.split(".")[0].split("/")[-1]

    # ritornato = calculate_time_window_date.scateniamo_l_inferno(paese)
    # parte_date = ritornato.split("/")[1].split(".")[0][4:]
    # tre_lettere = vector_file.split(".")[0].split("/")[-1][0:3]
    # raster_file = "gribs/historical/" + tre_lettere + parte_date + ".grib"
    # print raster_file
    #
    # if os.path.isfile(raster_file):
    #     print "grib esiste"
    #     genera_means(raster_file)
    # else:
    #     print "grib non esiste"
    #     genera_gribs(ritornato, vector_file, raster_file)
    #     genera_means(raster_file)
    #

dict = {'ymax': '15', 'xmin': '-90','ymin': '-20', 'xmax': '-65'}

# fetch_ECMWF_data("c:/temp/tt1.grib",'dates/req_0817_12_19732012.txt',dict)

# fetch_ECMWF_data("gribs/probabilities/prob_test.grib", "dates/req_20131205.txt", dict)

fetch_ECMWF_ReForecast("realtime_reforecast/ref_test.grib")

