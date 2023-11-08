### IMPORTACIÓN DE LAS LIBRERÍAS NECESARIAS PARA EJECUTAR NUESTRO CÓDIGO
import os                               #Para Funcionalidades de sistema operativo (directorios etcc)
import requests
import pandas as pd
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
#from datetime import timedelta
from dateutil.relativedelta import *   #Para tratamiento de fechas
import warnings
warnings.filterwarnings('ignore')   #Desactivamos los warnings de tipo obsoleto

### Definicion de la funcion mediante la cual se ha obtener las URLS de empresas IBEX35 a traves de SELENIUM
def SeleniumURl(url_inicial):
    driver = webdriver.Chrome()
    driver.get(url_inicial)

    # Aceptar el aviso de cookies si es necesario
    try:
        xpath_cookie = '//*[@id="onetrust-accept-btn-handler"]'
        cookies_popup = driver.find_element(By.XPATH, xpath_cookie)
        cookies_popup.click()
    except:
        pass

    # Encontrar y guardar en una lista las URLs que contienen "equities" en href y "S.A" en el título
    enlaces = driver.find_elements(By.TAG_NAME, "a")
    enlaces_filtrados = []

    for enlace in enlaces:
        href = enlace.get_attribute("href")
        title = enlace.get_attribute("title")
        if href is not None and "equities" in href and "CFD" in title:
            enlaces_filtrados.append(href)

    # Crear una variable para almacenar la lista de URLs filtradas, y elimina duplicados
    lista_de_urls = list(set(enlaces_filtrados))
    #print("lista_de_uls: ", lista_de_urls)

    # Iterar sobre las URLs filtradas y buscar elementos "a" con "historical" en la URL
    #for url in enlaces_filtrados:
    lista_de_urls2 =[]

    for url in set(enlaces_filtrados):
        driver.get(url)  # Abrir la URL

        # Obtener elementos "a" con "historical" en el contexto de la página actual
        elementos_a = driver.find_elements(By.XPATH, '//a[contains(@href, "historical")]')

        for elemento in elementos_a:
            lista_de_urls2.append(elemento.get_attribute("href"))

    URL_hist= list(set(lista_de_urls2))
    URL_hist.sort()

    # Cerrar el navegador
    driver.quit()

    return URL_hist

### Definicion de la funcion mediante la cual se va a realizar el WEB SCRAPING de Historicos IBEX35
def HistIbex35(url_complet):

    dd = []                        # Se crea una lista vacía donde se recopilará la información que se extrae de la web

    print("url_complet: ", url_complet)
    page = requests.get(url_complet)
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

        dd.append(dd_diaX)

    return dd


### ----------------------------------------------------------------------------------------------------------###
#    Proceso PRINCIPAL                                                                                          #
#                                                                                                               #
#    A partir de este punto se ejecutará la funcion y se creara el fichero csv que contendrá el                 #
#    DATASET extraido mediante WEB SCRAPING                                                                     #
### ----------------------------------------------------------------------------------------------------------###

url_inicial = 'https://es.investing.com/indices/spain-35-components'   # URL donde se encuentran los componentes IBEX35
print('URL inicial: ', url_inicial)

link_ibex35 = SeleniumURl(url_inicial)    #Obtenemos las direcciones de los historicos de componentes IBEX35

# Generamos el datase que contendrá todos los valores a imprimir, y le añadimos una cambecera
dataset1 = []
campos = ["Empresa", "Fecha",  "Último", "Apertura",  "Maximo", "Minimo"
            , "Vol.", "%var."]     # lista con los nombres de los campos a recopilar
dataset1.append(campos)            # El primer elemento de dd son los nombres de los campos a recopilar

i=0
while i < len(link_ibex35):     # Accedemos a la pagina de cada link obtenido para traernos los datos historicos

    url_complet = link_ibex35[i]
    dataset = HistIbex35(url_complet)
    dataset1 = dataset1 + dataset

    i += 1

# Escritura del dataset en nuestro archivo .csv
directorio_actual = os.getcwd()
nombre_archivo = "datos_ibex35_dataset.csv"
ruta_archivo = os.path.join(directorio_actual, nombre_archivo)

with open(ruta_archivo, 'w', newline='') as archivo_csv:
    writer = csv.writer(archivo_csv, delimiter=';')
    for i in dataset1:
        writer.writerow(i)