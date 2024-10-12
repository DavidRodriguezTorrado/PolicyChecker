from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import pickle
import platform
import os
import time
import random


# Configuración del WebDriver usando WebDriverManager
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")  # Evitar la detección de automatización
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--disable-blink-features")
options.add_argument("--disable-gpu")  # Útil en sistemas con poca GPU
options.add_argument("--disable-extensions")
options.add_argument("--disable-popup-blocking")

options.add_argument("--lang=en")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
options.add_argument(f"user-agent={user_agent}")


driver_path = ChromeDriverManager().install()

# Inicialización del driver
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Evitar la detección de Selenium mediante la modificación de propiedades
script_to_disable_webdriver = "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script_to_disable_webdriver})

try:
    # Navegar a la página de inicio de sesión de OpenAI
    driver.get("https://platform.openai.com")

    # Esperar hasta que el elemento específico esté presente
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'font-medium') and contains(text(), 'OpenAI developer platform')]"))
    )

    print("Página cargada completamente y elemento encontrado")

    # Esperar y hacer clic en el botón de Log in
    # login_button = WebDriverWait(driver, 30).until(
    #     EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'btn-label-inner') and contains(text(), 'Log in')]"))
    # )
    # login_button.click()
    #
    # print("Botón de Log in clicado")
    #
    # # Esperar hasta que la página esté completamente cargada después de hacer clic en Log in
    # WebDriverWait(driver, 30).until(
    #     lambda d: d.find_element(By.TAG_NAME, "body")
    # )

    # Esperar 100 segundos para manipulación manual
    time.sleep(100)

    # Guardar cookies después de iniciar sesión
    time.sleep(5)  # Esperar un momento para asegurarse de que las cookies de sesión están disponibles
    with open("cookies.pkl", "wb") as f:
        pickle.dump(driver.get_cookies(), f)


except Exception as e:
    print(f"Ocurrió un error: {e}")
finally:
    # Puedes cerrar el navegador aquí si solo querías probar el inicio de sesión
    # driver.quit()
    pass