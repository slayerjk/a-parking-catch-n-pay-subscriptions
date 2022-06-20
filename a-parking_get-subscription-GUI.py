#!/usr/bin/env python3

import PySimpleGUI as sg
import re
import logging
from os import mkdir, path
import requests
import urllib3
from bs4 import BeautifulSoup
from datetime import date, datetime
from time import sleep
from sys import exit
import re

### DISABLE SSL WARNING MESSAGES ###
urllib3.disable_warnings()

### DEFINING SCRIPT'S START TIME ###
start_date = datetime.now()
today = (date.today()).strftime('%d-%m-%Y')

'''
### DEFINING WORK DIR(SCRIPT'S LOCATION) ###
work_dir = 'D:/Docs-marchenm/Scripts/Python/A-parking_get-subscription'

###########################
##### LOGGING SECTION #####

logs_dir = work_dir+'/logs'

if not path.isdir(logs_dir):
    mkdir(logs_dir)

app_log_name = logs_dir+'/GUI_a-parking_get-subscription_log_' + \
    str(start_date.strftime('%d-%m-%Y'))+'.log'
logging.basicConfig(filename=app_log_name, filemode='w', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%Y %H:%M:%S')

logging.info('SCRIPT WORK STARTED: GET & PAY A-PARKING SUBSCRIPTION')
logging.info('Script Starting Date&Time is: ' +
             str(start_date.strftime('%d/%m/%Y %H:%M:%S')) + '\n')
'''

##########################################
##### A-PARKING CONNECTION VARIABLES #####

### URLS ###
a_parking_url = 'https://lk.aparking.kz/'
a_parking_subscriptions_url = 'https://lk.aparking.kz/?page=subscriptions'
a_parking_logout_url = 'https://lk.aparking.kz/?page=logout/'

### CONNECTION DATA ###
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.141 Safari/537.36'
}

### PROXIES DEFAULT VALUES ###
proxies = {
    'http': None,
    'https': None
}

### NUMBER OF ATTEMPTS FOR EVERY GET/POST REQUEST ###
request_attempts = 10

### SUBSCRIPTIONS LIST ###
subscriptions_list = []

### RESULT LIST ###
result_list = []

######################
#####  FUNCTIONS #####

### COUNT ESTIMATED TIME ###
def estimated_time():
    end_date = datetime.now()
    estimated_time = ('Затрачено времени:' + str(end_date - start_date))
    return(estimated_time)

### SHOW RESULT POPUP ###
def show_result():
    result_list.append(estimated_time())
    sg.popup_ok(title='Результат', *result_list)
    user_window.close()
    exit()

### DEFINING WINDOW THEME ###
sg.theme('Topanga')

### USER WINDOW LAYOUT ELEMENTS ###
checkbox_proxy = sg.Checkbox(
    'Использовать Proxy', False, enable_events=True, key='check-proxy')
http_proxy_text = sg.Text(
    'Введите HTTP прокси(формат: http://proxy.example.com:8080):', visible=False)
https_proxy_text = sg.Text(
    'Введите HTTPS прокси(формат: http(s)://proxy.example.com:8080):', visible=False)
http_proxy_field = sg.InputText(
    visible=False, key='http-proxy', default_text='None')
https_proxy_field = sg.InputText(
    visible=False, key='https-proxy', default_text='None')
user_login_text = sg.Text('Введите свой A-Parking ЛОГИН(пр.: +7xxxxxxxxxx): ')
user_login_field = sg.InputText(
    #s=50, key='user-login', default_text='+77773878075')
    s=50, key='user-login')
user_pin_text = sg.Text('Введите свой A-Parking ПАРОЛЬ: ')
user_pin_field = sg.InputText(
    #key='user-pin', password_char='*', size=50, default_text='1366')
    key='user-pin', password_char='*', size=50)
user_car_text = sg.Text(
    'Введите свой ГОС. НОМЕР МАШИНЫ(как в личном кабинете): ')
