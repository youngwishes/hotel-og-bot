from datetime import datetime


class Command:
    """
    RU:
        Базовый класс, описывающий команду пользователя.

        Атрибуты:
            self.name: название команды
            self.command_date: дата ввода команды
            self.command_time: время ввода команды
            self.order_by: способ сортировки отелей
    EN:
        The base class describing the user's command.

        Attributes:
            self.name: command name
            self.command_date: date the command was entered
            self.command_time: time the command was entered
            self.order_by: hotel sorting method

    """

    def __init__(self, command_name: str) -> None:
        self.name = command_name
        self.command_date = datetime.today().date()
        self.command_time = datetime.today().time().replace(microsecond=0)
        self.order_by = self.order_by_setter()

    @property
    def command_name(self) -> str:
        return self.name

    def order_by_setter(self):
        """
        RU:
            Установление способа сортировки отелей

        EN:
            Establishing a way to sort hotels

        :return: str
        """
        if self.name == "/lowprice":
            return "PRICE"
        elif self.name == "/highprice":
            return "PRICE_HIGHEST_FIRST"
