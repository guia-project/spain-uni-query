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
    driver.get(url)
    university_name = driver.find_element(By.XPATH, "//form/h2").text
    try:
        entity_main_name = driver.find_element(By.XPATH, "//form[@id='centro']/h3").text
        entity_code = get_entity_code("codigoCentro=")
        education_dict[entity_code]["Datos de identificación"]["Nombre centro"] = entity_main_name
    except NoSuchElementException:
        entity_code = get_entity_code("codigoUniversidad=")
    education_dict[entity_code]["Datos de identificación"]["Nombre universidad"] = university_name
    education_table = driver.find_element(By.TAG_NAME, "fieldset")
    get_groupbox_data(education_table, education_dict, entity_code)
    driver.back()
    print("Completed")
    return education_dict


def get_groupbox_data(groupbox, entity_dict, entity_code):
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


def get_table_data(table, entity_dict, div_id):
    degree_code = get_entity_code("codigoEstudio=")
    container = driver.find_element(By.ID, div_id)
    field_name = container.find_element(By.TAG_NAME, "h3").text
    if div_id == "ttwo":
        field_name = table.find_element(By.XPATH, "..").find_element(By.TAG_NAME, "legend").text
    table_title = table.find_elements(By.TAG_NAME, "th")
    table_row = table.find_elements(By.TAG_NAME, "tr")
    row_number = "1"
    for row in table_row:
        cells = row.find_elements(By.TAG_NAME, "td")
        for key, value in zip(table_title, cells):
            if div_id != "tfour":
                entity_dict[degree_code][field_name][key.text] = value.text.strip()
            else:
                if key.text == "Orden":
                    entity_dict[degree_code][field_name][value.text.strip()] = {}
                    row_number = value.text.strip()
                else:
                    entity_dict[degree_code][field_name][row_number][key.text] = value.text.strip()


def get_entity_code(separator):
    return driver.current_url.split(separator)[1].split("&")[0]


def extract_all_degree_links(center_link):
    driver.get(center_link)
    degree_list = extract_all_entity_links("ruct/estudiocentro.action")
    driver.back()
    return degree_list


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


def retrieve_data_to_dict(entity_list):
    entity_dict = {}
    for entity in entity_list:
        entity_dict.update(get_education_data(entity))
    return entity_dict


def write_to_json_file(entity_dict, file_name):
    json_string = json.dumps(entity_dict, ensure_ascii=False, indent=4)
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(json_string)


driver.implicitly_wait(0.5)

navigate_to(UNIVERSITY_URL)
universities_list = extract_all_entity_links("ruct/universidad.action")
universities_dict = retrieve_data_to_dict(universities_list)
write_to_json_file(universities_dict, "universities_data.json")

navigate_to(CENTER_URL)
centers_list = extract_all_entity_links("ruct/centro.action")
centers_dict = retrieve_data_to_dict(centers_list)
write_to_json_file(centers_dict,"centers_data.json")
navigate_to(CENTER_URL)
degrees_list = []
centers_degree_list = extract_all_entity_links("ruct/listaestudioscentro.action")
for center in centers_degree_list:
    degrees_list.extend(extract_all_degree_links(center))


driver.get("https://www.educacion.gob.es/ruct/estudiocentro.action?codigoCiclo=SC&codigoEstudio=2503028&actual=estudios")
div_id_list = ["tone", "ttwo", "tthree", "tfour"]
degrees_dict = nested_dict()

for index, div_id in enumerate(div_id_list):
    ui_id = f"tab{index+1}"
    try:
        driver.find_element(By.ID, ui_id).click()
        degree_information = driver.find_element(By.ID, div_id)
        degree_information_table = degree_information.find_elements(By.TAG_NAME, "table")
        degree_information_groupbox = degree_information.find_elements(By.TAG_NAME, "fieldset")
        degree_code = get_entity_code("codigoEstudio=")
        for degree in degree_information_table:
            get_table_data(degree, degrees_dict, div_id)
        for degree in degree_information_groupbox:
            get_groupbox_data(degree, degrees_dict, degree_code)
    except NoSuchElementException:
        pass

write_to_json_file(degrees_dict, "degrees_data.json")

driver.quit()