#user_car_field = sg.InputText(s=50, key='user-car', default_text='718ARA02')
user_car_field = sg.InputText(s=50, key='user-car')
user_zone_text = sg.Text('Введите желаемую ПАРКОВОЧНУЮ ЗОНУ: ')
#user_zone_field = sg.InputText(s=50, key='user-zone', default_text='1003')
user_zone_field = sg.InputText(s=50, key='user-zone')
subcrtiptions_quantity_text = sg.Text('Сколько подписок купить(от 1 до 5): ')
subcrtiptions_quantity_field = sg.Spin(
    [i for i in range(1, 6)], initial_value=1, s=(2), key='subscriptions-quantity')
user_output_element = sg.Multiline(
    size=(75, 15), key='user-output-elem', visible=False, reroute_stdout=True)
user_validate_btn = sg.Button(
    button_text='Проверить и запустить', key='user-validate-btn')
user_about_btn = sg.Button(button_text='О программе', key='user-about-btn')
user_quit_btn = sg.Button(button_text='Выход', key='user-quit-btn')

### ABOUT TEXT ###
about_text = f'Программа для поиска и оплаты подписок на парковки A-Parking(Almaty).\nДата сборки: {today}\nMMV'

### USER WINDOW LAYOUT ###
user_layout = [
    [sg.Push(), user_output_element, sg.Push()],
    [checkbox_proxy, sg.Push()],
    [sg.pin(http_proxy_text), sg.Push(), http_proxy_field],
    [sg.pin(https_proxy_text), sg.Push(), https_proxy_field],
    [user_login_text, sg.Push(), user_login_field],
    [user_pin_text, sg.Push(), user_pin_field],
    [user_car_text, sg.Push(), user_car_field],
    [user_zone_text, sg.Push(), user_zone_field],
    [subcrtiptions_quantity_text, subcrtiptions_quantity_field, sg.Push()],
    [user_validate_btn, sg.Push(), user_about_btn, sg.Push(), user_quit_btn]
]

### CREATE USER WINDOW ###
user_window = sg.Window('Catch&Pay A-Parking Subscription', user_layout)

