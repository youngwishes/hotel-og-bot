# RU: getenv("API_KEY") - твой API ключ (Сервис - https://rapidapi.com/hub)
# EN: getenv("API_KEY") - your API KEY (Service - https://rapidapi.com/hub)

from os import getenv

headers = {'x-rapidapi-host': 'hotels4.p.rapidapi.com',
           'x-rapidapi-key': getenv("API_KEY")}
