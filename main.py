import csv
import requests
from bs4 import BeautifulSoup
from constants import HEADERS, CAR_ATTRIB_HEADERS, OLD_HREFS, BASE_URL, BASE_PARAMS, TOKEN
import re
import time
from datetime import datetime


request_counter = [0]


def send_to_smyshlbot(send_data):

    data = {'chat_id': "217907810", 'text': send_data}
    requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage', data=data)


def save_viewed_cars(cars_list_for_save, flags_list_for_save):

    with open('viewed_cars.csv', 'a+', newline='', encoding='utf-8') as csv_file:
        csv_file_writer = csv.writer(csv_file, delimiter=' ')

        for index, flag in enumerate(flags_list_for_save):
            if flag == 0:
                csv_file_writer.writerow([cars_list_for_save[index]['Ссылка'], datetime.today()])


def make_request(page: int, base_url=BASE_URL, params=BASE_PARAMS):

    request_counter[0] += 1

    if page == 1:
        url = base_url
    elif page > 1:
        url = base_url + '?page=' + str(page)

    response = requests.get(url, headers=HEADERS, params=params)
    # time.sleep(0.05)

    response.encoding = 'utf-8'

    return response.text


def check_page_response(link):

    page_response = ''

    page_head_title_text = BeautifulSoup(make_request(1, link, ''), features='html.parser').head.title.text

    if 'Ой!' in page_head_title_text:
        page_response = 'Captcha'
        print(link, '- На странице стоит Captcha!')
    elif '404' in page_head_title_text:
        page_response = '404'
    elif 'Купить' in page_head_title_text:
        page_response = 'OK'

    return page_response


def analyse_cars_list_page(cars_list_page):

    soup = BeautifulSoup(cars_list_page, features='html.parser')
    cars = soup.find_all(attrs={"class": "ListingItem"})

    old_car_flags = []
    cars_page_list = []
    non_existent_cars_list = []

    if cars:
        response_no_cars = False

        print('\nСтраница -', page_counter)

        for i, car in enumerate(cars):

            print('\rВыполняется обработка машин ', '-' * (i + 1), (i + 1), end='')

            car_dict = dict(zip(CAR_ATTRIB_HEADERS, ['' for _ in range(len(CAR_ATTRIB_HEADERS))]))

            car_name = car.find("a", class_="Link ListingItemTitle__link").text.split()

            if len(car_name) == 3:
                car_dict['Марка'], car_dict['Модель'], car_dict['Поколение'] = car_name
            elif len(car_name) == 4:
                car_dict['Марка'], car_dict['Модель'], car_dict['Поколение'], car_dict['Рестайлинг'] = car_name

            car_dict['Ссылка'] = car.find('a').get('href')

            car_price = car.find("div", class_="ListingItemPrice__content").text
            car_dict['Валюта'] = car_price[-1]
            car_dict['Цена'] = int(''.join(re.findall(r"\d+", car_price)))

            car_dict['Год выпуска'] = int(car.find("div", class_="ListingItem__year").text)

            car_odometer = car.find("div", class_="ListingItem__kmAge").text
            car_dict['ед.изм.Пробега'] = car_odometer[-2:]
            car_dict['Пробег'] = int(''.join(re.findall(r"\d+", car_odometer)))

            car_dict['Место продажи'] = car.find("span", class_="MetroListPlace__regionName MetroListPlace_nbsp").text

            tech_info = []

            for info in car.find_all('div', class_="ListingItemTechSummaryDesktop__cell"):
                for string in info.strings:
                    tech_info.append(string)

            tech_info[0] = tech_info[0].split()

            car_dict['Объем двигателя'], car_dict['ед.изм.Vдв'], car_dict['Мощность'], \
            car_dict['ед.изм.Wдв'], car_dict['Тип топлива'] = tech_info[0][0], tech_info[0][1], \
                                                              tech_info[0][3], tech_info[0][4], tech_info[0][6]
            car_dict['Тип коробки передач'], car_dict['Тип кузова'], car_dict['Привод'], car_dict['Цвет'] = tech_info[
                                                                                                            1:]
            if car_dict['Ссылка'] in OLD_HREFS:
                old_car_flags.append(1)
                cars_page_list.append(car_dict)
            else:
                page_response_val = check_page_response(car_dict['Ссылка'])
                if page_response_val == 'OK':
                    cars_page_list.append(car_dict)
                    old_car_flags.append(0)
                    send_to_smyshlbot(f'Найдена новая машина - {car_dict["Ссылка"]}')
                elif page_response_val == '404':
                    non_existent_cars_list.append(car_dict['Ссылка'])

        if 0 in old_car_flags:
            save_viewed_cars(cars_page_list, old_car_flags)

        print('\nНесуществующих объявлений в выдаче -', len(non_existent_cars_list))
        if non_existent_cars_list:
            print('\n'.join(non_existent_cars_list))
        print('Новых машин - ', len([old_car_flags[i] for i in range(len(old_car_flags)) if old_car_flags[i] == 0]))

    else:
        response_no_cars = True

    return response_no_cars, cars_page_list, old_car_flags


if __name__ == '__main__':

    page_counter = 1
    flags = []
    cars_list = []
    no_cars_response = False
    av_price = 0
    av_odometer = 0
    cities_list = []
    cars_counter = 0

    while not no_cars_response:

        result = analyse_cars_list_page(make_request(page_counter))
        no_cars_response = result[0]
        if not no_cars_response:
            flags.append(result[2])
            cars_list.append(result[1])
            page_counter += 1

    for page in cars_list:
        for car in page:
            av_price += car['Цена']
            av_odometer += car['Пробег']
            cities_list.append(car['Место продажи'])
            cars_counter += 1

    av_price = round(av_price / cars_counter, 2)
    av_odometer = round(av_odometer / cars_counter, 2)

    print('\nВсего страниц:', page_counter - 1)
    print('Всего объявлений:', sum([len(cars_list[page]) for page in range(len(cars_list))]))
    print('Средняя цена машин:', av_price)
    print('Средний пробег машин:', av_odometer)
    print('Города продажи:', ', '.join(set(cities_list)))
    print('Выполнено requests:', request_counter[0])

