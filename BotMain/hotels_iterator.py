from Classes.telegram_user import TelegramUser
from typing import Iterator
from Classes.history import History


def my_hotels_deserializer(result: dict, tg_user: TelegramUser, check_gen: bool = None) -> Iterator:
    """
    RU:
        Функция итератор, возвращает структурированную 'упакованную' информацию о каждом найденном отеле
    EN:
        The iterator function returns structured 'packed' information about each hotel found

    :param result: dictionary with list of hotels
    :param tg_user: TelegramUser
    :param check_gen: A special parameter. Used to check the iterator for iterations
    :return: Iterator
    """
    result_dict = result['data']['body']['searchResults']['results']
    for i_hotel in result_dict:
        if i_hotel:
            hostel_name = i_hotel.get("name")
            if i_hotel.get("address").get("streetAddress"):
                hostel_address = i_hotel.get("address").get("streetAddress")
            else:
                hostel_address = "Не указан"
            if i_hotel.get("guestReviews"):
                rating = i_hotel.get("guestReviews").get("rating")
                scale = i_hotel.get("guestReviews").get("scale")
            else:
                rating = 'Не указан'
                scale = 10
            if i_hotel.get("landmarks")[1]["label"]:
                landmarks = i_hotel.get("landmarks")[1]["label"]
                lm_distance = float(i_hotel.get("landmarks")[1]["distance"].split()[0]) * 1.61
            else:
                landmarks = "Не указано"
                lm_distance = "Не указано"

            if i_hotel.get("landmarks")[0]["distance"]:
                center_distance = float(i_hotel.get("landmarks")[0]["distance"].split()[0]) * 1.61
                if tg_user.commands_list[-1].name == '/bestdeal':
                    if center_distance > tg_user.hotel.distance:
                        continue
            else:
                center_distance = "Не указано"

            if i_hotel.get("ratePlan").get("price").get("exactCurrent"):
                price = i_hotel.get("ratePlan").get("price").get("exactCurrent")
                total_price = int((tg_user.check_out - tg_user.check_in).days) * price
            else:
                price = "Не указано"
                total_price = None

            hotel_id = i_hotel.get('id')
            hotel_url = "https://www.hotels.com/ho{hotel_id}?" \
                        "q-check-in={check_in}&q-check-out={check_out}".format(hotel_id=hotel_id,
                                                                               check_in=tg_user.check_in,
                                                                               check_out=tg_user.check_out)

            hotel_info = f"Название отеля: {hostel_name}\n\n" \
                         f"Адресс: {hostel_address}\n" \
                         f"Рейтинг отеля: {rating} из {scale}\n" \
                         f"Ориентир: {landmarks}, расстояние - {lm_distance:.2f} км.\n" \
                         f"Расстояние до центра: {center_distance:.2f} км.\n" \
                         f"\nЦена за ночь - {price}$\n" \
                         f"Итого - {total_price:.2f}$\n" \

            if not check_gen:
                History(tg_user.user_id).add_info((hotel_url, hotel_info, hotel_id))
            yield hotel_info, hotel_id, hotel_url
