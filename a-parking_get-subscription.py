#!/usr/bin/env python3

'''
This script is automatization of seraching and bying
Almaty A-Parking Subscriptions.
'''

import logging
from unittest import result
import requests
import urllib3
from datetime import datetime
from time import sleep
from os import mkdir, path
from sys import exit
import re

### DEFINING WORK DIR(SCRIPT'S LOCATION) ###
work_dir = 'D:/Docs-marchenm/Scripts/Python/A-parking_get-subscription'

###########################
##### LOGGING SECTION #####

### DEFINING SCRIPT'S START TIME ###
start_date = datetime.now()

logs_dir = work_dir+'/logs'

if not path.isdir(logs_dir):
    mkdir(logs_dir)

app_log_name = logs_dir+'/a-parking_get-subscription_log_' + \
    str(start_date.strftime('%d-%m-%Y'))+'.log'
logging.basicConfig(filename=app_log_name, filemode='w', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%Y %H:%M:%S')

logging.info('SCRIPT WORK STARTED: GET & PAY A-PARKING SUBSCRIPTION')
logging.info('Script Starting Date&Time is: ' +
             str(start_date.strftime('%d/%m/%Y %H:%M:%S')) + '\n')

### TRYING TO ADD EXTERNAL MODULES ###
try:
    from bs4 import BeautifulSoup
except:
    print('FAILED to load bs4(BeautifulSoup) module, check log')
    logging.exception('FAILURE: load bs4 module, exiting')
    exit()

try:
    from pwinput import pwinput
except:
    print('FAILED to load pwinput module, check log')
    logging.exception('FAILURE: load pwinput module, exiting')
    exit()

### DISABLE SSL WARNING MESSAGES ###
urllib3.disable_warnings()

#####################
##### USER DATA #####

##### PROXIES #####
user_proxy = input('Do you want to use proxy server for connections? [yes|no/blank] (NO - is defaulut): ')

### NUMBER OF ATTEMPTS FOR EVERY GET/POST REQUEST ###
request_attempts = 10

### PROXY DETAILS ###
if user_proxy == 'yes':
    http_proxy = input('Input HTTP proxy(example: http://proxy.example.com:8080): ')
    https_proxy = input('Input HTTPS proxy(example: http(s)://proxy.example.com:8080): ')
    proxies = {
        'http': http_proxy,
        'https': https_proxy,
    }
else:
    print('No proxy needed, skipping')
    proxies = {
        'http': None,
        'https': None,
    }
 
### INPUT USER'S A-PAKRING LOGIN ###
user_login = input('Input your LOGIN and press ENTER(+7xxxxxxxxxx): ')
while not re.match('^\+7[\d]{10}$', user_login):
    print('Not correct LOGIN, must be like.: +7xxxxxxxxxx')
    user_login = input('Input your CORRECT A-Parking LOGIN and press ENTER(+7xxxxxxxxxx): ')

logging.info('USER IS: ' + str(user_login))

### INPUT USER'S A-PARKING PIN ##
user_pin = pwinput(prompt = 'Input your A-Parking PIN and press ENTER(xxxx): ')
while not re.match('^[\d]*$', user_pin):
    print('Not correct PIN, must be ONLY numbers, ex.:1234')
    user_pin = pwinput(prompt = 'Input your CORRECT A-Parking PIN and press ENTER: ')

### INPUT A-PAKRING ZONE TO PAY ###
user_zone = input('Input your A-Parking ZONE and press ENTER(xxxx): ')
while not re.match('^[\d]{4}$', user_zone):
    print('Not correct ZONE, must be 4 numbers, ex.:1234')
    user_zone = input('Input your CORRECT A-Parking ZONE and pres ENTER: ')

logging.info('LOOKUP FOR ZONE: ' + str(user_zone))

### INPUT USER'S CAR NUMBER ###
user_car = input('Input your CAR NUMBER(check your A-Parking cabinet) and press ENTER: ')

logging.info('USER CAR NUMBER IS: ' + str(user_car))

### NUMS OF SUBSCRIPTIONS ###
subcrtiptions_quantity = input('How many subcriptions you are going to pay?(NOT MORE THAN 5, DON\'T BE GREEDY!): ')
while (subcrtiptions_quantity) == '0' or (subcrtiptions_quantity) > '5':
    subcrtiptions_quantity = input('Enter num than MORE than 0 and LESS than 6: ')
logging.info('NUM OF SUBSCRIPTIONS TO PAY: ' + subcrtiptions_quantity)
subscriptions_list = []

################################
##### FILES & FOLDERS VARS #####

response_dir = work_dir+'/response'

a_parking_logon_response = response_dir + '/a_parking_logon_response.html'
a_parking_subscriptions_response = response_dir + '/a_parking_subscriptions_response.html'
a_parking_subscriptions_list = response_dir + '/a_parking_subscriptions_response_list.txt'
a_parking_payment_response = response_dir + '/a_parking_payment_response.html'

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

login_data = {
    'page': 'login',
    'username': user_login,
    'password': user_pin,
    'login': 'Залогиниться',
    '_reqNo': '0'
}
# '%D0%97%D0%B0%D0%BB%D0%BE%D0%B3%D0%B8%D0%BD%D0%B8%D1%82%D1%8C%D1%81%D1%8F' = 'Залогиниться'
# '%D0%9E%D0%BF%D0%BB%D0%B0%D1%82%D0%B8%D1%82%D1%8C' = 'Оплатить'

############################
##### HELPER FUNCTIONS #####

### COUNT ESTIMATED TIME ###
def estimated_time():
    end_date = datetime.now()
    print('Estimated time is:', end_date - start_date)
    logging.info('Estimated time is: ' + str(end_date - start_date))
    print('Last Attempts count is: ', count_attempt)
    logging.info('Attempts count is: ' + str(count_attempt))
    print('----------------------------\n')

### PRINT CURRENT/FINAL PROCESSED SUBSCRIPTIONS ###
def print_final_subscription_list():
    print('')
    print('FINAL Subscriptions List:')
    print(*subscriptions_list, sep='\n')
    print('')
    estimated_time()

##################################
##### PRE PROCESSING ACTIONS #####

if not path.isdir(response_dir):
    mkdir(response_dir)

############################################################################
##### MAKING REQUESTS(LOGIN->GET SUBSCRIPTIONS PAGE->PAY SUBSCRIPTION) #####

count_subscriptions = 0
print('----------------------------')
while count_subscriptions < int(subcrtiptions_quantity):
    print(datetime.now(), 'Getting subscription', (count_subscriptions + 1), '/', subcrtiptions_quantity)
    with requests.Session() as s:
        def logging_in():
            ### LOGGING-IN A-PARKING FUNCTION, TRYING RETRY ON REQUEST ERRORS ###
            print('Trying to Login...')
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
                    print('Exceptioned, retrying to get proper answer...')
                    logging.exception('Exceptioned:')
                    count_request_try += 1
                    if count_request_try > request_attempts:
                        request_try = False
                        print('Request attempts exceeded', request_attempts, 'exiting...')
                        logging.error('Request attempts exceeded, attempts exceeded...')
                        exit()
                    else:
                        print('Retrying to get proper answer, attempt', count_request_try, 'of', request_attempts)
                        logging.warning('Exceptioned:, retrying...')
                        sleep(2)
            #DEBUG print(login.request.url)
            #DEBUG print(login.request.headers)
            #DEBUGprint(login.status_code)
            #DEBUG print(login.request.body)
            logging.info('Logging in status code: ' + str(login.status_code))
            
            if 'Здравствуйте' not in login.text:
                print('FAILED to Login(check login/pass), exiting')
                logging.error('FAILURE: failed to log in, check creds!')
                exit()
            else:
                print('Login Attempt SUCCESS')

            ### (OPTIONAL) LOOKUP FOR NOWSESS COOKIE DATA ###
        
            #DEBUG print('Finding Request Cookies for Payment...')
            nowsess_pattern = '^nowsess=(\w+);'
            nowsess_cookie = re.findall(nowsess_pattern, login.request.headers['Cookie'])[0]
            session_cookies = {
                'nowsess': nowsess_cookie
            }
            #DEBUG print('nowsess value is:', session_cookies['nowsess'])
            logging.info('Nowsess cookie value is: ' + str(session_cookies['nowsess']))
        
        ### TRYING TO LOG IN A-PARKING ###
        logging_in()

        ### DEBUG: WRITING LOG-IN RESPONSE
        #with open(a_parking_logon_response, 'w', encoding='utf-8') as f:
        #       print(login.text, file=f)
        #       f.close()
        
        print('Looking up for A-Parking Subscription...')
        flag = False
        count_attempt = 1
        while flag == False:
            ### GETTING A-PARKING SUBSCRIPTIONS PAGE, TRYING RETRY ON REQUEST ERRORS ###
            #DEBUG print(datetime.now(), 'Getting Subscriptions List, ATTEMPT:', count_attempt)
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
                    print('Exceptioned, retrying to get proper answer...')
                    logging.exception('Exceptioned:')
                    count_request_try += 1
                    if count_request_try > request_attempts:
                        request_try = False
                        print('Request attempts exceeded', request_attempts, 'exiting...')
                        logging.error('Request attempts exceeded, attempts exceeded...')
                        exit()
                    else:
                        print('Retrying to get proper answer, attempt', count_request_try, 'of', request_attempts)
                        logging.warning('Exceptioned:, retrying...')
                        sleep(2)
            #DEBUG print(subscriptions.request.url)
            #DEBUG print(subscriptions.request.headers)
            #DEBUG print(subscriptions.status_code)
            if 'subscriptionCost' not in subscriptions.text:
                print('FAILED to get Subscriptons Data, retrying to login')
                logging.warning('SESSION: most propably, session is dead, retrying to login')
                count_attempt += 1
                print('IF SUBSCRIPTION COST count_attempt:', count_attempt)
                logging_in()
                continue

            ### LOOKING UP FOR USER ZONE ###
            soup = BeautifulSoup(subscriptions.content, 'html.parser')
            subscriptionCost = soup.find(id='subscriptionCost')
            zones_n_values_parse = subscriptionCost.find_all('option')
            zone_pattern = '^.*(\d{4}).*<\/option>$'
            zones = []
            for i in zones_n_values_parse:
                find_zone = re.findall(zone_pattern, str(i))
                if len(find_zone) == 0:
                    find_zone.append('NA')
                zones.append(find_zone[0])
            values = [value['value'] for value in zones_n_values_parse]
            zone_n_values_dict = {zones[i]: values[i] for i in range(len(zones))}
            for key in zone_n_values_dict.keys():
                if key == user_zone:
                    subscription_value = zone_n_values_dict[key]
                    print('User Zone', user_zone, 'FOUND!', 'Subsctription value is:', subscription_value)
                    payment_data = {
                        'carNo': user_car,
                        'subscriptionCost': subscription_value,
                        'page': 'subscriptions',
                        'operation': 'addSubscription',
                        'pay': 'Оплатить',
                        '_reqNo': 1
                    }
                    print('Making Payment with user Zone', user_zone)
            
                    ### MAKING PAYMENT RESPONSE, TRYING RETRY ON REQUEST ERRORS ###
                    request_try = True
                    count_request_try = 1
                    while request_try == True:
                        try:
                            pay_subscription = s.post(
                                a_parking_url,
                                data=payment_data,
                                headers=headers,
                                #cookies=session_cookies,
                                proxies=proxies, 
                                verify=False,
                                timeout=300
                            )
                            request_try = False
                        except:                     
                            print('Exceptioned, retrying to get proper answer...')
                            logging.exception('Exceptioned:')
                            count_request_try += 1
                            if count_request_try > request_attempts:
                                request_try = False
                                print('Request attempts exceeded', request_attempts, 'exiting...')
                                logging.error('Request attempts exceeded, attempts exceeded...')
                                exit()
                            else:
                                print('Retrying to get proper answer, attempt', count_request_try, 'of', request_attempts)
                                logging.warning('Exceptioned:, retrying...')
                                sleep(2)

                    #DEBUG print(pay_subscription.request.url)
                    #DEBUG print(pay_subscription.request.headers)
                    #DEBUG print(pay_subscription.status_code)
                    logging.info('Pay Subscription requset headers:\n' + str(pay_subscription.request.body))
                    logging.info('Pay Subscription status code is: ' + str(pay_subscription.status_code))
                    logging.info('Pay Subscription requset headers:\n' + str(pay_subscription.request.headers))
                    #DEBUG print(pay_subscription.request.body)
                    
                    ### WRITING DOWN PAYMENT RESPONSE ###
                    with open(a_parking_payment_response, 'w', encoding='utf-8') as f:
                        print(pay_subscription.text, file=f)
                        f.close()
                    
                    ### CHECKING PAYMENT RESPONSE ###
                    if 'На вашем счету недостаточно средств' in pay_subscription.text:
                        print('NO SUFFICIENT FUNDS, CHECK YOUR BALANCE! EXITING')
                        count_subscriptions += 1
                        subscriptions_list.append(str(count_subscriptions) + '. ' + 'No sufficient funds, check your balance, exiting')
                        logging.warning('No sufficient funds, check your balance, exiting')
                        print_final_subscription_list()
                        exit()
                    elif pay_subscription.status_code == 200 and 'Разрешение на парковку' in pay_subscription.text:
                        print('PAYMENT SUCCESS!')
                        soup = BeautifulSoup(pay_subscription.content, 'html.parser')
                        result = str(soup.find('div', {'class': 'warning'})).strip('</div class="warning">').strip()
                        print('Payment Info:\n', result)
                        count_subscriptions += 1
                        subscriptions_list.append(str(count_subscriptions) + '. ' + result)
                        logging.info('PAYMENT SUCCESS:\n' + result)
                        estimated_time()
                        print('----------------------------\n')
                        flag = True
                    else:
                        print('RESPONSE UNSUSPECTED, check response file.')
                        logging.info('RESPONSE UNSUSPECTED, check response file.')
                        print(pay_subscription.request.headers)
                        print(pay_subscription.status_code)
                        print(pay_subscription.request.body)
                        print_final_subscription_list()
                        exit()

            count_attempt += 1
            #DEBUG print('ZONE NOT FOUND: Sleeping for 2 seconds before next attempt')
            sleep(2)

print('###########################')
print('DONE Script job!\n')
print_final_subscription_list()