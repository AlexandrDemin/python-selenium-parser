from logic import *

# Очистка логов, чтобы не разрастались
discardOldLogs(10000)

# Чтение конфигов
parsers_config, subscriptions_config = readConfigs('./parsers-config.json', './subscriptions-config.json')

writeLog({
    'time': datetime.now().strftime(getDateFormat(True)),
    'message': "Старт"
})
# Запускаем Хром
driver = webdriver.Chrome()

# Перебор подписок, парсинг сайтов и рассылка писем
for user in subscriptions_config:
    for subscription in user['subscriptions']:
        try:
            website = subscription['website']
            parser_config = parsers_config[website]
            fltr = subscription['filter']
            data = parseSite(website, parser_config, fltr, driver, subscription)
            writeLog({
                'time': datetime.now().strftime(getDateFormat(True)),
                'message': f"Спарсили {len(data)} элементов по подписке {subscription['name']}"
            })
            if len(data):
                html_content = generateHtml(data, subscription, parser_config.get("values").get("TYPES"), user['guid'])
                sendEmail(user['email'], subscription['name'], html_content)
        except Exception as e:
            writeLog({
                'time': datetime.now().strftime(getDateFormat(True)),
                'error': f'Ошибка при обработке подписки {subscription["name"]}',
                'stackTrace': str(e)
            }, True)

# Выключаем хром
driver.quit()
writeLog({
    'time': datetime.now().strftime(getDateFormat(True)),
    'message': f"Финиш"
})
