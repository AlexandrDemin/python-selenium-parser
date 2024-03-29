# Описание

Скрипт парсинга сайтов с помощью Selenium и Chrome Driver.
При запуске скрипт читает информацию о сайтах из файла `parsers-config.json` и информацию о подписках из файла `subscriptions-config.json`. Затем для каждой подписки парсит указанные в ней сайты по заданным фильтрам и отправляет найденную информацию на указанные почты в формате html.

# Установка и запуск

На сервере должны быть установлены:

1. Python 3.6
1. Selenium
1. Beautiful Soup 4
1. Chrome Driver
1. SMTP Server

Все файлы должны лежать в одной папке:

1. app.py
1. logic.py
1. parsers-config.json
1. subscriptions-config.json

Скрипт запускается командой

```
python -m app
```

Для периодического запуска скрипта необходимо использовать сторонние инструменты, например, cron.

# Управление подписками

Информация о пользователях и их подписках хранится в файле `subscriptions-config.json`.
Структура данных такая: есть множество пользователей, у каждого можетбыть несколько подписок. Подписка - это назание, сайт и фильтр. Подписка относится только к одному сайту, потому что у разных сайтов разные айдишники регионов и типов, их нельзя смешивать.
Файл имеет следующую структуру:

```
[
	{
		"name": "имя пользователя",
		"email": ["массив email пользователя, на которые слать результаты"],
		"subscriptions": [ // список подписок пользователя 1
			{
				"name": "Название подписки по-русски для использования в тексте письма и в логах",
				"website": "id сайта из файла parsers-config.json. Важно, чтобы строка полностью совпадала и была в том же регистре (большие и маленькие буквы)",
				"filter": {
					"daysBackPublished": 10, // Берётся период публикации от текущая дата - указанное число до текущей даты. Если не указано, берутся тенедры, опубликованные сегодня
					"regions": ["3", "866"], // Id регионов, в которых искать тендеры. Найти их можно в конфиге parsers-config.json в разделе REGIONS для нужного сайта. Если не указано, берутся все регионы.
					"minPrice": 4000, // Минимальная цена. Число. Если не задано, берётся 0. Если будет больше maxPrice, парсинг упадёт с ошибкой
					"maxPrice": 200000, // Максимальная цена. Число. Если не задано, берётся бесконечность. Если будет меньше minPrice, парсинг упадёт с ошибкой
					"keywords": [], // Список ключевых слов для поиска по описанию тендера. Если слова не заданы, берутся тендеры с любым описанием (*).
					"tenderTypes": [], // // Id типов тендеров. Найти их можно в конфиге parsers-config.json в разделе TYPES для нужного сайта. Если не указано, берутся все типы.
					"organizerOrCustomer": {
						"name": "глонасс", // Название заказчика или организатора. Если в списке на сайте ничего не найдётся по этой строке, в лог запишется ошибка. Если не указан, любой заказчик/организатор
						"type": "organizer" // Тип поиска. customer - заказчик, organizer - организатор.
					}
				}
			},
			{
				// Подписка 2
			}
		]
	},
	{
		// Пользователь 2
	}
]
```

Файл конфига парсится как JSON, поэтому важно соблюдать корректную структуру. Если потерять ковычку или скобку или запятую, или использовать одинарные кавычки вместо двойных, работать не будет.

# Управление парсерами сайтов

Данные о парсерах хранятся в файле `parsers-config.json`. Файл имеет следующую структуру:

```
{
	"Айдишник сайта. Должен быть уникальным": {
		"url": "Урл сайта, с которого оначинается парсинг",
		"locators": { // Список локаторов для поиска элементов на сайте. Если на сайте поменяется вёрстка, нужно будет поменять способ поиска элементов здесь.
			"SOME_BUTTON": {
				"by": "css selector", // Как искать элемент. Варианты: "id", "xpath", "link text", "partial link text", "name", "tag name", "class name", "css selector"
                "selector": ".marketplace-unit__title a" // Строка для поиска. Формат зависит от значения в поле "by"
			},
			"OTHER_ELEMENT": {
				"by": "id",
                "selector": "some_id"
			}
		},
		"values": { // Список констант для сайта. Например, айдишники регионов, названия параметров в урле, скрипты и т. д.
			"SOME_CONSTANT_VALUE": "",
			"SOME_OTHER_VALUE": [1,2,3]
		}
	}
}
```

Файл конфига парсится как JSON, поэтому важно соблюдать корректную структуру. Если потерять ковычку или скобку или запятую, или использовать одинарные кавычки вместо двойных, работать не будет.

# Добавление парсеров других сайтов

Чтобы добавить парсер, нужно добавить данные для него в конфиг `parsers-config.json`, написать функцию парсинга этого сайта в `logic.py` и там же расширить функцию `parseSite`, чтобы привязать функцию парсинга к айдишнику сайта из конфига.

# Мониторинг результатов работы и ошибок

Результаты работы скрипта записываются в файл `results.log`.
Ошибки записываются в файл `errors.log`.
Файлы логов складываются в ту же папку, где находится скрипт. При запуске скрипта удаляются старые записи в логах, чтобы в них было не больше 10000 строк.

