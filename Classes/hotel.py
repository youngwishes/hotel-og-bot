from typing import Iterator


class Hotel:
    """
    RU:
        Базовый класс, описывающий информацию о выводе отелей.

        Атрибуты:
            self.description: описание отеля
            self.hotel_id: уникальный айди отеля
            self.hotel_url: ссылка на отель
            self.photos: список фоток обёрнутый в класс BidirectionalIterator
            self.iterator: итератор отелей
            self.distance: расстояние до центра
            self.price_range: dict{'priceMin': price_min, 'priceMax': price_max}
    EN:
        A base class describing information about hotels.

        Attributes:
            self.description: description of the hotel
            self.hotel_id: unique hotel id
            self.hotel_url: URL from https://www.hotels.com/
            self.photos: a list of photos wrapped in the BidirectionalIterator class
            self.iterator: iterator of list of hotels
            self.distance: distance to the center
            self.price_range: dict{'priceMin': price_min, 'priceMax': price_max}

    """

    def __init__(self):
        self.description = None
        self.hotel_id = None
        self.hotel_url = None
        self.photos = None
        self.iterator = None
        self.distance = None
        self.price_range = dict()

    @property
    def distance(self) -> float:
        return self._distance

    @distance.setter
    def distance(self, user_distance: float):
        self._distance: float = user_distance

    @property
    def price_range(self) -> dict:
        return self._price_range

    @price_range.setter
    def price_range(self, user_range: dict):
        self._price_range: dict = user_range

    @property
    def iterator(self) -> Iterator:
        return self._iterator

    @iterator.setter
    def iterator(self, iterator: Iterator) -> None:
        self._iterator: Iterator = iterator
