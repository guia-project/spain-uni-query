from selenium import webdriver
from selenium.webdriver.common.by import By

rootURL = "https://www.educacion.gob.es/ruct/"
universityURL = rootURL + "consultauniversidades?actual=universidades"
centerURL = rootURL + "consultacentros?actual=centros"
titleURL= rootURL + "consultaestudios?actual=estudios"
driver = webdriver.Chrome()

driver.implicitly_wait(0.5)
driver.get(universityURL)
#print(driver.page_source)

submit = driver.find_element(By.CLASS_NAME, "botones-submit")
submit.click()
print("--------------------------------------------------------------------------------")
print(driver.page_source)

table = driver.find_element(By.TAG_NAME,"table")
elements = table.find_elements(By.TAG_NAME, "a")
for element in elements:
    #print(element.text)
    link_element = element.get_attribute("href")
    if link_element.__contains__("ruct/universidad.action"):
        print(element.text)
        print(link_element)


driver.quit()
