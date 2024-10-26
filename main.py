from selenium import webdriver

rootURL = "https://www.educacion.gob.es/ruct/"
universityURL = rootURL + "consultauniversidades?actual=universidades"
centerURL = rootURL + "consultacentros?actual=centros"
titleURL= rootURL + "consultaestudios?actual=estudios"
driver = webdriver.Chrome()

driver.get(universityURL)
print(driver.page_source)
