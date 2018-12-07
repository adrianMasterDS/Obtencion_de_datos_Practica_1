import csv
import os
import re
from unicodedata import normalize


# Elimina las tildes sin quitar las de la ennes
def clean_string(string):
    # Fuente:
    # https://es.stackoverflow.com/questions/135707/
    # c%C3%B3mo-puedo-reemplazar-las-letras-con-tildes-por-las-mismas-sin-tilde-pero-no-l

    # -> NFD y eliminar diacríticos
    string = re.sub(
        r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1",
        normalize("NFD", string), 0, re.I
    )
    # -> NFC
    string = normalize('NFC', string)
    return string


def sorting_criteria(line_num, line_position):
    return str(10 ** 10) if line_num is None else line_num, line_position



def load_and_filter_metro_data():
    with open(scripts_dir_path + '/../data/stops_metro.txt', encoding='utf-8-sig') as metro_data:
        metro_dict = list()
        metro_dict_aux = list()

        dict_reader = csv.DictReader(metro_data)
        global metro_fields
        metro_fields = dict_reader.fieldnames

        for row in dict_reader:
            if row[dict_reader.fieldnames[0]].startswith('est'):  # TODO eliminar filtrado
                metro_dict_aux.append(row)

        for row in metro_dict_aux:
            aux_dict = dict()
            [aux_dict.update({cell: clean_string(row[cell])}) for cell in row]
            metro_dict.append(aux_dict)

        return metro_dict


def load_and_clean_scrap_data():
    with open(scripts_dir_path + '/../data/result_scrapy_ex.csv', encoding='utf-8-sig') as scrapy_metro_data:
        scrapy_metro_dict = list()

        dict_reader = csv.DictReader(scrapy_metro_data)
        global scrap_fields
        scrap_fields = dict_reader.fieldnames

        for row in dict_reader:
            aux_dict = dict()
            [aux_dict.update({cell: clean_string(row[cell])}) for cell in row]
            scrapy_metro_dict.append(aux_dict)
        return scrapy_metro_dict


scripts_dir_path = os.path.dirname(os.path.realpath(__file__))

metro_fields = list()
scrap_fields = list()

metro_dict = load_and_filter_metro_data()
scrapy_metro_dict = load_and_clean_scrap_data()


# TODO Si hiciese falta, normalizar nombres eliminando todo tipo de prefijos espacios etc y ordenando palabras
#  del nombre alfabeticamente para comparacion para evitar diferencias de orden


# Para cada fila proveniente del fichero, buscar los datos del scrap. Si no se encuentran:
# datos añadir campos nuevos vacios
for metro_row in metro_dict:
    positive_match = False
    for scrap_row in scrapy_metro_dict:
        aux_metro_stop_name = metro_row['stop_name'].lower()
        aux_scrap_station_name = scrap_row['station_name'].lower()

        is_station = metro_row['stop_id'].startswith('est')
        equals = aux_metro_stop_name == aux_scrap_station_name
        metro_contains_scrap = aux_metro_stop_name.find(aux_scrap_station_name) != -1

        if is_station and (equals or metro_contains_scrap):  # positive match
            metro_row.update(scrap_row)
            positive_match = True
            break

    if not positive_match:
        aux = dict()
        [aux.update({key: None}) for key in scrap_fields]
        metro_row.update(aux)


with open(scripts_dir_path + '/../merge_results/restult_test_1.csv', 'wt', encoding='utf-8-sig') as target_file:

    field_names = metro_fields + scrap_fields
    writer = csv.DictWriter(target_file, field_names)

    writer.writeheader()
    # Ordenar segun citerios:
    # 1: Primero los registros con numero de linea
    # 2: Los registros con menor numero de linea primero
    # 3: Los registos con menor posicion en linea primero
    for row in sorted(metro_dict, key=lambda r: sorting_criteria(r['line_number'], r['position_in_line'])):
        writer.writerow(row)
