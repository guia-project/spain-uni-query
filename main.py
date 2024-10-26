from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options)
root_url = "https://www.educacion.gob.es/ruct/"
university_url = root_url + "consultauniversidades?actual=universidades"
center_url = root_url + "consultacentros?actual=centros"
title_url = root_url + "consultaestudios?actual=estudios"


def get_university_data(url):
    university_data = {
        "Identification": {},
        "Address": {},
        "Document": {}
    }
    driver.get(url)
    university_code = driver.find_element(By.CSS_SELECTOR, 'label[for="codigoUniversidad"]')
    print(university_code.text)
    driver.back()


driver.implicitly_wait(0.5)
driver.get(university_url)
submit = driver.find_element(By.CLASS_NAME, "botones-submit")
submit.click()

end_page = False
universities_list = []
while not end_page:
    table_university = driver.find_element(By.TAG_NAME, "table")
    table_links = table_university.find_elements(By.TAG_NAME, "a")
    for link in table_links:
        link_address = link.get_attribute("href")
        if link_address.__contains__("ruct/universidad.action"):
            universities_list.append(link_address)
    try:
        page_link = driver.find_element(By.CLASS_NAME, "pagelinks").find_element(By.LINK_TEXT, "Siguiente")
        page_link.click()
    except NoSuchElementException:
        end_page = True

for university in universities_list:
    get_university_data(university)

driver.quit()
