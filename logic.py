from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
import json
import codecs
import urllib.parse as urllib
from datetime import datetime, timedelta
import sys
import time

# Получение формата даты
def getDateFormat(with_time = False):
    if with_time:
        return '%d.%m.%y %H:%M:%S'
    else:
        return '%d.%m.%Y'

# Очистка старых логов
def discardOldLogs(max_log_length):
    try:
        with codecs.open('errors.log', 'r', encoding='utf-8') as f:
            errors = f.readlines()
        if len(errors) > max_log_length:
            with codecs.open('errors.log', 'w', encoding='utf-8') as f:
                f.write(errors[-max_log_length:])
    except:
        pass
    try:
        with codecs.open('results.log', 'r', encoding='utf-8') as f:
            errors = f.readlines()
        if len(errors) > max_log_length:
            with codecs.open('results.log', 'w', encoding='utf-8') as f:
                f.write(errors[-max_log_length:])
    except:
        pass

# Запись логов
def writeLog(logEntry, isError=False):
    logEntry = str(logEntry)
    if isError:
        try:
            sys.stderr.write(logEntry)
        except:
            pass
        with codecs.open('errors.log', 'a', encoding='utf-8') as f:
            f.write(logEntry + '\n')
    else:
        try:
            print(logEntry)
        except:
            pass
        with codecs.open('results.log', 'a', encoding='utf-8') as f:
            f.write(logEntry + '\n')

# Чтение конфигов
def readConfigs(parser_config_path, subscriptions_config_path):
    parser_config = None
    subscriptions_config = None
    try:
        with codecs.open(parser_config_path, encoding='utf-8') as f:
            parser_config = json.load(f)
    except Exception as e:
        writeLog({'time': datetime.now().strftime(getDateFormat(True)), 'error': f'Не удалось прочитать {parser_config_path}. Проверьте, что файл лежит в той же папке, что и скрит, и что в файле валидный JSON.', 'stackTrace': str(e)}, True)
    try:
        with codecs.open(subscriptions_config_path, encoding='utf-8') as f:
            subscriptions_config = json.load(f)
    except Exception as e:
        writeLog({'time': datetime.now().strftime(getDateFormat(True)), 'error': f'Не удалось прочитать {subscriptions_config_path}. Проверьте, что файл лежит в той же папке, что и скрит, и что в файле валидный JSON.', 'stackTrace': str(e)}, True)
    return parser_config, subscriptions_config

