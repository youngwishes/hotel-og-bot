import json
import requests
from CreatingQueries.headers import headers


def city_req(url: str, params: dict) -> dict or bool:
    """
    RU:
        Отправка get-запроса к API hotels.com (использованный сервис - https://rapidapi.com/hub)
    EN:
        Sending a get request to the API hotels.com (used service - https://rapidapi.com/hub)

    :param url: get request URL
    :param params: get request params
    :return: dict
    """
    response = requests.get(url, headers=headers, params=params, timeout=30)
    print(response.headers)
    if response.status_code == 200:
        try:
            result = json.loads(response.text)
            return result
        except json.decoder.JSONDecodeError:
            return False
    else:
        return False


def init_req(city: str) -> dict:
    """
    RU:
        Составление исходных данных для создания get-запроса
    EN:
        Compilation of source data for creating a get request

    :param city: city name
    :return: dict
    """
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    params = {"query": city, "locale": 'en_US', "currency": 'USD'}
    response = city_req(url, params)
    return response


def search_city(city: str) -> dict:
    """
    RU:
        Составление словаря по найденным городам и странам
    EN:
        Compiling a dictionary of found cities and countries

    :param city: city name
    :return: dict{destinationId: tuple(city name, state, city country)
    """
    destinations_dict = dict()
    response = init_req(city)
    if response:
        response = response['suggestions'][0]['entities']
        for i_elem in response:
            if i_elem['name'].lower() == city.lower():
                city_name = i_elem['name']
                if len(i_elem['caption'].split(',')) > 2:
                    country = ', '.join(i_elem['caption'].split(',')[-2:])
                else:
                    country = i_elem['caption'].split(',')[-1]
                destinations_dict[i_elem['destinationId']] = (city_name, country)
        return destinations_dict
