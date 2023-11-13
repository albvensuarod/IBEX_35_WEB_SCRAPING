### ----------------------------------------------------------------------------------------------------------###
#    Importacion de las librerias necesarias para ejecutar nuestro código                                       #
### ----------------------------------------------------------------------------------------------------------###
import os                               #Para Funcionalidades de sistema operativo (directorios etcc)
import requests
import pandas as pd
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from dateutil.relativedelta import *   #Para tratamiento de fechas
import warnings
warnings.filterwarnings('ignore')   #Desactivamos los warnings de tipo obsoleto

### ----------------------------------------------------------------------------------------------------------###
#                               Deficiones de FUNCIONES                                                         #
### ----------------------------------------------------------------------------------------------------------###
#
### Definicion de la funcion mediante la cual se ha obtener las URLS de empresas IBEX35 a traves de SELENIUM
def SeleniumURl(url_inicial):
    driver = webdriver.Chrome()        #Inicializamos el driver
    driver.get(url_inicial)            #Accedemos a la url especificada en param. de entrada

    # Aceptar el aviso de cookies si es necesario
    try:
        xpath_cookie = '//*[@id="onetrust-accept-btn-handler"]'
        cookies_popup = driver.find_element(By.XPATH, xpath_cookie)
        cookies_popup.click()
    except:
        pass

    # Encontrar y guardar en una lista las URLs que contienen "equities" en href y "CFD" en el título
    enlaces = driver.find_elements(By.TAG_NAME, "a")
    enlaces_filtrados = []

    for enlace in enlaces:
        href = enlace.get_attribute("href")
        title = enlace.get_attribute("title")
        if href is not None and "equities" in href and "CFD" in title:
            enlaces_filtrados.append(href)

    # Crear variables para almacenar la lista de URLs filtradas y elimina duplicados
    lista_de_urls = list(set(enlaces_filtrados))
    lista_de_urls2 = []
    lista_de_urls_categoricas_2 = []

    # Iterar sobre las URLs filtradas y buscar elementos "a" con "historical" en la URL for url in enlaces_filtrados:
    for url in set(enlaces_filtrados):
        driver.get(url)  # Abrir la URL

        # Confecionamos lista URL_hist: Obtener elementos "a" con "historical" en el contexto de la página actual
        elementos_a = driver.find_elements(By.XPATH, '//a[contains(@href, "historical")]')
        for elemento in elementos_a:
            lista_de_urls2.append(elemento.get_attribute("href"))

        # Confecionamos lista URL_Categoricas: Obtener elementos "a" con "profile" en el contexto de la página actual
        elementos_b = driver.find_elements(By.XPATH, '//a[contains(@href, "profile")]')
        for elementob in elementos_b:
            lista_de_urls_categoricas_2.append(elementob.get_attribute("href"))

    # Eliminamos posibles duplicados y ordenamos las listas con las URLs necesarias para obtener los datos
    URL_hist = list(set(lista_de_urls2))
    URL_hist.sort()
    URL_categoricas = list(set(lista_de_urls_categoricas_2))
    URL_categoricas.sort()

    # Cerrar el navegador
    driver.quit()

    return URL_hist, URL_categoricas


### Definicion de la funcion mediante la cual se va a realizar el WEB SCRAPING de Historicos IBEX35
def HistIbex35(url_complet, headers):

    ddH = []                       # Se crea una lista vacía donde se recopilará la información que se extrae de la web

    print("url_complet: ", url_complet)
    page = requests.get(url_complet, headers )
    soup = BeautifulSoup(page.content, "html.parser")

    #En los datos variables que almacenamos el código HTML buscamos la etiqueta H1, para localizar el nombre empresa IBEX35
    Empresa = soup.find('h1').getText()

    # En los datos variables que almacenamos el código HTML buscamos la  palabra  clave «table» con la función.find_all()
    datos = soup.find_all('table')
    #print(datos[1].prettify())

    datos = datos[:-3]  # Eliminamos los tres últimos valores de la lista "datos" porque son tres tablas de datos
                        # globales  que no nos interesan en el estudio

    # Con el comando .read_html, la maquina interpretara el html y luego recuperaremos el bloque1 en un dataFrame, que
    # es donde se encuentran los datos que buscamos.
    datos1 = pd.DataFrame(pd.read_html(str(datos))[1])

    for i in range(len(datos1)):  # recorremos los valores de cada una de las filas del dataFrame
        try:
            Fecha = datos1.Fecha[i]
        except Exception as err:
            datos1 = pd.DataFrame(pd.read_html(str(datos))[0])

        Fecha     = datos1.Fecha[i]
        ultim_avg = format((datos1.Último[i]/1000),'0,.3f').replace('.',',')
        apert_avg = format((datos1.Apertura[i] / 1000), '0,.3f').replace('.', ',')
        maxim_avg = format((datos1.Máximo[i] / 1000), '0,.3f').replace('.', ',')
        minim_avg = format((datos1.Mínimo[i] / 1000), '0,.3f').replace('.', ',')
        vol_avg   = datos1['Vol.'][i]
        pvar_avg  = datos1['% var.'][i]

        #Almacenamos los datos obtenidos en un array para añadirlos en el dataFrame dd
        dd_diaX   = [Empresa, Fecha, ultim_avg, apert_avg, maxim_avg, minim_avg, vol_avg, pvar_avg]

        ddH.append(dd_diaX)

    return ddH