# Подготовка контента для письма
def generateHtml(data, subscription, tender_types_enum):
    fltr = subscription['filter']
    html = f'<p>Выборка по фильтру {subscription["name"]}:<p>'
    html += '<ul>'
    if fltr.get('daysBackPublished') and fltr.get('daysBackPublished') > 0:
        date_from = (datetime.today() - timedelta(days=fltr.get('daysBackPublished'))).strftime(getDateFormat())
        date_to = datetime.today().strftime(getDateFormat())
    else:
        date_from = datetime.today()
        date_to = datetime.today()
    if fltr.get('minPrice'):
        min_price = fltr.get('minPrice')
    else:
        min_price = 0
    if fltr.get('maxPrice'):
        max_price = fltr.get('maxPrice')
    else:
        max_price = 999999999
    html += f'<li>Период публикации: {date_from} - {date_to}</li>'
    html += f'<li>Цена: {min_price} - {max_price}</li>'
    html += f'<li>Ключевые слова: {"|".join(fltr.get("keywords"))}</li>'
    tender_types = 'Любые'
    if fltr.get('tenderTypes') and len(fltr.get('tenderTypes')) > 0 and len(tender_types_enum) > 0:
        tender_types_array = []
        for t_t in fltr.get('tenderTypes'):
            name = 'Неизвестно'
            for t_e in tender_types_enum:
                if str(t_t) == str(t_e['id']):
                    name = t_e['name']
            tender_types_array.append(name)
        tender_types = ', '.join(tender_types_array)
    html += f'<li>Типы процедуры: {tender_types}</li>'
    if fltr.get('organizerOrCustomer') and fltr.get('organizerOrCustomer').get('name') and fltr.get('organizerOrCustomer').get('type') and len(fltr.get('organizerOrCustomer')['name']) > 0:
        if fltr.get('organizerOrCustomer').get('type') == 'organizer':
            html += f'<li>Организатор: {fltr.get("organizerOrCustomer").get("name")}</li>'
            html += f'<li>Заказчик: Любой</li>'
        else:
            html += f'<li>Организатор: Любой</li>'
            html += f'<li>Заказчик: {fltr.get("organizerOrCustomer").get("name")}</li>'
    html += '</ul>'
    hasStuff = {}
    for item in data:
        if item.get('number'):
            hasStuff['hasNumber'] = True
        if item.get('linkText'):
            hasStuff['hasLinkText'] = True
        if item.get('price'):
            hasStuff['hasPrice'] = True
        if item.get('type'):
            hasStuff['hasType'] = True
        if item.get('organizer'):
            hasStuff['hasOrganizer'] = True
        if item.get('customer'):
            hasStuff['hasCustomer'] = True
    number_header = '<th>Номер закупки</th>' if hasStuff.get("hasNumber") else ''
    link_header = '<th>Ссылка</th>' if hasStuff.get("hasLinkText") else ''
    price_header = '<th>Цена</th>' if hasStuff.get("hasPrice") else ''
    type_header = '<th>Тип</th>' if hasStuff.get("hasType") else ''
    organizer_header = '<th>Организатор</th>' if hasStuff.get("hasOrganizer") else ''
    customer_header = '<th>Заказчик</th>' if hasStuff.get("hasCustomer") else ''
    html += f'''
        <table>
            <thead>
                <tr>
                    {number_header}
                    {link_header}
                    {price_header}
                    {type_header}
                    {organizer_header}
                    {customer_header}
                </tr>
            </thead>
            <tbody>
    '''
    for item in data:
        number = f'<td>{item.get("number")}</td>' if item.get("number") else ''
        link = f'<td><a href="{item.get("linkHref")}">{item.get("linkText")}</a></td>' if item.get("linkText") else ''
        price = f'<td>{item.get("price")}</td>' if item.get("price") else ''
        typ = f'<td>{item.get("type")}</td>' if item.get("type") else ''
        organizer = f'<td>{item.get("organizer")}</td>' if item.get("organizer") else ''
        customer = f'<td>{item.get("customer")}</td>' if item.get("customer") else ''
        html += f'''
            <tr>
                {number}
                {link}
                {price}
                {typ}
                {organizer}
                {customer}
            </tr>
        '''
    html += '</tbody></table>'
    with codecs.open('email.html', 'a', encoding='utf-8') as f:
        f.write(html)
        f.write('\n')
    return html
    
# Отправка письма с результатом
def sendEmail(to, subject, html):
    HOST = "mail.smartchein.ru"
    fro = "info@smartchein.ru"
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = fro
    msg['To'] = to
    html = html
    msg.attach(MIMEText(html, 'html'))
    # server = smtplib.SMTP(HOST,587)
    # server.login('info@smartchein.ru','scinfo_76589')
    # server.sendmail(fro, to, msg.as_string())
    # server.quit()
    writeLog({
        'time': datetime.now().strftime(getDateFormat(True)),
        'message': f"Отправлено письмо на почту {to} с темой {subject}. Длина контента {len(html)}"
    })