while True:
    event, value = user_window.read()

    if event in (None, 'user-quit-btn'):
        logging.warning('Script job interrupted by user, exiting')
        exit()

    if event in ('user-about-btn'):
        sg.popup_ok(about_text, title='О программе')

    if value['check-proxy'] == True:
        http_proxy_text.Update(visible=True)
        https_proxy_text.Update(visible=True)
        http_proxy_field.Update(visible=True)
        https_proxy_field.Update(visible=True)
        if value['http-proxy'] == 'None' or value['http-proxy'] == '':
            proxies['http'] = None
        else:
            proxies['http'] = value['http-proxy']

        if value['https-proxy'] == 'None' or value['https-proxy'] == '':
            proxies['https'] = None
        else:
            proxies['https'] = value['http-proxy']
    else:
        http_proxy_text.Update(visible=False)
        https_proxy_text.Update(visible=False)
        http_proxy_field.Update(visible=False)
        https_proxy_field.Update(visible=False)
        proxies = {
            'http': None,
            'https': None,
        }

    if event == 'user-validate-btn':
        count_req_fields = 0

        if not re.match('^\+7[\d]{10}$', value['user-login']):
            sg.popup(
                'Неверный формат логина, пример: +7xxxxxxxxxx\nПроверьте заполненные поля и попробуйте снова.')
        else:
            count_req_fields += 1
        if not re.match('^[\d]+$', value['user-pin']):
            sg.popup(
                'Неверный формат пароля, только цифры\nПроверьте заполненные поля и попробуйте снова.')
        else:
            count_req_fields += 1
        if not re.match('^[A-Z,\d]{7,}$', value['user-car'].upper()):
            sg.popup('Неверный формат гос. номера, не меньше 7 символов, цифры и латинские буквы\nПроверьте заполненные поля и попробуйте снова.')
        else:
            count_req_fields += 1
        if not re.match('^[\d]{4}$', value['user-zone']):
            sg.popup(
                'Неверный формат зоны, только 4 цифры\nПроверьте заполненные поля и попробуйте снова.')
        else:
            count_req_fields += 1

        if count_req_fields == 4:
            user_login = value['user-login']
            user_pin = value['user-pin']
            user_car = value['user-car'].upper()
            user_zone = value['user-zone']
            subcrtiptions_quantity = value['subscriptions-quantity']

            ### HIDE UNNECCESSARY ELEMENTS AND SHOW OUTPUT ###
            checkbox_proxy.Update(visible=False)
            http_proxy_text.Update(visible=False)
            http_proxy_field.Update(visible=False)
            https_proxy_text.Update(visible=False)
            https_proxy_field.Update(visible=False)
            user_login_text.Update(visible=False)
            user_login_field.Update(visible=False)
            user_pin_text.Update(visible=False)
            user_pin_field.Update(visible=False)
            user_car_text.Update(visible=False)
            user_car_field.Update(visible=False)
            user_zone_text.Update(visible=False)
            user_zone_field.Update(visible=False)
            subcrtiptions_quantity_text.Update(visible=False)
            subcrtiptions_quantity_field.Update(visible=False)
            user_validate_btn.Update(visible=False)
            user_quit_btn.Update(visible=False)
            user_about_btn.Update(visible=False)
            user_output_element.Update(visible=True)

            user_window.refresh()

            login_data = {
                'page': 'login',
                'username': user_login,
                'password': user_pin,
                'login': 'Залогиниться',
                '_reqNo': '0'
            }

            ############################################################################
            ##### MAKING REQUESTS(LOGIN->GET SUBSCRIPTIONS PAGE->PAY SUBSCRIPTION) #####
            count_subscriptions = 0
            ############################################################################
            ##### MAKING REQUESTS(LOGIN->GET SUBSCRIPTIONS PAGE->PAY SUBSCRIPTION) #####
            count_subscriptions = 0

            while count_subscriptions < int(subcrtiptions_quantity):
                print(datetime.now(), '\nНачат поиск подписки',
                      (count_subscriptions + 1), '/', subcrtiptions_quantity)
                user_window.refresh()
                #sg.Print(str(datetime.now()) + 'dfdf')
                user_window.refresh()
                with requests.Session() as s:
                    def logging_in():
                        ### LOGGING-IN A-PARKING FUNCTION, TRYING RETRY ON REQUEST ERRORS ###
                        print('Пытаемся залогиниться...')
                        user_window.refresh()
                        request_try = True
                        count_request_try = 1
                        while request_try == True:
                            try:
                                login = s.post(
                                    a_parking_url,
                                    data=login_data,
                                    headers=headers,
                                    proxies=proxies,
                                    verify=False,
                                    timeout=300
                                )
                                request_try = False
                            except:
                                print('Ошибка, пытаемся повторить запрос...')
                                user_window.refresh()
                                logging.exception('Exceptioned:')
                                count_request_try += 1
                                if count_request_try > request_attempts:
                                    request_try = False
                                    print('Превышено количество попыток повторить запрос',
                                          request_attempts, 'прерываем исполнение...')
                                    user_window.refresh()
                                    logging.error(
                                        'Request attempts exceeded, attempts exceeded...')
                                    result_list.append(
                                        'ОШИБКА: проверьте подключение и/или настройки прокси!')
                                    show_result()
                                else:
                                    print('Пытаемся получить корректный ответ, попытка',
                                          count_request_try, 'из', request_attempts)
                                    user_window.refresh()
                                    logging.warning(
                                        'Exceptioned:, retrying...')
                                    sleep(2)
                        logging.info('Logging in status code: ' +
                                     str(login.status_code))

                        if 'Здравствуйте' not in login.text:
                            print(
                                'ОШИБКА: при попытке залогиниться, проверьте правильность данных и повторите запуск')
                            user_window.refresh()
                            logging.error(
                                'FAILURE: failed to log in, check creds!')
                            result_list.append(
                                'ОШИБКА: проверьте логин и пароль!')
                            show_result()
                        else:
                            print('УСПЕХ: залогинились!')
                            user_window.refresh()

                        ### (OPTIONAL) LOOKUP FOR NOWSESS COOKIE DATA ###

                        # DEBUG print('Finding Request Cookies for Payment...')
                        nowsess_pattern = '^nowsess=(\w+);'
                        nowsess_cookie = re.findall(
                            nowsess_pattern, login.request.headers['Cookie'])[0]
                        session_cookies = {
                            'nowsess': nowsess_cookie
                        }
                        logging.info('Nowsess cookie value is: ' +
                                     str(session_cookies['nowsess']))
                    ### TRYING TO LOG IN A-PARKING ###
                    logging_in()

                    print('Ищем нужную подписку...')
                    user_window.refresh()
                    flag = False
                    count_attempt = 1
                    while flag == False:
                        ### GETTING A-PARKING SUBSCRIPTIONS PAGE, TRYING RETRY ON REQUEST ERRORS ###
                        request_try = True
                        count_request_try = 1
                        while request_try == True:
                            try:
                                subscriptions = s.get(
                                    a_parking_subscriptions_url,
                                    headers=headers,
                                    proxies=proxies,
                                    verify=False,
                                    timeout=300
                                )
                                request_try = False
                            except:
                                print('Ошибка, пытаемся повторить запрос...')
                                user_window.refresh()
                                logging.exception('Exceptioned:')
                                count_request_try += 1
                                if count_request_try > request_attempts:
                                    request_try = False
                                    print('Превышено количество попыток повторить запрос',
                                          request_attempts, 'прерываем исполнение...')
                                    user_window.refresh()
                                    logging.error(
                                        'Request attempts exceeded, attempts exceeded...')
                                    result_list.append(
                                        'ОШИБКА: проверьте подключение и/или настройки прокси!')
                                    show_result()
                                else:
                                    print('Пытаемся получить корректный ответ, попытка',
                                          count_request_try, 'из', request_attempts)
                                    user_window.refresh()
                                    logging.warning(
                                        'Exceptioned:, retrying...')
                                    sleep(2)

                        if 'subscriptionCost' not in subscriptions.text:
                            print(
                                'ОШИБКА: не удалось получить список, ошибка сессии, пытаемся перелогиниться')
                            user_window.refresh()
                            logging.warning(
                                'SESSION: most propably, session is dead, retrying to login')
                            count_attempt += 1
                            logging_in()
                            continue

                        ### LOOKING UP FOR USER ZONE ###
                        soup = BeautifulSoup(
                            subscriptions.content, 'html.parser')
                        subscriptionCost = soup.find(id='subscriptionCost')
                        zones_n_values_parse = subscriptionCost.find_all(
                            'option')
                        zone_pattern = '^.*(\d{4}).*<\/option>$'
                        zones = []
                        for i in zones_n_values_parse:
                            find_zone = re.findall(zone_pattern, str(i))
                            if len(find_zone) == 0:
                                find_zone.append('NA')
                            zones.append(find_zone[0])
                        values = [value['value']
                                  for value in zones_n_values_parse]
                        zone_n_values_dict = {zones[i]: values[i]
                                              for i in range(len(zones))}
                        for key in zone_n_values_dict.keys():
                            if key == user_zone:
                                subscription_value = zone_n_values_dict[key]
                                print('Пользовательсая Зона', user_zone,
                                      'НАЙДЕНА!', 'Код подписки:', subscription_value)
                                user_window.refresh()
                                payment_data = {
                                    'carNo': user_car,
                                    'subscriptionCost': subscription_value,
                                    'page': 'subscriptions',
                                    'operation': 'addSubscription',
                                    'pay': 'Оплатить',
                                    '_reqNo': 1
                                }
                                print('Пытаемся оплатить подписку', user_zone)
                                user_window.refresh()

                                ### MAKING PAYMENT RESPONSE, TRYING RETRY ON REQUEST ERRORS ###
                                request_try = True
                                count_request_try = 1
                                while request_try == True:
                                    try:
                                        pay_subscription = s.post(
                                            a_parking_url,
                                            data=payment_data,
                                            headers=headers,
                                            proxies=proxies,
                                            verify=False,
                                            timeout=300
                                        )
                                        request_try = False
                                    except:
                                        print(
                                            'Ошибка, пытаемся повторить запрос...')
                                        user_window.refresh()
                                        logging.exception('Exceptioned:')
                                        count_request_try += 1
                                        if count_request_try > request_attempts:
                                            request_try = False
                                            print('Превышено количество попыток повторить запрос',
                                                  request_attempts, 'прерываем исполнение...')
                                            user_window.refresh()
                                            logging.error(
                                                'Request attempts exceeded, attempts exceeded...')
                                            result_list.append(
                                                'ОШИБКА: проверьте подключение и/или настройки прокси!')
                                            show_result()
                                        else:
                                            print('Пытаемся получить корректный ответ, попытка',
                                                  count_request_try, 'из', request_attempts)
                                            user_window.refresh()
                                            logging.warning(
                                                'Exceptioned:, retrying...')
                                            sleep(2)

                                logging.info(
                                    'Pay Subscription requset headers:\n' + str(pay_subscription.request.body))
                                logging.info(
                                    'Pay Subscription status code is: ' + str(pay_subscription.status_code))
                                logging.info(
                                    'Pay Subscription requset headers:\n' + str(pay_subscription.request.headers))

                                ### CHECKING PAYMENT RESPONSE ###
                                if 'На вашем счету недостаточно средств' in pay_subscription.text:
                                    print(
                                        'НЕДОСТАТОЧНО СРЕДСТВ, ПРОВЕРЬТЕ СВОЙ БАЛАНС')
                                    user_window.refresh()
                                    count_subscriptions += 1
                                    '''
                                    subscriptions_list.append(
                                        'Подписка' + str(count_subscriptions) + '. ' + 'Недостаточно средств на балансе')
                                    '''
                                    result_list.append(
                                        'Подписка' + str(count_subscriptions) + '. ' + 'Недостаточно средств на балансе')
                                    logging.warning(
                                        'Недостаточно средств на балансе')
                                    result_list.append(
                                        'ОШИБКА: недостаточно средств на балансе')
                                    show_result()

                                elif pay_subscription.status_code == 200 and 'Разрешение на парковку' in pay_subscription.text:
                                    print('ПЛАТЁЖ УСПЕШНО ПРОИЗВЕДЁН!')
                                    user_window.refresh()
                                    soup = BeautifulSoup(
                                        pay_subscription.content, 'html.parser')
                                    result = str(soup.find('div', {'class': 'warning'})).strip(
                                        '</div class="warning">').strip()
                                    print('Информация о платеже:\n', result)
                                    user_window.refresh()
                                    count_subscriptions += 1

                                    result_list.append(
                                        str(count_subscriptions) + '. ' + result)
                                    logging.info('PAYMENT SUCCESS:\n' + result)
                                    estimated_time()
                                    print('----------------------------\n')
                                    user_window.refresh()
                                    flag = True
                                else:
                                    print('ОШИБКА: получен неожиданный ответ:', pay_subscription.status_code,
                                          pay_subscription.request.headers, pay_subscription.request.body, sep='\n')
                                    logging.info(
                                        'RESPONSE UNSUSPECTED, check response file.')
                                    result_list.append(
                                        'ОШИБКА: получен неожиданный ответ:' + pay_subscription.status_code)
                                    show_result()

                        count_attempt += 1
                        sleep(2)
                        user_window.refresh()
            result_list.append('Работа завершена')
            show_result()
