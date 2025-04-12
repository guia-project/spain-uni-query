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
chrome_options.add_argument("--incognito")
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


def get_groupbox_data(groupbox, entity_dict):
    entity_code = driver.current_url.split("codigoEstudio=")[1].split("&")[0]
    groupbox_children = groupbox.find_elements(By.XPATH, "./*")
    entity_name = ""
    for child in groupbox_children:
        if child.aria_role == "heading":
            entity_name = child.text
        elif child.aria_role == "LabelText":
            key_value = child.text.split(":\n")
            try:
                entity_dict[entity_code][entity_name][key_value[0].rstrip()] = key_value[1]
            except IndexError:
                entity_dict[entity_code][entity_name][key_value[0].rstrip()] = ""


def get_table_data(table, entity_dict, id):
    degree_code = driver.current_url.split("codigoEstudio=")[1].split("&")[0]
    container = driver.find_element(By.ID, id)
    field_name = container.find_element(By.TAG_NAME, "h3").text
    table_title = table.find_elements(By.TAG_NAME, "th")
    table_row = table.find_elements(By.TAG_NAME, "tr")
    row_number = "1"
    for row in table_row:
        cells = row.find_elements(By.TAG_NAME, "td")
        for key, value in zip(table_title, cells):
            if id != "tfour":
                entity_dict[degree_code][field_name][key.text] = value.text.strip()
            else:
                if key.text == "Orden":
                    entity_dict[degree_code][field_name][value.text.strip()] = {}
                    row_number = value.text.strip()
                else:
                    entity_dict[degree_code][field_name][row_number][key.text] = value.text.strip()


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
"""
navigate_to(UNIVERSITY_URL)
universities_list = extract_all_entity_links("ruct/universidad.action")
write_to_json_file(universities_list, "universities_data.json")

navigate_to(CENTER_URL)
centers_list = extract_all_entity_links("ruct/centro.action")
write_to_json_file(centers_list,"centers_data.json")


universities_degree_list = extract_all_entity_links("ruct/universidadcentros.action")
degree_list = extract_all_entity_links("ruct/estudiouniversidad.action")
"""
driver.get("https://www.educacion.gob.es/ruct/estudiocentro.action?codigoCiclo=SC&codigoEstudio=2503028&actual=estudios")
degree_information_table = driver.find_element(By.ID, "tab_estudio")
driver.find_element(By.ID, "tab4").click()
degree_information = degree_information_table.find_elements(By.TAG_NAME, "table")
#degree_information = degree_information_table.find_elements(By.XPATH, "//fieldset")
degree_dict = nested_dict()

for degree in degree_information:
    get_table_data(degree, degree_dict,"tfour")
    #get_groupbox_data(degree, degree_dict)

for key, value in degree_dict.items():
    print("key: ", key, " values: ", value)

driver.quit()
