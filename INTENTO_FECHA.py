from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Inicializa el navegador web (asegúrate de tener el controlador adecuado, como ChromeDriver, instalado y en el PATH)
driver = webdriver.Chrome()

# URL de la página web
url = "https://es.investing.com/equities/acciona-sa-historical-data"

# Inicializa el navegador web y abre la página
driver.get(url)

# Aceptar el aviso de cookies si es necesario (opcional)
try:
    xpath_cookie = '//*[@id="onetrust-accept-btn-handler"]'
    cookies_popup = driver.find_element_by_xpath(xpath_cookie)
    cookies_popup.click()
except:
    pass

# Inicializa date_input fuera del bloque try
date_input = None

# Espera a que el elemento de fecha esté presente, sea visible e interactuable
try:
    date_input = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="date"]')))
except TimeoutException as e:
    print(f"Error al esperar el elemento de fecha: {e}")

# Comprueba si date_input no es None antes de intentar obtener el atributo
if date_input is not None:
    is_disabled = date_input.get_attribute("disabled")
    print(f"¿El elemento está deshabilitado? {is_disabled}")

# Cierra el navegador al finalizar
driver.quit()
