import requests
import json
from CreatingQueries.headers import headers
from Classes.history import History


def make_req(hotel_id: int):
    """
    RU:
        Сбор необходимых параметров для создания API-запроса
    EN:
        Collecting the necessary parameters to create an API request

    :param hotel_id: unique id of the hotel
    :return: result of api_request
    """
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    request_params = {'id': hotel_id}
    return api_request(request_params, url)


def api_request(params: dict, url: str) -> dict or bool:
    """
    RU:
        Отправка get-запроса к API hotels.com (использованный сервис - https://rapidapi.com/hub)
    EN:
        Sending a get request to the API hotels.com (used service - https://rapidapi.com/hub)

    :param url: get request URL
    :param params: get request params
    :return: dict
    """
    try:
        response = requests.get(url, params=params, headers=headers, timeout=20)
        if response.status_code == 200:
            try:
                result = json.loads(response.text)
                return result
            except json.decoder.JSONDecodeError as exc:
                print(f'WARNING!!!\n{exc}')
        else:
            return False
    except requests.exceptions.ReadTimeout as exc:
        print(f'WARNING!!!\n{exc}')


def send_photos(hotel_id: int, user_id: int) -> list[str] or bool:
    """
    RU:
        Сбор URL-фотографий в список, добавление фото в базу данных
    EN:
        Collecting URL photos in the list, adding photos to the database

    :param hotel_id: unique id of the hotel
    :param user_id: unique telegram-id of the user
    :return: list[photo_url, photo_url, ... , photo_url]
    """
    result: dict = make_req(hotel_id)
    if result:
        photos_list = []
        for current, i_photo in enumerate(result["hotelImages"]):
            photo_url = i_photo.get("baseUrl")
            if photo_url:
                photos_list.append(photo_url.replace("_{size}", ""))
        History(user_id).add_photos(photos_list[:6], hotel_id)
        return photos_list
    else:
        return False
