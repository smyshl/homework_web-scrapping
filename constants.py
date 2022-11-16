import csv
import os.path


def get_old_hrefs():

    if os.path.isfile('viewed_cars.csv'):
        with open('viewed_cars.csv', 'r', newline='', encoding='utf-8') as csv_file:
            csv_file_reader = csv.reader(csv_file, delimiter=' ')
            all_file_list = list(csv_file_reader)
            viewed_cars_hrefs_list = [nested_list[0] for nested_list in all_file_list]
    else:
        viewed_cars_hrefs_list = []

    return viewed_cars_hrefs_list


BASE_URL = 'https://auto.ru/cars/ford/mondeo/6519702/used/displacement-2300/'
BASE_PARAMS = {}  # {'year_from': '2010', 'year_to': '2011'}  # , 'output_type': 'list'}

OLD_HREFS = get_old_hrefs()

TOKEN = ''

HEADERS = {

}

CAR_ATTRIB_HEADERS = [
    'Марка',
    'Модель',
    'Поколение',
    'Рестайлинг',
    'Объем двигателя',
    'ед.изм.Vдв',
    'Мощность',
    'ед.изм.Wдв',
    'Тип топлива',
    'Тип коробки передач',
    'Тип кузова',
    'Привод',
    'Цвет',
    'Цена',
    'Валюта',
    'Год выпуска',
    'Пробег',
    'ед.изм.Пробега',
    'Место продажи',
    'Ссылка'
]
