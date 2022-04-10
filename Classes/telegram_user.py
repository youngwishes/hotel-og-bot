from Classes.command import Command
from db import connection
from psycopg2 import Error
from telebot.types import Message


class TelegramUser:
    """
    RU:
        Базовый класс, описывает пользователя

        Атрибуты:
            self.user_id: уникальный телеграмм-айди пользователя
            self.commands_list: список всех команд пользователя (объекты класса Command)
            self.cities: объект класса City с информацией о городе
            self.hotel: объект класса Hotel с информацией об отелях
            self.check_in: дата заезда
            self.check_out: дата выезда
            self.keyboard_control: статус текущего запроса
    EN:
        Base class, describes the user

        Attributes:
            self.user_id: unique telegram ID of the user
            self.commands_list: a list of all user commands (objects of the Command class)
            self.cities: an object of the City class with information about the city
            self.hotel: a Hotel class object with information about hotels
            self.check_in: check-in date
            self.check_out: departure date
            self.keyboard_control: status of the current request
    """

    def __init__(self, message: Message):
        self.user_id = message
        self.cities = None
        self.hotel = None
        self.check_in = None
        self.check_out = None
        self.commands_list = list()
        self.keyboard_control = True

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, message: Message):
        """
        RU:
            Добавление пользователя через его телеграмм-id, добавление пользователя в базу данных

        EN:
            Adding a user via his telegram-id, adding a user to the database

        :param message: object Message
        :return:
        """
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO tg_user(user_id, user_name) VALUES ({tg_user_id}, '{tg_user_name}')".format(
                        tg_user_id=message.from_user.id,
                        tg_user_name=message.from_user.first_name)
                )
            except Error:
                print(f'{message.from_user.first_name} зашёл на огонёк')

            self._user_id = message.from_user.id

    def log_command(self, command: Command):
        """
        RU:
            Логирование команд пользователя, добавление команд в базу данных
        EN:
            Logging user commands, adding commands to the database

        :param command: object Command
        :return:
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO command(command_name, command_date, command_time, fk_user_id) VALUES
                ('{command_name}', '{command_date}', '{command_time}', {user_id})""".format(
                    command_name=command.name, command_date=command.command_date,
                    command_time=command.command_time, user_id=self.user_id)
            )
        self.commands_list.append(command)


class TelegramUsers:
    """
    RU:
        Базовый класс, описывающий список юзеров

        Атрибуты:
            self.__user_list - список id пользователей.
    EN:
        Base class describing the list of users

        Attributes:
            self.__user_list: list of user ids
    """

    def __init__(self):
        self.__users_list = []

    def append_user(self, tg_user: TelegramUser) -> None:
        """
        RU:
            Добавление пользователя в список пользователей
        EN:
            Adding a user to the list of users

        :param tg_user: object of TelegramUser
        :return:
        """
        if tg_user not in self.__users_list:
            self.__users_list.append(tg_user)

    def get_user_from_id(self, user_id: int) -> False or TelegramUser:
        """
        RU:
            Поиск пользователя по его id в списке пользователей
        EN:
            Search for a user by his id in the list of users

        :param user_id: user telegram-id
        :return: object of TelegramUser or False if TelegramUser is not
        """
        for i_user in self.__users_list:
            if i_user.user_id == user_id:
                return i_user
        else:
            return False
