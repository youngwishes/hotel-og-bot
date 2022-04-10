class City:
    """
    RU:
        Базовый класс, описывающий город.

        Атрибуты:
            self.destination_id = уникальный id города
            self.response = dict{destinationId: tuple(название города, штат, страна)}

    EN:
        A base class describing the city.

        Attributes:
            self.destination_id = unique id of the city
            self.response = dict{destinationId: tuple(city name, state, country name)}

    """

    def __init__(self):
        self.destination_id = None
        self.response = None

    @property
    def response(self) -> dict:
        return self._response

    @response.setter
    def response(self, response: dict) -> None:
        self._response = response

    @property
    def destination_id(self) -> str:
        return self._destination_id

    @destination_id.setter
    def destination_id(self, destination_id: str) -> None:
        self._destination_id = destination_id
