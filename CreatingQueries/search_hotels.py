from BotMain.hotels_iterator import my_hotels_deserializer

from Classes.telegram_user import TelegramUser
from CreatingQueries.headers import headers

import requests
import json


def api_request(url: str, query_string: dict) -> dict:
    """
    RU:
        Отправка get-запроса к API hotels.com (использованный сервис - https://rapidapi.com/hub)
    EN:
        Sending a get request to the API hotels.com (used service - https://rapidapi.com/hub)

    :param url: get request URL
    :param query_string: get request info for get request params
    :return:
    """
    params = {
        "destinationId": query_string.get('id'),
        "pageNumber": '1',
        "pageSize": '25',
        "checkIn": query_string.get('checkIn'),
        "checkOut": query_string.get('checkOut'),
        "adults1": '1',
        "sortOrder": query_string.get('sortOrder'),
        "locale": 'en_US',
        "currency": 'USD',
        "priceMin": query_string.get('priceMin'),
        "priceMax": query_string.get('priceMax')
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        print(response.text)
        if response.status_code == 200:
            result = json.loads(response.text)
        else:
            result = None
    except requests.Timeout as time_end:
        print(f'Ошибка {time_end}')
        result = None
    except requests.RequestException as er:
        print(f'Ошибка {er}')
        result = None

    return result


def make_req(tg_user: TelegramUser):
    """
    RU:
        Сбор необходимых параметров для создания get-запроса.
    EN:
        Collecting the necessary parameters to create a get request.

    :param tg_user: object of TelegramUser
    :return: result of api_request
    """
    query_string = {'id': tg_user.cities.destination_id,
                    'checkIn': tg_user.check_in,
                    'checkOut': tg_user.check_out,
                    'sortOrder': tg_user.commands_list[-1].order_by,
                    'priceMin': tg_user.hotel.price_range.get('priceMin'),
                    'priceMax': tg_user.hotel.price_range.get('priceMax')
                    }
    url = 'https://hotels4.p.rapidapi.com/properties/list'
    return api_request(url, query_string)


def search_hotels(tg_user: TelegramUser, check_gen: bool = None):
    """
    RU:
        Проверка запроса на валидный ответ.
    EN:
        Checking the request for a valid response.

    :param tg_user: object of TelegramUser
    :param check_gen: A special parameter. Used to check the iterator for iterations
    :return:
    """
    result: dict = make_req(tg_user)
    if result:
        return my_hotels_deserializer(result, tg_user, check_gen)
    else:
        return None