### Definicion de la funcion mediante la cual se va a realizar el WEB SCRAPING para la obtencion de las variables categoricas
### Por cada empresa que componen el IBEX35.
def categIbex35(url_complet, headers):

    print("url_complet (Categoricas): ", url_complet)
    page = requests.get(url_complet, headers)
    soup = BeautifulSoup(page.text, "lxml")
    dato = soup.find('div', attrs={'class': 'companyProfileHeader'})

    # Se crean listas vacías donde se recopilará la información que se extrae de la web para las var. categoricas
    ddCat = []
    dda   = []      # Lista auxiliar por añadiendo cada uno de los elementos

    # En los datos variables que almacenamos el código HTML buscamos la etiqueta H1, para localizar el nombre empresa IBEX35
    Empresa = soup.find('h1').getText()
    dda.append(Empresa)

    # Obtenemos los datos de las etiquetas "a" ("Industria" y "Sector")
    a_tags = dato.find_all('a')
    for tag in a_tags:
         dda.append(tag.get_text())

    # Obtenemos los datos de las etiquetas "p" ("Empleados" y "Tipo de Accion")
    p_tags = dato.find_all('p')
    for tag in p_tags:
        dda.append(tag.get_text())

    #Añadimos las listas creadas con los campos independientes a una q contenga toda la linea.
    ddCat.append(dda)

    return ddCat

### Definicion de la funcion para imprimir los distintos ficheros
def writeFicheros(nombre_archivo, fdatasets):
    directorio_actual = os.getcwd()
    ruta_archivo = os.path.join(directorio_actual, nombre_archivo)

    with open(ruta_archivo, 'w', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv, delimiter=';')
        for i in fdatasets:
            writer.writerow(i)


### ----------------------------------------------------------------------------------------------------------###
#    Proceso PRINCIPAL                                                                                          #
#                                                                                                               #
#    A partir de este punto se ejecutará la funcion y se creara el fichero csv que contendrá el                 #
#    DATASET extraido mediante WEB SCRAPING                                                                     #
### ----------------------------------------------------------------------------------------------------------###

##---------  Definimos user-Agent ----------------------------------------------------------------------
# defining the User-Agent header to use in the GET request below
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

##---------  Definiciones de variables  ----------------------------------------------------------------------
# Definimos las cabeceras para cada uno de los ficheros necesarios para la practica (datos Historicos, datos Categoricos)
camposH = ["Empresa", "Fecha", "Último", "Apertura", "Maximo", "Minimo", "Vol.", "%var."]  #lista con los nombres de los campos a recopilar en historico
camposC = ["Empresa", "Industria", "Sector", "Empleados", "Tipo de Accion"]                #lista con los nombres de los campos a recopilar en categoricos

# Generamos los datasetse que contendrá todos los valores a imprimir para cada uno de los ficheros
fdatasets = []                      # dataset, auxiliar para enviar a imprimir

dataset1 = []                       # dataset1: Para el fichero "datos_ibex35_dataset.csv"
dataset1.append(camposH)            # El primer elemento de dd son los nombres de los campos a recopilar

dataset2 = []                       # dataset2: Para el fichero "datos_categericos_dataset.csv"
dataset2.append(camposC)            # El primer elemento de dd son los nombres de los campos a recopilar


##---------  Inicio de programa  -------------------------------------------------------------------------
url_inicial = 'https://es.investing.com/indices/spain-35-components'   # URL donde se encuentran los componentes IBEX35
print('URL inicial: ', url_inicial)

link_ibex35, link_categoricas  = SeleniumURl(url_inicial)   # Obtenemos las direcciones de los historicos y categoricas de componentes IBEX35

i=0  #Bucle para obtener los datos para el fichero  "datos_ibex35_dataset.csv".
while i < len(link_ibex35):     # Accedemos a la pagina de cada link obtenido para traernos los datos historicos
    url_complet = link_ibex35[i]
    dataset = HistIbex35(url_complet, headers)
    dataset1 = dataset1 + dataset
    i += 1


i=0  #Bucle para obtener los datos para el fichero  "datos_categericos_dataset.csv".
while i < len(link_categoricas):     # Accedemos a la pagina de cada link obtenido para traernos los datos historicos
     url_complet = link_categoricas[i]
     dataset = categIbex35(url_complet, headers)
     dataset2 = dataset2 + dataset
     i += 1


# Escritura de los datasets en nuestros diferentes archivos .csv
nombre_archivo = "datos_ibex35_dataset.csv"
fdatasets = dataset1
writeFicheros(nombre_archivo, fdatasets)

nombre_archivo = "datos_categericos_dataset.csv"
fdatasets = dataset2
writeFicheros(nombre_archivo, fdatasets)
