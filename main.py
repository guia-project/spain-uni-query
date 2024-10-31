from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

ROOT_URL = "https://www.educacion.gob.es/ruct/"
UNIVERSITY_URL = ROOT_URL + "consultauniversidades?actual=universidades"
CENTER_URL = ROOT_URL + "consultacentros?actual=centros"
TITLE_URL = ROOT_URL + "consultaestudios?actual=estudios"
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options)


def get_university_data(url):
    university_data = {
        "University": {"Identification": {},
                       "Address": {},
                       "Document": {}}
    }
    entity = 2
    driver.get(url)
    university_table = driver.find_element(By.TAG_NAME, "fieldset")
    university_children = university_table.find_elements(By.XPATH, "./*")
    for child in university_children:
        if child.aria_role == "heading":
            entity = (entity + 1) % 3
        attributes = driver.find_elements(By.TAG_NAME, "label")
        for attribute in attributes:
            print(attribute.get_attribute("for") + " " + attribute.text)
            #university_data[entity][child.tag_name] = child.text
    driver.back()


driver.implicitly_wait(0.5)
driver.get(UNIVERSITY_URL)
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
