from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options)
rootURL = "https://www.educacion.gob.es/ruct/"
universityURL = rootURL + "consultauniversidades?actual=universidades"
centerURL = rootURL + "consultacentros?actual=centros"
titleURL = rootURL + "consultaestudios?actual=estudios"


def get_university_data(url):
    university_data = {
        "Identification": {},
        "Address": {},
        "Document": {}
    }
    # driver.get(url)

    # print(driver.page_source)


driver.implicitly_wait(0.5)
driver.get(universityURL)

submit = driver.find_element(By.CLASS_NAME, "botones-submit")
submit.click()
print(driver.page_source)

table_university = driver.find_element(By.TAG_NAME, "table")
table_links = table_university.find_elements(By.TAG_NAME, "a")
universities_list = []

for link in table_links:
    link_address = link.get_attribute("href")
    if link_address.__contains__("ruct/universidad.action"):
        universities_list.append(link_address)

for university in universities_list:
    get_university_data(university)

driver.quit()
