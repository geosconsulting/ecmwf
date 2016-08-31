#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

from Tkinter import *
import tkMessageBox
import ttk
import psycopg2
import datetime
import os

import calculate_time_window_date
import ecmwf_data_analysis
import extract_total_precipitation_hres
import wfp_data_analysis_anomalies_r1

class AppECMWF:

    def __init__(self, finestra):
        
        # self.host = "10.11.40.84"
        self.host = "localhost"

        self.dbname = "geonode-imports"
        self.user = "geonode"
        self.password = "geonode"

        self.now = datetime.datetime.now()
        self.anno_inizio = self.now.year
        self.mese_inizio = self.now.month
        self.giorno_inizio = self.now.day

        #Define our connection string
        try:
            connection_string = "host=%s dbname=%s user=%s password=%s" % (self.host,
                                                                           self.dbname,
                                                                           self.user,
                                                                           self.password)
            self.conn = psycopg2.connect(connection_string)
        except Exception as e:
            print e.message

        self.cur = self.conn.cursor()

        def all_country_db():

            self.cur = self.conn.cursor()
            comando = "SELECT DISTINCT adm0_name FROM sparc_gaul_wfp_iso;"

            try:
                self.cur.execute(comando)
            except psycopg2.ProgrammingError as laTabellaNonEsiste:
                descrizione_errore = laTabellaNonEsiste.pgerror
                codice_errore = laTabellaNonEsiste.pgcode
                print descrizione_errore, codice_errore
                return codice_errore

            paesi = []
            for paese in self.cur:
                paesi.append(paese[0])
            return sorted(paesi)

        self.lista_paesi = all_country_db()
        self.parte_3lettere_per_file_grib = []

        finestra.geometry("610x390+30+30")

        self.area_messaggi = Text(finestra, background="black", foreground="green")
        self.area_messaggi.place(x=18, y=30, width=425, height=350)

        self.scr = Scrollbar(finestra, command=self.area_messaggi.yview)
        self.scr.place(x=8, y=30, width=10, height=215)
        self.area_messaggi.config(yscrollcommand=self.scr.set)

        self.box_value_adm0 = StringVar()
        self.box_adm0 = ttk.Combobox(finestra, textvariable=self.box_value_adm0)
        self.box_adm0['values'] = self.lista_paesi
        self.box_adm0.current(0)
        self.box_adm0.place(x=10, y=2, width=200, height=25)

        self.listbox = Listbox(finestra)
        self.listbox.place(x=450, y=170, width=155, height=175)

        self.button_add_countries = Button(finestra, text="Add Country", fg="blue",
                                           command=self.aggiungi_paese_alla_lista_di_processo)
        self.button_add_countries.place(x=210, y=3, width=80, height=25)

        self.button_add_countries = Button(finestra, text="Delete Country", fg="blue",
                                           command=lambda lb=self.listbox: self.listbox.delete(ANCHOR))
        self.button_add_countries.place(x=290, y=3, width=90, height=25)

        def attiva_disattiva():

            attivo_nonAttivo = self.global_mean.get()
            if attivo_nonAttivo == 0:
                self.box_adm0.config(state='normal')
                self.button_add_countries.config(state='normal')
            else:
                self.box_adm0.config(state='disabled')
                self.button_add_countries.config(state='disabled')

        self.button_latest_forecasts = Button(finestra, text="Calculate Mean",
                                              fg="blue",
                                              command=self.calcola_mean_from_historical_forecasts)
        self.button_latest_forecasts.place(x=400, y=3, width=100, height=25)

        self.button_avg_forecasts = Button(finestra, text="Extract Latest", fg="red",
                                           command=self.extract_precipitation_from_last_forecast)
        self.button_avg_forecasts.place(x=500, y=3, width=110, height=25)

        self.area_oggi = Entry(finestra, background="white", foreground="red",)
        self.area_oggi.place(x=450, y=30, width=150, height=25)

        # self.area_oggi.insert(INSERT, str(self.data_modificata))
        self.area_oggi.insert(INSERT, str(self.now.date()))

        #Scelta anni minimo massimo per analisi corrente
        in_che_anno_siamo = self.now.year
        lista_anni_correnti = list(range(1979, in_che_anno_siamo))

        self.days_check = IntVar()
        self.check_3 = Radiobutton(finestra, text="3 Days", value=3, variable=self.days_check)
        self.check_3.place(x=450, y=60, width=60, height=25)
        self.check_5 = Radiobutton(finestra, text="5 Days", value=5, variable=self.days_check)
        self.check_5.place(x=520, y=60, width=60, height=25)
        self.check_7 = Radiobutton(finestra, text="7 Days", value=7, variable=self.days_check)
        self.check_7.place(x=450, y=80, width=60, height=25)
        self.check_10 = Radiobutton(finestra, text="10 Days", value=10, variable=self.days_check)
        self.check_10.place(x=520, y=80, width=60, height=25)
        self.check_30 = Radiobutton(finestra, text="30 Days", value=30, variable=self.days_check)
        self.check_30.place(x=450, y=100, width=60, height=25)
        # self.check_46 = Radiobutton(finestra, text="46 Days", value=46, variable=self.days_check)
        self.check_46 = Radiobutton(finestra, text="46 Days", value=46, variable=self.days_check)
        self.check_46.place(x=520, y=100, width=60, height=25)

        self.box_value_minYear_current = StringVar()
        self.box_minYear_current = ttk.Combobox(finestra, textvariable= [], width=7)
        self.box_minYear_current['values'] = lista_anni_correnti
        self.box_minYear_current.place(x=450, y=125, width=155)

        self.box_value_maxYear_current = StringVar()
        self.box_maxYear_current = ttk.Combobox(finestra, textvariable = [],width=7)
        self.box_maxYear_current['values'] = lista_anni_correnti
        self.box_maxYear_current.place(x=450, y=150, width=155)

        self.button_anomalies = Button(finestra, text="Generate Anomaly Raster", fg="red",
                                       command= self.taglia_e_sottrai)
        self.button_anomalies.place(x=450, y=350, width=150, height=25)

        finestra.mainloop()


    def aggiungi_paese_alla_lista_di_processo(self):

        paese = self.box_value_adm0.get()
        self.listbox.insert(END, paese)


    def calcola_bbox_parteISO(self):

        lista_comandi = []
        lista_comandi.append("SELECT ST_Extent(geom) as bbox FROM sparc_gaul_wfp_iso WHERE ")
        self.cur_bbox = self.conn.cursor()

        num_items = self.listbox.size()
        for illo in range(0, num_items):
            pattivo = self.listbox.get(illo, last=None)
            self.parte_3lettere_per_file_grib.append(pattivo[0:3])
            if illo < num_items-1:
                lista_comandi.append("adm0_name = '" + str(pattivo) + "' OR ")
            else:
                lista_comandi.append("adm0_name = '" + str(pattivo) + "' ")
        lista_comandi.append(";")
        comando = ''.join(lista_comandi)

        self.dict_coords = {}
        try:
            self.cur_bbox.execute(comando)
            for la_stringa_coords in self.cur_bbox:
                coordinate = (la_stringa_coords[0].split("(")[1].split(")")[0])
                coordinateX, coordinateY = coordinate.split(",")
                min_x, min_y = coordinateX.split()
                max_x, max_y = coordinateY.split()
                self.dict_coords = {'xmin': min_x, 'ymin': min_y, 'xmax': max_x, 'ymax': max_y}
        except psycopg2.ProgrammingError as laTabellaNonEsiste:
            descrizione_errore = laTabellaNonEsiste.pgerror
            codice_errore = laTabellaNonEsiste.pgcode
            print descrizione_errore, codice_errore
            return codice_errore

        self.area_messaggi.insert(INSERT, self.dict_coords)


    def calcola_mean_from_historical_forecasts(self):

        anno_minimo = self.box_minYear_current.get()
        anno_massimo = self.box_maxYear_current.get()
        salto = self.days_check.get()

        range_anni_scelti = range(int(anno_minimo), int(anno_massimo)+1)
        date_per_creazione_files = calculate_time_window_date.controlla_date(anno_minimo,
                                                                             self.mese_inizio,
                                                                             self.giorno_inizio,
                                                                             salto)

        file_date = calculate_time_window_date.crea_file_avanzato(range_anni_scelti,
                                                                  date_per_creazione_files)
        self.calcola_bbox_parteISO()

        parte_iso = ''.join(self.parte_3lettere_per_file_grib)
        parte_date = file_date.split(".")[0].split("req")[1]

        self.raster_file_mean_grib = "1_gribs_from_ecmwf/" + parte_iso + parte_date + ".grib"
        if os.path.isfile(self.raster_file_mean_grib):
            self.area_messaggi.insert(INSERT, "Grib file exists")
            self.file_media = ecmwf_data_analysis.genera_means(self.raster_file_mean_grib,
                                                                    parte_iso,
                                                                    parte_date)
            self.area_messaggi.insert(INSERT, "File Mean Generated in %s " % self.file_media)
        else:
            self.area_messaggi.insert(INSERT, "Grib file does not exist")
            ecmwf_data_analysis.fetch_ECMWF_data_extent(self.raster_file_mean_grib, file_date, self.dict_coords)
            self.file_media = ecmwf_data_analysis.genera_means(self.raster_file_mean_grib,
                                                                                   parte_iso,
                                                                                   parte_date)
            self.area_messaggi.insert(INSERT,"File Mean Generated in %s " % self.file_media)


    def extract_precipitation_from_last_forecast(self):

        self.listbox.delete(0, END)
        messaggioFTP, files_disponibili = extract_total_precipitation_hres.FtpConnectionFilesGathering()
        stringhe_da_cercare = calculate_time_window_date.controlla_date_ftp(self.anno_inizio,
                                                                            str(self.mese_inizio),
                                                                            self.giorno_inizio,
                                                                            self.days_check.get())

        if len(files_disponibili) > 0:
            self.area_messaggi.insert(INSERT, messaggioFTP)
            lista_ftp = []
            tempo_analisi = self.days_check.get()

            if len(str(self.giorno_inizio)) < 2:
                stringa1 = str(self.mese_inizio) + str('0' + (str(self.giorno_inizio)))
                stringa2 = str(self.mese_inizio) + str(int(self.giorno_inizio + tempo_analisi))
            else:
                stringa1 = stringhe_da_cercare[1] + stringhe_da_cercare[0]
                stringa2 = stringhe_da_cercare[3] + stringhe_da_cercare[2]

            for file_disponibile in files_disponibili:
                lista_ftp.append(file_disponibile)
                self.listbox.insert(END, file_disponibile)
                if stringa1 and stringa2 in file_disponibile:
                    file_scelto = file_disponibile
            self.area_messaggi.insert(INSERT, file_scelto)

            ecmwf_dir = "3_ecmwf_ftp_wfp/"
            file_ftp = ecmwf_dir + file_scelto
            self.nome_file_estratto_TP = "3_ecmwf_ftp_wfp/TP_" + stringa1 + stringa2 + '.tif'

            extract_total_precipitation_hres.FtpConnectionFilesRetrieval(ecmwf_dir, file_scelto)
            extract_total_precipitation_hres.EstrazioneBandaTP_hres(file_ftp, self.nome_file_estratto_TP)
        else:
            tkMessageBox.showinfo("Warning", "No ECMWF files on server!!")
            pass


    def taglia_e_sottrai(self):

        file_current = self.nome_file_estratto_TP
        file_climate = self.file_media
        self.area_messaggi.insert(INSERT, "File Current %s " % file_current)
        self.area_messaggi.insert(INSERT, "File Climate %s " % file_climate)

        minX_clim_ar, maxY_clim_ar, maxX_clim_ar, minY_clim_ar = \
            wfp_data_analysis_anomalies_r1.coordinate_immagini(file_climate)
        print "Le coordinate di %s \nsono left %0.4f bottom %0.4f right %0.4f top %0.4f" %(
                    file_climate, minX_clim_ar, minY_clim_ar, maxX_clim_ar, maxY_clim_ar)

        larghezza,altezza = wfp_data_analysis_anomalies_r1.misura_immagini(file_climate)
        print "Le dimensioni della immagine %s \nsono larghezza %d altezza %d" % (file_climate,
                                                                                      larghezza,
                                                                                      altezza)

        print
        minX, maxY, maxX, minY = wfp_data_analysis_anomalies_r1.coordinate_immagini(file_current)
        print "Le coordinate di %s \nsono left %0.4f bottom %0.4f right %0.4f top %0.4f" % (file_current,
                                                                                                minX,
                                                                                                minY,
                                                                                                maxX,
                                                                                                maxY)

        larghezza, altezza = wfp_data_analysis_anomalies_r1.misura_immagini(file_current)
        print "Le dimensioni della immagine %s \nsono larghezza %d altezza %d" % (file_current, larghezza, altezza)

        ulY, lrY, lrX, ulX = \
            wfp_data_analysis_anomalies_r1.coordinate_da_tagliare_sul_raster_precipitazione_globale(file_current,
                                                                                                    minX_clim_ar,
                                                                                                    maxY_clim_ar,
                                                                                                    maxX_clim_ar,
                                                                                                    minY_clim_ar)
        print
        print "Le coordinate di taglio per  %s inviate sono ulX %0.4f lrY %0.4f lrX %0.4f ulY %0.4f" % (
                        file_climate, minX_clim_ar, minY_clim_ar, maxX_clim_ar, maxY_clim_ar )
        print "Le coordinate di taglio derivate da %s \nsono ulX %0.4f lrY %0.4f lrX %0.4f ulY %0.4f" % (
                file_climate, ulY, lrY, lrX, ulX)

        wfp_data_analysis_anomalies_r1.taglio_raster_corrente_su_area_mean_partial(file_current,
                                                                                    ulY,
                                                                                    lrY,
                                                                                    lrX,
                                                                                    ulX,
                                                                                    file_climate)

root = Tk()
root.title("ECMWF Data Analysis")
app = AppECMWF(root)




