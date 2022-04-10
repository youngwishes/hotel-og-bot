from db import connection, send_mail
from typing import Iterator


class History:
    """
    Database - SQL
    Database Management System - PostgreSQL

    RU:
        Базовый класс описывающий сериализацию и десериализацию истории пользователя

        Атрибуты:
            self.tg_user_id: id телеграмм пользователя
    EN:
        A base class describing the serialization and deserialization of a user's history

        Attributes:
            self.tg_user_id: user's telegram id
    """

    def __init__(self, tg_user_id: int):
        self.tg_user_id = tg_user_id

    def set_mail(self, mail: str) -> None:
        """
        RU:
            Добавление почты пользователя
        EN:
            Adding user mail

        :param mail: user's email
        :return:
        """
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE tg_user SET user_mail = '{user_mail}' WHERE user_id = {user_id}".format(
                    user_id=self.tg_user_id,
                    user_mail=mail)
            )

    def clear_all(self) -> bool:
        """
        RU:
            Удаление истории пользователя
        EN:
            Adding user mail

        :return: True if history is, False else
        """
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT * FROM hotel
            WHERE fk_user_id = {}
            """.format(self.tg_user_id))
            if cursor.fetchall():
                cursor.execute("""
                DELETE FROM hotel
                WHERE fk_user_id = {};
                DELETE FROM command
                WHERE fk_user_id = {}
                """.format(self.tg_user_id, self.tg_user_id))
                return True
            else:
                return False

    def check_mail(self):
        """
        RU:
            Проверка электронной почты
        EN:
            Email check

        :return: Email if email is, None else
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                        SELECT user_mail
                        FROM tg_user
                        WHERE tg_user.user_id = {user_id}
                        """.format(user_id=self.tg_user_id))
            address = cursor.fetchone()
        return address[0]

    def select_commands(self):
        """
        RU:
            Десериализация пяти последних команд пользователя
        EN:
            Deserialization of the last five user commands

        :return: commands if commands is, None else
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                            SELECT command_name, command_time, command_id
                            FROM command
                            WHERE fk_user_id = {user_id}
                            ORDER BY command_id DESC LIMIT 5
                        """.format(user_id=self.tg_user_id))
            return cursor.fetchall()

    @classmethod
    def send_for_command(cls, command_id: str) -> Iterator:
        """
        RU:
            Десериализация отелей по выбранной команде
        EN:
            Deserialization of hotels by the selected command

        :param command_id: command's id
        :return: Iterator[hotel_description, hotel_photos, hotel_url]
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                        SELECT hotel_info, hotel_photos, hotel_url
                        FROM hotel
                        WHERE fk_command_id = {command_id}
                        """.format(command_id=int(command_id)))
            data = cursor.fetchall()
        for i_hotel in data:
            yield i_hotel

    def send_all_mail(self, email: str):
        """
        RU:
            Составление сообщения для отправки истории на электронную почту
        EN:
            Composing a message to send a story to an email

        :param email: user's email
        :return: False if field email is not, else send_mail
        """
        hotel_info = 'Hello my dear friend! This is your history!\n\n'
        if email:
            for current, i_data in enumerate(self.send_all()):
                if len(i_data) == 2:
                    command_data, hotel_data = i_data
                    command_info = f'Command_name - {command_data[0]}\n' \
                                   f'Command_date - {command_data[1]}\n' \
                                   f'Command_time - {command_data[2]}\n'
                    hotel_info = f'{hotel_info}\n{"-" * 100}\n{command_info}{"-" * 100}\n'
                else:
                    hotel_data = i_data
                hotel_url, info = hotel_data[0], hotel_data[1].replace(",", "\n")
                hotel_info = f'{hotel_info}\n #{current + 1}:\nHotel info - {info}\nURL - {hotel_data[0]}\n'
            hotel_info = f'{hotel_info}\n\n With love, your OG HOTEL BOT😎'
            return send_mail(hotel_info, email)
        else:
            return False

    def send_all(self) -> tuple:
        """
        RU:
            Функция-генератор. Десериализация всей истории пользователя.
        EN:
            The generator function. Deserialization of the entire user history.

        :return: False if fields in table hotel are not, else optional
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                        SELECT command_name, command_date, command_time, command_id, hotel_url, hotel_info, hotel_photos
                        FROM tg_user
                        JOIN command ON tg_user.user_id = command.fk_user_id
                        JOIN hotel ON command.command_id = hotel.fk_command_id
                        WHERE tg_user.user_id = {user_id}
                        """.format(user_id=self.tg_user_id))
            cursor = cursor.fetchall()
        if cursor:
            current = 0
            for i_hotel in cursor:
                command_name, command_date, command_time, command_id, hotel_url, hotel_info, hotel_photos = i_hotel
                hotel_data = (hotel_url, hotel_info, hotel_photos)
                if command_id > current:
                    current = command_id
                    command_data = (command_name, command_date, command_time)
                    yield command_data, hotel_data
                else:
                    yield hotel_data
        else:
            return False

    def add_info(self, values: tuple):
        """
        RU:
            Сериализация истории пользователя.
        EN:
            Serialization of user history.

        :param values: tuple(hotel_url, hotel_description, hotel_id)
        :return:
        """
        with connection.cursor() as cursor:
            cursor.execute('SELECT MAX(command_id) FROM command '
                           'WHERE fk_user_id = {};'.format(self.tg_user_id))
            command_id = int(cursor.fetchone()[0])
            hotel_url, hotel_info, hotel_id = values
            hotel_info = hotel_info.replace("'", "''")
            sql_command = "INSERT INTO hotel(hotel_id, hotel_url, hotel_info, fk_user_id, fk_command_id)" \
                          " VALUES ('{hotel_id}','{url}', '{info}', {user_id}, {command_id})".format(
                            hotel_id=hotel_id, url=hotel_url, info=hotel_info.replace('\n', ', '),
                            user_id=self.tg_user_id, command_id=command_id)
            cursor.execute(sql_command)

    def add_photos(self, photos: list, hotel_id: int):
        """
        RU:
            Сериализация фотографий отеля.
        EN:
            Serialization of hotel photos.

        :param photos: list(photo_url, photo_url, ... , photo_url)
        :param hotel_id: id of current hotel
        :return:
        """
        with connection.cursor() as cursor:
            cursor.execute('SELECT MAX(command_id) FROM command '
                           'WHERE fk_user_id = {}'.format(self.tg_user_id))
            command_id = int(cursor.fetchone()[0])
            sql_command = "UPDATE hotel SET hotel_photos = %s" \
                          " WHERE (fk_user_id = %s) AND (fk_command_id = %s) AND (hotel_id = %s)"
            values = (photos, self.tg_user_id, command_id, hotel_id)
            cursor.execute(sql_command, values)
