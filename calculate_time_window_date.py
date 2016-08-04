import os
import datetime

def raccolta_parametri(iso):

    range_anni = range(1979, 2016)
    while True:
        anno_minimo = input("Starting Year: ")
        if anno_minimo in range_anni:
            print "Selected %d " % anno_minimo
            break
        else:
            print "Year must be between 1979 and 2015"

    while True:
        anno_massimo = input("Ending Year (max 2015): ")
        if anno_massimo in range_anni:
            print "Selected %d " % anno_massimo
            break
        else:
            print "Year must be between 1979 and 2015"

    range_anni_scelti = range(anno_minimo, anno_massimo+1)
    # numero_anni = input("Number of Years : ")
    numero_anni = anno_massimo - anno_minimo
    print("Fetching data for %d years" % numero_anni)
    mese = raw_input("Month : ")
    if len(mese) == 1:
        mese = "0" + mese
    giorno_inizio = input("Starting Day: ")
    numero_giorni = input("Number of days: ")
    # giorno_fine = giorno_inizio + 7
    # giorno_fine = giorno_inizio + 8
    giorno_fine = giorno_inizio + numero_giorni

    return anno_minimo, anno_massimo, numero_anni, mese, giorno_inizio, giorno_fine, range_anni_scelti, numero_giorni

def controlla_date(anno_inizio, mese_inizio, giorno_inizio, salto):

    lista_mese_giorno = []
    lista_giorni = []
    data_iniziale = datetime.date(int(anno_inizio), int(mese_inizio), int(giorno_inizio))

    salto_giorni = datetime.timedelta(days=salto+1)
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

    lista_mese_giorno.append(str(mese_data_inziale) + "-" + str(giorno_data_iniziale))
    lista_giorni.append(giorno_data_iniziale)
    for indice in range(1, salto):
        range_date = datetime.timedelta(days=indice)
        giorni_successivi = data_iniziale + range_date
        lista_mese_giorno.append('{:02d}'.format(giorni_successivi.month) + "-" + '{:02d}'.format(giorni_successivi.day))
        lista_giorni.append(giorni_successivi)

    return lista_mese_giorno #,giorno_data_iniziale, mese_data_inziale, giorno_data_finale, mese_data_finale

def controlla_date_ftp(anno_inizio, mese_inizio, giorno_inizio, salto):

    data_iniziale = datetime.date(int(anno_inizio), int(mese_inizio), int(giorno_inizio))

    # DA RIMUOVERE PASSATO FEBBRAIO
    salto_giorni = datetime.timedelta(days=salto)
    data_finale = data_iniziale + salto_giorni

    giorno_data_iniziale = '{:02d}'.format(data_iniziale.day)
    giorno_data_finale = '{:02d}'.format(data_finale.day)
    mese_data_inziale = '{:02d}'.format(data_iniziale.month)
    mese_data_finale = '{:02d}'.format(data_finale.month)

    # print giorno_data_iniziale,mese_data_inziale,giorno_data_finale,mese_data_finale

    return giorno_data_iniziale, mese_data_inziale, giorno_data_finale, mese_data_finale

def crea_file(anno_minimo, numero_anni, mese, giorno_inizio, giorno_fine):

    lista_anni = []
    lista_finale = []
    giorno_controllo = giorno_inizio
    for anno_inizio in range(0, numero_anni +1 ):
        lista_anni.append(anno_minimo + anno_inizio)

    for anno in lista_anni:
        while giorno_controllo < giorno_fine:
            lista_finale.append(str(anno) + "-" + str(mese) + "-" + str(giorno_controllo))
            giorno_controllo += 1
        giorno_controllo = giorno_inizio

    prima_parte = str(giorno_inizio) + str(giorno_fine-1)
    seconda_parte = str(anno_minimo) + str(max(lista_anni))
    file_path = '0_generate_date_file/' + "req_" + str(prima_parte) + "_" + str(mese) + "_" + str(seconda_parte) + ".txt"
    if os.path.isfile(file_path):
        print "FILE DATES ESISTENTE"
        return file_path

    nuovo = open(file_path, mode='w')
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

    return file_path

def crea_file_avanzato(lista_anni, lista_giorni):

    lista_finale = []
    for anno in lista_anni:
        for giorno in lista_giorni:
                lista_finale.append(str(anno) + "-" + giorno)

    imesi = [i.split('-', 1)[0] for i in lista_giorni]
    mese_minimo = min(imesi)
    mese_massimo = max(imesi)
    # print mese_minimo, mese_massimo
    if mese_minimo == mese_massimo:
        igiorni = [i.split('-', 1)[1] for i in lista_giorni]
        giorno_minimo = min(igiorni)
        giorno_massimo = max(igiorni)
        mese = mese_minimo
    else:
        igiorni_a = [i.split(str(mese_massimo), 1)[0] for i in lista_giorni]
        solo_valori_igiorni_prima = filter(None, [i.split('-', 0)[0] for i in igiorni_a])
        igiorni_prima = [i.split('-', 1)[1] for i in solo_valori_igiorni_prima]
        igiorni_b = [i.split(str(mese_minimo), 1)[0] for i in lista_giorni]
        solo_valori_igiorni_dopo = filter(None, [i.split('-', 0)[0] for i in igiorni_b])
        igiorni_dopo = [i.split('-', 1)[1] for i in solo_valori_igiorni_dopo]
        giorno_minimo_a = min(igiorni_prima)
        # giorno_massimo_a = max(igiorni_prima)
        # giorno_minimo_b = min(igiorni_dopo)
        giorno_massimo_b = max(igiorni_dopo)

        giorno_minimo = giorno_minimo_a
        giorno_massimo = giorno_massimo_b
        mese = str(mese_minimo) + "_" + str(mese_massimo)
        # print giorno_minimo, giorno_massimo

    anno_minimo = min(lista_anni)
    anno_massimo = max(lista_anni) + 1

    prima_parte = str(giorno_minimo) + str(giorno_massimo)
    seconda_parte = str(anno_minimo) + str(anno_massimo)
    file_path = '0_generated_date_files/' + "req_" + str(prima_parte) + "_" + str(mese) + "_" + str(seconda_parte) + ".txt"
    if os.path.isfile(file_path):
        print "FILE DATES ESISTENTE"
        return file_path

    nuovo = open(file_path, mode='w')
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

    return file_path

def scateniamo_l_inferno(paese):

    pass

    # dati_raccolti = raccolta_parametri(paese)
    # lista_anni_analisi = dati_raccolti[6]
    # liste_date = controlla_date(dati_raccolti[0], dati_raccolti[3], dati_raccolti[4], dati_raccolti[7])
    # lista_mese_giorno = liste_date[0]
    # il_file_generato = crea_file(lista_anni_analisi, lista_mese_giorno)
    #
    # return il_file_generato
