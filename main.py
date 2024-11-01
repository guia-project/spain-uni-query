from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from collections import defaultdict
import json

ROOT_URL = "https://www.educacion.gob.es/ruct/"
UNIVERSITY_URL = ROOT_URL + "consultauniversidades?actual=universidades"
CENTER_URL = ROOT_URL + "consultacentros?actual=centros"
TITLE_URL = ROOT_URL + "consultaestudios?actual=estudios"
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options)


def nested_dict():
    return defaultdict(nested_dict)


def get_university_data(url):
    university_dict = nested_dict()
    entity_name = ""
    driver.get(url)
    name_university = driver.find_element(By.TAG_NAME, "h2")
    university_table = driver.find_element(By.TAG_NAME, "fieldset")
    university_children = university_table.find_elements(By.XPATH, "./*")
    for child in university_children:
        if child.aria_role == "heading":
            entity_name = child.text
        if child.aria_role == "LabelText":
            key_value = child.text.split(":\n")
            try:
                university_dict[name_university.text][entity_name][key_value[0].rstrip()] = key_value[1]
            except IndexError:
                university_dict[name_university.text][entity_name][key_value[0].rstrip()] = ""
    driver.back()
    print("Completed")
    return university_dict


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
        if "ruct/universidad.action" in link_address:
            universities_list.append(link_address)
    try:
        page_link = driver.find_element(By.CLASS_NAME, "pagelinks").find_element(By.LINK_TEXT, "Siguiente")
        page_link.click()
    except NoSuchElementException:
        end_page = True

universities_dict = {}
for university in universities_list:
    universities_dict.update(get_university_data(university))
with open("universities_data.json", "w", encoding="utf-8") as f:
    json.dump(universities_dict, f, ensure_ascii=False, indent=4)

driver.quit()