# Парсинг fabrikant.ru
def parseFabrikant(config, fltr, driver, subscription):
    # Заходим на основной урл, чтобы получить куки и сессию
    driver.get(config['url'])

    # Генерируем урл с фильтрами
    url_params = config['values']['URL_PARAMS']
    if fltr.get('daysBackPublished') and fltr.get('daysBackPublished') > 0:
        url_params['date_from'] = (datetime.today() - timedelta(days=fltr.get('daysBackPublished'))).strftime(getDateFormat())
        url_params['date_to'] = datetime.today().strftime(getDateFormat())
    else:
        url_params['date_from'] = datetime.today()
        url_params['date_to'] = datetime.today()
    regions_params = []
    if fltr.get('regions') and len(fltr.get('regions')) > 0:
        region_param_name = config['values']['REGIONS_PARAM_NAME']
        for region in fltr.get('regions'):
            regions_params.append((region_param_name, region))
    if fltr.get('minPrice') and fltr.get('minPrice') > 0:
        url_params['price_from'] = fltr.get('minPrice')
    if fltr.get('maxPrice') and fltr.get('maxPrice') > 0:
        url_params['price_to'] = fltr.get('maxPrice')
    if fltr.get('maxPrice') and fltr.get('minPrice') and  fltr.get('maxPrice') < fltr.get('minPrice'):
        writeLog({'time': datetime.now().strftime(getDateFormat(True)), 'error': f'Минимальная цена {fltr.get("minPrice")} больше максимальной {fltr.get("maxPrice")} по подписке {subscription["name"]}'}, True)
        return []
    types_params = []
    if fltr.get('tenderTypes') and len(fltr.get('tenderTypes')) > 0:
        type_param_name = config['values']['TYPE_PARAM_NAME']
        for tender_type in fltr.get('tenderTypes'):
            types_params.append((type_param_name, tender_type))
    if fltr.get('organizerOrCustomer') and fltr.get('organizerOrCustomer').get('name') and fltr.get('organizerOrCustomer').get('type') and len(fltr.get('organizerOrCustomer')['name']) > 0:
        org_name = fltr.get('organizerOrCustomer')['name']
        org_type = config['values']['ORGANIZER'] if fltr.get('organizerOrCustomer')['type'] == 'organizer' else config['values']['CUSTOMER']
        org_id = driver.execute_script(config['values']['SCRIPT'].format(org_name, org_type))
        url_params['org[]'] = org_id
        url_params['org_type'] = org_type
    else:
        url_params.pop('org[]', None)
    
    # Перебираем кейворды, парсим каждый, сохраняем информацию в общий массив
    data = []
    for query in fltr['keywords']:
        page_num = 1
        while True:
            url_params['query'] = query
            url_params['page'] = page_num
            url = config['values']['URL_WITH_FILTERS'] + urllib.urlencode(url_params)
            if len(regions_params) > 0:
                url = url + '&' + urllib.urlencode(regions_params)
            if len(types_params) > 0:
                url = url + '&' + urllib.urlencode(types_params)
            driver.get(url)
            items = driver.find_elements(config['locators']['ITEM']['by'], config['locators']['ITEM']['selector'])
            if len(items) > 0:
                for item in items:
                    try:
                        link = item.find_element(config['locators']['ITEM_LINK']['by'], config['locators']['ITEM_LINK']['selector'])
                        link_text = link.text
                        link_href = link.get_attribute('href')
                    except:
                        link_text = None
                        link_href = None
                    try:
                        price = item.find_element(config['locators']['ITEM_PRICE']['by'], config['locators']['ITEM_PRICE']['selector']).text
                    except:
                        price = None
                    try:
                        number = item.find_element(config['locators']['ITEM_NUMBER']['by'], config['locators']['ITEM_NUMBER']['selector']).text
                    except:
                        number = None
                    try:
                        organizer = item.find_element(config['locators']['ITEM_ORGANIZER']['by'], config['locators']['ITEM_ORGANIZER']['selector']).text
                    except:
                        organizer = None
                    try:
                        customer = item.find_element(config['locators']['ITEM_CUSTOMER']['by'], config['locators']['ITEM_CUSTOMER']['selector']).text
                    except:
                        customer = None
                    data.append({
                        'linkText': link_text,
                        'linkHref': link_href,
                        'price': price,
                        'number': number.split(' № ')[1],
                        'type': number.split(' № ')[0],
                        'organizer': organizer,
                        'customer': customer
                    })
            try:
                last_page = int(driver.find_element(config['locators']['LAST_PAGE']['by'], config['locators']['LAST_PAGE']['selector']).text)
            except:
                last_page = 0
            if page_num >= last_page:
                break
            else:
                page_num += 1
    return data

# Парсинг roseltorg.ru
def parseRoseltorg(config, fltr, driver, subscription):
    driver.get(config['url'])

