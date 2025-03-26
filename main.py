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

def navigate_to(url):
    driver.get(url)
    submit = driver.find_element(By.CLASS_NAME, "botones-submit")
    submit.click()


def nested_dict():
    return defaultdict(nested_dict)


def get_education_data(url):
    education_dict = nested_dict()
    entity_name = ""
    driver.get(url)
    university_name = driver.find_element(By.XPATH, "//form/h2").text
    try:
        entity_main_name = driver.find_element(By.XPATH, "//form[@id='centro']/h3").text
        education_dict[entity_main_name]["Datos de identificación"]["Nombre universidad"] = university_name
    except NoSuchElementException:
        entity_main_name = university_name
    education_table = driver.find_element(By.TAG_NAME, "fieldset")
    education_children = education_table.find_elements(By.XPATH, "./*")
    for child in education_children:
        if child.aria_role == "heading":
            entity_name = child.text
        if child.aria_role == "LabelText":
            key_value = child.text.split(":\n")
            try:
                education_dict[entity_main_name][entity_name][key_value[0].rstrip()] = key_value[1]
            except IndexError:
                education_dict[entity_main_name][entity_name][key_value[0].rstrip()] = ""
    driver.back()
    print("Completed")
    return education_dict


def extract_all_entity_links(entity_link):
    end_page = False
    entities_list = []
    while not end_page:
        table_education = driver.find_element(By.TAG_NAME, "table")
        table_links = table_education.find_elements(By.TAG_NAME, "a")
        for link in table_links:
            link_address = link.get_attribute("href")
            if entity_link in link_address:
                entities_list.append(link_address)
        end_page = True
    return entities_list


def go_to_next_page():
    try:
        page_link = driver.find_element(By.CLASS_NAME, "pagelinks").find_element(By.LINK_TEXT, "Siguiente")
        page_link.click()
        return False
    except NoSuchElementException:
        return True


def write_to_json_file(entity_list, file_name):
    entity_dict = {}
    for entity in entity_list:
        entity_dict.update(get_education_data(entity))
    json_string = json.dumps(entity_dict, ensure_ascii=False, indent=4)
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(json_string)

driver.implicitly_wait(0.5)

navigate_to(UNIVERSITY_URL)
universities_list = extract_all_entity_links("ruct/universidad.action")
write_to_json_file(universities_list, "universities_data.json")

navigate_to(CENTER_URL)
centers_list = extract_all_entity_links("ruct/centro.action")
write_to_json_file(centers_list,"centers_data.json")

driver.quit()