# Парсинг b2b-center.ru
def parseB2bCenter(config, fltr, driver, subscription):
    # Заходим на основной урл, чтобы получить куки и сессию
    driver.get(config['url'])
    # Принимаем куки
    try:
        cookie_btn = driver.find_element(config['locators']['COOKIE_BUTTON']['by'], config['locators']['COOKIE_BUTTON']['selector'])
        cookie_btn.click()
    except:
        pass
    if 'captcha' in driver.current_url:
        writeLog({'time': datetime.now().strftime(getDateFormat(True)), 'error': f'Поймали капчу по подписке {subscription["name"]} на сайте {subscription["website"]}'})
        return []
    # Ждём, чтобы не забанили
    time.sleep(1500)
    # Генерируем урл с фильтрами
    url_params = config['values']['URL_PARAMS']
    if fltr.get('daysBackPublished') and fltr.get('daysBackPublished') > 0:
        url_params['date_start_dmy'] = (datetime.today() - timedelta(days=fltr.get('daysBackPublished'))).strftime(getDateFormat())
        url_params['date_end_dmy'] = datetime.today().strftime(getDateFormat())
    else:
        url_params['date_start_dmy'] = datetime.today()
        url_params['date_end_dmy'] = datetime.today()
    regions_params = []
    if fltr.get('regions') and len(fltr.get('regions')) > 0:
        i = 0
        region_param_name = config['values']['REGIONS_PARAM_NAME']
        for region in fltr.get('regions'):
            url_params[region_param_name.format(i)] = region
            i += 1
    if fltr.get('minPrice') and fltr.get('minPrice') > 0:
        url_params['price_start'] = fltr.get('minPrice')
    if fltr.get('maxPrice') and fltr.get('maxPrice') > 0:
        url_params['price_end'] = fltr.get('maxPrice')
    if fltr.get('maxPrice') and fltr.get('minPrice') and  fltr.get('maxPrice') < fltr.get('minPrice'):
        writeLog({'time': datetime.now().strftime(getDateFormat(True)), 'error': f'Минимальная цена {fltr.get("minPrice")} больше максимальной {fltr.get("maxPrice")} по подписке {subscription["name"]}'}, True)
        return []
    if fltr.get('organizerOrCustomer') and fltr.get('organizerOrCustomer').get('name') and fltr.get('organizerOrCustomer').get('type') and len(fltr.get('organizerOrCustomer')['name']) > 0:
        org_name = fltr.get('organizerOrCustomer')['name']
        constant_name = 'ORGANIZER' if fltr.get('organizerOrCustomer')['type'] == 'organizer' else 'CUSTOMER'
        org_type = config['values'][constant_name]
        org_id = driver.execute_script(config['values']['SCRIPT'].format(org_type, org_name))
        id_param = config['values'][constant_name + '_PARAMS']['id']
        company_type_param_value = config['values'][constant_name + '_PARAMS']['companyType']
        url_params[id_param] = org_id
        url_params['company_type'] = company_type_param_value
    
    # Перебираем кейворды, типы тендеров, парсим каждый, сохраняем информацию в общий массив
    data = []
    if fltr.get('tenderTypes') and len(fltr.get('tenderTypes')) > 0:
        tender_types = fltr.get('tenderTypes')
    else:
        tender_types = ["0"]
    for tender_type in tender_types:
        url_params['lot_type'] = tender_type
        for query in fltr['keywords']:
            time.sleep(5)
            page_num = 0
            while True:
                url_params['f_keyword'] = query
                url_params['from'] = page_num
                url = config['values']['URL_WITH_FILTERS'] + urllib.urlencode(url_params)
                driver.get(url)
                items = driver.find_elements(config['locators']['ITEM']['by'], config['locators']['ITEM']['selector'])
                if len(items) > 0:
                    for item in items:
                        try:
                            link = item.find_element(config['locators']['ITEM_LINK']['by'], config['locators']['ITEM_LINK']['selector'])
                            number = link.text
                            link_href = link.get_attribute('href')
                        except:
                            number = None
                            link_href = None
                        try:
                            organizer = item.find_element(config['locators']['ITEM_ORGANIZER']['by'], config['locators']['ITEM_ORGANIZER']['selector']).text
                        except:
                            organizer = None
                        try:
                            link_text = item.find_element(config['locators']['ITEM_DESCRIPTION']['by'], config['locators']['ITEM_DESCRIPTION']['selector']).text
                        except:
                            link_text = None
                        data.append({
                            'linkText': link_text,
                            'linkHref': link_href,
                            'number': number.replace(link_text, '').split(' № ')[1].strip(),
                            'type': number.replace(link_text, '').split(' № ')[0],
                            'organizer': organizer
                        })
                try:
                    last_page = int(driver.find_element(config['locators']['LAST_PAGE']['by'], config['locators']['LAST_PAGE']['selector']).text)*20
                except:
                    last_page = 0
                if page_num+20 >= last_page:
                    break
                else:
                    page_num += 20
                    # Ждём, чтобы не забанили
                    time.sleep(3+page_num/20)
    return data

# Парсинг сайтов
def parseSite(website, parser_config, fltr, driver, subscription):
    if website == 'fabrikant':
        return parseFabrikant(parser_config, fltr, driver, subscription)
    if website == 'b2b-center':
        return parseB2bCenter(parser_config, fltr, driver, subscription)
    if website == 'roseltorg':
        return parseRoseltorg(parser_config, fltr, driver, subscription)


