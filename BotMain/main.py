from os import getenv

import telebot
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, InlineKeyboardButton, KeyboardButton, InputMediaPhoto

from telegram_bot_calendar import WMonthTelegramCalendar

from Classes.telegram_user import TelegramUser, TelegramUsers
from Classes.hotel import Hotel
from Classes.command import Command
from Classes.city import City
from Classes.history import History
from Classes.bd_iter import BidirectionalIterator

from datetime import datetime
from datetime import timedelta

from CreatingQueries.search_city import search_city
from CreatingQueries.search_hotels import search_hotels
from CreatingQueries.photos_api import send_photos

from typing import Iterator
import re


def main():
    @bot.callback_query_handler(func=lambda call: call.data in ('next', 'prev', 'next_hotel', 'exit'))
    def callback_worker(call: CallbackQuery):
        """
        CALLBACK WORKER # 1
        RU:
            Обработчик Inline-клавиатуры (отель).
            При просмотре отеля (результат поиска пользователя)
        EN:
            Inline keyboard handler (hotel).
            When the user looking through hotels

        :param call: CallbackQuery
        :return: None
        """
        tg_user = bot_users.get_user_from_id(call.message.chat.id)
        if call.data == 'next':
            next_photo = tg_user.hotel.photos.next()
            if next_photo:
                bot.edit_message_media(InputMediaPhoto(media=next_photo,
                                                       caption=tg_user.hotel.description),
                                       call.message.chat.id, call.message.message_id,
                                       reply_markup=photo_alb_kb(tg_user.hotel.hotel_url))
        elif call.data == 'prev':
            prev_photo = tg_user.hotel.photos.prev()
            if prev_photo:
                bot.edit_message_media(InputMediaPhoto(media=prev_photo,
                                                       caption=tg_user.hotel.description),
                                       call.message.chat.id, call.message.message_id,
                                       reply_markup=photo_alb_kb(tg_user.hotel.hotel_url))
        elif call.data == 'next_hotel':
            try:
                tg_user.hotel.description, tg_user.hotel.hotel_id, tg_user.hotel.hotel_url \
                                                                                = next(tg_user.hotel.iterator)
                photos_list = send_photos(tg_user.hotel.hotel_id, call.message.chat.id)
                tg_user.hotel.photos = BidirectionalIterator(photos_list)
                bot.edit_message_media(InputMediaPhoto(media=tg_user.hotel.photos.next(),
                                                       caption=tg_user.hotel.description),
                                       call.message.chat.id, call.message.message_id,
                                       reply_markup=photo_alb_kb(tg_user.hotel.hotel_url))
            except StopIteration:
                bot.send_message(call.message.chat.id,
                                 'По данному запросу больше отелей нет, поискать ещё что-нибудь?',
                                 reply_markup=acceptance_keyboard())
                bot.register_next_step_handler(call.message, finally_block)
        else:
            tg_user.keyboard_control = True
            bot.edit_message_media(InputMediaPhoto(media=open('ThankYou.png', mode='rb')),
                                   call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, 'Поискать ещё что-нибудь?', reply_markup=acceptance_keyboard())
            bot.register_next_step_handler(call.message, finally_block)

    @bot.callback_query_handler(func=lambda call: call.data in ('chat', 'mail'))
    def callback_worker(call: CallbackQuery):
        """
        CALLBACK WORKER # 2
        RU:
            Обработчик Inline-клавиатуры (история).
            При выборе пользователем способа отправки всей истории (в чат/на почту)
        EN:
            Inline-keyboard handler (history).
            When the user decides the way to send the whole history (to chat/email)

        :param call: CallbackQuery
        :return:
        """
        if call.data == 'chat':
            return send_history(call)
        elif call.data == 'mail':
            mail = History(call.message.chat.id).check_mail()
            if mail:
                if check_iter(History(call.message.chat.id).send_all()):
                    History(call.message.chat.id).send_all_mail(mail)
                    bot.edit_message_text('Отправил! Пожалуйста, проверьте Вашу почту.', call.message.chat.id,
                                          call.message.message_id)
                else:
                    bot.edit_message_text('История поиска пуста', call.message.chat.id,
                                          call.message.message_id)
            else:
                bot.send_message(call.message.chat.id, 'Не нашёл почту, пожалуйста, укажите ваш почтовый ящик')
                bot.register_next_step_handler(call.message, add_mail)

    @bot.callback_query_handler(func=lambda call: call.data.isdigit())
    def send_history_for_command(call: CallbackQuery):
        """
        CALLBACK WORKER # 3
        RU:
            Обработчик Inline-клавиатуры (история).
            При выборе пользователем конкретной команды из истории запроса пользователя
        EN:
            Inline keyboard handler (history).
            When the user have chosen his command from five last commands in commands list

        :param call: CallbackQuery
        :return:
        """
        data = History(call.message.chat.id).send_for_command(call.data)
        for i_data in data:
            hotel_data, hotel_photos, hotel_url = i_data
            bot.send_message(call.message.chat.id, hotel_data.replace(',', '\n'), reply_markup=make_url(hotel_url))
            hotel_photos = [InputMediaPhoto(i_url) for i_url in hotel_photos if i_url]
            try:
                bot.send_media_group(call.message.chat.id, hotel_photos)
            except telebot.apihelper.ApiException:
                bot.send_message(call.message.chat.id, 'Не удалось получить доступ к фото данного отеля.')

    @bot.callback_query_handler(func=lambda call: call.data in ('clear', 'all', 'partly'))
    def callback_worker(call: CallbackQuery):
        """
        CALLBACK WORKER # 4
        RU:
            Обработчик Inline-клавиатуры (история).
            При вводе пользователем команды '/history'
        EN:
            Inline-keyboard handler (history).
            When the user have sent a command '/history'

        :param call: CallbackQuery
        :return:
        """
        if call.data == 'clear':
            if History(call.message.chat.id).clear_all():
                bot.edit_message_text('Ваша история успешно очищена!', call.message.chat.id,
                                      call.message.message_id)
            else:
                bot.edit_message_text('История поиска пуста', call.message.chat.id,
                                      call.message.message_id)
        elif call.data == 'all':
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                          reply_markup=choose_history('select'))
        else:
            kb = choose_history(call)
            if len(kb.keyboard) > 0:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                              reply_markup=kb)
            else:
                bot.edit_message_text('Не было ни одного запроса', call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, menu)

    @bot.callback_query_handler(func=MyStyleCalendar(calendar_id=1).func(calendar_id=1))
    def callback_worker_check_in(call: CallbackQuery):
        """
        CALLBACK WORKER # 5
        RU:
            Обработчик Inline-клавиатуры (календарь).
            Выбор даты заезда
        EN:
            Inline-keyboard handler (calendar).
            When the user selects a check-in date.

        :param call: CallbackQuery
        :return:
        """
        result, key, step = MyStyleCalendar(calendar_id=1).process(call.data)
        tg_user = bot_users.get_user_from_id(call.message.chat.id)
        if result:
            tg_user.check_in = result
            return check_out(call.message, flag=True)
        elif not result and key:
            bot.edit_message_text(f"Выберите дату заезда",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=key)

    @bot.callback_query_handler(func=MyStyleCalendar(calendar_id=2).func(calendar_id=2))
    def callback_worker_check_out(call: CallbackQuery):
        """
        CALLBACK WORKER # 6
        RU:
            Обработчик Inline-клавиатуры (календарь).
            Выбор даты выезда
        EN:
            Inline-keyboard handler (calendar).
            When the user selects a check-out date.

        :param call: CallbackQuery
        :return:
        """
        tg_user = bot_users.get_user_from_id(call.message.chat.id)
        result, key, step = MyStyleCalendar(calendar_id=2).process(call.data)
        if result:
            tg_user.check_out = result
            if tg_user.check_out > tg_user.check_in:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
                bot.edit_message_text('Ищу лучшие варианты...', call.message.chat.id, call.message.message_id)
                return hotels_iterator(call.message.chat.id)
            else:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
                bot.edit_message_text("Указан некорректный промежуток. Дата отъезда не может быть"
                                      " раньше даты въезда или совпадать с ней.",
                                      call.message.chat.id, call.message.message_id)
                tg_user.check_out = None
                tg_user.check_in = None
                return choose_date(call.message)
        elif not result and key:
            bot.edit_message_text(f"Выберите дату отъезда",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=key)

    @bot.callback_query_handler(func=lambda call: not call.data.isdigit())
    def callback_worker(call: CallbackQuery):
        """
        CALLBACK WORKER # 7
        RU:
            Обработчик Inline-клавиатуры (город).
            Уточнение местоположения города
        EN:
            Inline-keyboard handler (city).
            When the user selects a country/state of req-city.

        :param call: CallbackQuery
        :return:
        """
        tg_user = bot_users.get_user_from_id(call.message.chat.id)
        for i_destination in tg_user.cities.response:
            if tg_user.cities.response[i_destination][1] == call.data:
                tg_user.cities.destination_id = i_destination
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
                if tg_user.commands_list[-1].name == "/bestdeal":
                    bot.send_message(call.message.chat.id, "Введите диапазон цен за ночь,"
                                                           " например, 30-70 (цена указывается в $)")
                    bot.register_next_step_handler(call.message, range_prices)
                else:
                    bot.send_message(call.message.chat.id, "Выберите дату заезда", reply_markup=choose_check_in())
                    bot.register_next_step_handler(call.message, check_in)

    def photo_alb_kb(hotel_url: str) -> InlineKeyboardMarkup:
        """
        RU:
            Создание Inline-клавиатуры (hotel).
            Обрабатывается CALLBACK WORKER # 1.
        EN:
            Creating Inline-keyboard (hotel).
            Handled by CALLBACK WORKER # 1.

        :param hotel_url: URL of hotel
        :return: InlineKeyboardMarkup
        """
        keyboard = InlineKeyboardMarkup(row_width=2)
        button1 = InlineKeyboardButton(text="  ➡  ", callback_data='next')
        button2 = InlineKeyboardButton(text="  ⬅  ", callback_data='prev')
        button3 = InlineKeyboardButton(text='Следующий отель', callback_data='next_hotel')
        button4 = InlineKeyboardButton(text="Ссылка", url=hotel_url)
        button5 = InlineKeyboardButton(text="Закончить", callback_data="exit")
        keyboard.add(button2, button1, button4, button3, button5)
        return keyboard

    def choose_history(key: str or CallbackQuery) -> InlineKeyboardMarkup:
        """
        RU:
            Создание Inline-клавиатуры (история).
            Обрабатывается CALLBACK WORKER # 2 или # 3 или # 4.
        EN:
            Creating Inline-keyboard (history).
            Handled by CALLBACK WORKER # 2 or # 3 or # 4.

        :param key: str or CallbackQuery, CallbackQuery when call.data is digit
        :return: InlineKeyboardMarkup
        """
        kb = InlineKeyboardMarkup()
        if key == 'start':
            button_1 = InlineKeyboardButton('Очистить', callback_data='clear')
            button_2 = InlineKeyboardButton('Всё', callback_data='all')
            button_3 = InlineKeyboardButton('Команды', callback_data='partly')
            kb.add(button_1, button_2, button_3)
        elif key == 'select':
            button_1 = InlineKeyboardButton('Отправить в чат', callback_data='chat')
            button_2 = InlineKeyboardButton('На почту', callback_data='mail')
            kb.add(button_1, button_2)
        else:
            commands = History(key.message.chat.id).select_commands()
            for i_command in commands:
                button = InlineKeyboardButton(f'{i_command[0]}, {i_command[1]}', callback_data=i_command[2])
                kb.add(button)
        return kb

    def cities_reply_kb() -> ReplyKeyboardMarkup:
        """
        RU:
            Создание Reply-клавиатуры (город).
        EN:
            Creating Reply-keyboard (city).

        :return: ReplyKeyboardMarkup
        """
        button_1 = KeyboardButton("Paris")
        button_2 = KeyboardButton("Bangkok")
        button_3 = KeyboardButton("Sochi")
        button_4 = KeyboardButton("Brasilia")
        button_5 = KeyboardButton("Cairo")
        button_6 = KeyboardButton("New York")
        button_7 = KeyboardButton("London")
        button_8 = KeyboardButton("Tokyo")
        cities_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        cities_keyboard.add(button_1, button_2, button_3, button_4, button_5, button_6, button_7, button_8)
        return cities_keyboard

    def make_inline_kb(cities: dict) -> InlineKeyboardMarkup:
        """
        RU:
            Создание Inline-клавиатуры (город).
            Обрабатывается CALLBACK WORKER # 7.
        EN:
            Creating Inline-keyboard (city).
            Handled by CALLBACK WORKER # 7.

        :param cities: dict{destinationId: (city name, country name)}
        :return: InlineKeyboardMarkup
        """
        keyboard = InlineKeyboardMarkup()
        for i_index, i_key in enumerate(cities):
            new_button = InlineKeyboardButton(text=cities.get(i_key)[1],
                                              callback_data=cities.get(i_key)[1])
            keyboard.add(new_button)
        return keyboard

    def make_url(url: str):
        """
        RU:
            Создание Inline-кнопки (отель).
            Handled by NONE.
        EN:
            Creating Inline-button (hotel).
            Handled by NONE.

        :param url: URL of hotel
        :return: InlineKeyboardMarkup
        """
        kb = InlineKeyboardMarkup()
        button = InlineKeyboardButton(text='Ссылка', url=url)
        kb.add(button)
        return kb

    def menu_keyboard() -> ReplyKeyboardMarkup:
        """
        RU:
            Создание Reply-клавиатуры (команды).
        EN:
            Creating Reply-keyboard (commands).

        :return: ReplyKeyboardMarkup
        """
        button_1 = KeyboardButton("/lowprice")
        button_2 = KeyboardButton("/highprice")
        button_3 = KeyboardButton("/bestdeal")
        button_4 = KeyboardButton("/history")
        button_5 = KeyboardButton("/mail")
        main_menu_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        main_menu_keyboard.add(button_1, button_2, button_3, button_4, button_5)
        return main_menu_keyboard

    def acceptance_keyboard() -> ReplyKeyboardMarkup:
        """
        RU:
            Создание Reply-клавиатуры ().
        EN:
            Creating Reply-keyboard ().

        :return: ReplyKeyboardMarkup
        """
        keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        yes_button = KeyboardButton(text="Да")
        no_button = KeyboardButton(text="Нет")
        keyboard.add(yes_button, no_button)
        return keyboard

    def choose_check_in() -> ReplyKeyboardMarkup:
        """
        RU:
            Создание Reply-клавиатуры (дата).
        EN:
            Creating Reply-keyboard (date).

        :return: ReplyKeyboardMarkup
        """
        keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        button_1 = KeyboardButton(text="Сегодня")
        button_2 = KeyboardButton(text="Завтра")
        button_3 = KeyboardButton(text="Другая дата")
        keyboard.add(button_1, button_2, button_3)
        return keyboard

    def log_user(message: Message) -> TelegramUser:
        """
        RU:
            Логирование нового пользователя.
        EN:
            Logging a new user.

        :param message: Message
        :return: object of TelegramUser
        """
        new_user = TelegramUser(message)
        bot_users.append_user(new_user)
        print(new_user.user_id)
        return new_user

    def log_commands(tg_user: TelegramUser, message: Message) -> None:
        """
        RU:
            Логирование команды пользователя.
        EN:
            Logging the user's command.

        :param tg_user: TelegramUser
        :param message: Message
        :return:
        """
        tg_user.log_command(Command(message.text))

    @bot.message_handler(content_types=['text'], commands=['/back'])
    def add_mail(message: Message):
        """
        RU:
            Добавление почты пользователя.
        EN:
            Adding user mail.

        :param message: Message
        :return:
        """
        if message.text != '/back':
            if re.findall(r'.+@.+\.', message.text):
                History(message.from_user.id).set_mail(message.text)
                bot.send_message(message.from_user.id, 'Почта успешно добавлена')
                return commands_print(message)
            else:
                bot.send_message(message.from_user.id, 'Некорректный ввод, попробуйте ещё раз.'
                                                       '\nЧтобы вернуться назад напишите /back')
                bot.register_next_step_handler(message, add_mail)
        else:
            return commands_print(message)

    def check_iter(some_iter: Iterator) -> bool:
        """
        RU:
            Проверка итератора на наличие итераций.
        EN:
            Checking the iterator for iterations.

        :param some_iter: Iterator
        :return: bool
        """
        try:
            next(some_iter)
            return isinstance(some_iter, Iterator)
        except (StopIteration, TypeError):
            return False

    def set_data(tg_user: TelegramUser) -> TelegramUser:
        """
        RU:
            Работа с запросом пользователя, реализация многопользовательского режима через класс TelegramUser
            Установление флага, что пользователь ищет отель
        EN:
            Working with a user request, implementing multi-user mode through the Telegram User class
            Setting the flag that the user is looking for a hotel

        :param tg_user: object of TelegramUser
        :return: object of TelegramUser
        """
        tg_user.hotel.iterator = search_hotels(tg_user, check_gen=False).__iter__()
        tg_user.keyboard_control = False
        tg_user.hotel.description, tg_user.hotel.hotel_id, tg_user.hotel.hotel_url = next(tg_user.hotel.iterator)
        tg_user.hotel.photos = BidirectionalIterator(send_photos(tg_user.hotel.hotel_id, tg_user.user_id))
        return tg_user

    # --------------------------------------------------------------------------------------------------------------------

    @bot.message_handler(commands=['start'])
    def commands_print(message: Message):
        """
        RU:
            Стартовая точка пользования ботом. Вывод команд.
        EN:
            The starting point of using the bot. Output of commands.

        :param message: Message
        :return:
        """
        main_menu_keyboard = menu_keyboard()
        bot.send_message(message.from_user.id,
                         "Список команд:\n"
                         "/lowprice - Узнать топ самых дешёвых отелей в городе\n"
                         "/highprice - Узнать топ самых дорогих отелей в городе\n"
                         "/bestdeal - Ручная выборка цен и расстояния до центра\n"
                         "/history - Узнать историю поиска отелей\n"
                         "/mail - Добавить/Изменить почту (вариант отправки Вашей истории)",
                         reply_markup=main_menu_keyboard)
        bot.register_next_step_handler(message, menu)
        log_user(message)

    @bot.message_handler(commands=["lowprice", "highprice", "bestdeal", "history", "mail"])
    def menu(message: Message):
        """
        RU:
            Функция, определяющая дальнейшие шаги работы с ботом.
            Ветвление
        EN:
            The func that determines the next steps of working with the bot.
            Branching

        :param message: Message
        :return:
        """
        tg_user = bot_users.get_user_from_id(message.from_user.id)
        if tg_user:
            if tg_user.keyboard_control:
                if message.text in ("/lowprice", "/highprice", "/bestdeal"):
                    log_commands(tg_user, message)
                    bot.send_message(message.from_user.id, "Введите город...", reply_markup=cities_reply_kb())
                    bot.register_next_step_handler(message, choose_city)
                elif message.text == "/history":
                    bot.send_message(tg_user.user_id, 'Пожалуйста, выберите один из вариантов',
                                     reply_markup=choose_history('start'))
                elif message.text == "/mail":
                    bot.send_message(message.from_user.id, 'Введите вашу почту')
                    bot.register_next_step_handler(message, add_mail)
                else:
                    bot.send_message(message.from_user.id, "Некорректная команда")
                    return commands_print(message)
            else:
                bot.send_message(message.from_user.id, 'Перед тем, как начать поиск,'
                                                       ' пожалуйста, завершите текущий сеанс')
        else:
            bot.send_message(message.from_user.id, "Чтобы начать работу с ботом, напишите /start")
            bot.register_next_step_handler(message, commands_print)

    @bot.message_handler(content_types=['text'])
    def choose_city(message: Message):
        """
        RU:
            Вывод Inline-клавиатуры (city, make_inline_kb).
        EN:
            Output Inline-keyboard (city, make_inline_kb).

        :param message: Message
        :return:
        """
        tg_user = bot_users.get_user_from_id(message.from_user.id)
        if tg_user:
            if not message.text.startswith('/'):
                tg_user.cities = City()
                tg_user.hotel = Hotel()
                tg_user.cities.response = search_city(message.text)
                keyboard = make_inline_kb(tg_user.cities.response)
                if len(keyboard.keyboard) == 0:
                    question = "К сожалению, город не был найден."
                else:
                    question = "Уточните местоположение города..."
                bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
            else:
                bot.send_message(message.from_user.id, '/back - чтобы вернуться назад')
                bot.register_next_step_handler(message, commands_print)
        else:
            return commands_print(message)

    def send_history(call: CallbackQuery) -> None:
        """
        RU:
            Десериализация истории пользователя, вывод истории в чат.
        EN:
            Deserialization of the user's history, output of the history to the chat.

        :param call: CallbackQuery
        :return:
        """
        if check_iter(History(call.message.chat.id).send_all()):
            user_history = History(call.message.chat.id).send_all()
            for i_hotel in user_history:
                if len(i_hotel) == 2:
                    new_command = f'Название команды - {i_hotel[0][0]}\n' \
                                  f'Дата - {i_hotel[0][1]}\n' \
                                  f'Время - {i_hotel[0][2]}'
                    bot.send_message(call.message.chat.id, new_command)
                    hotel_info = i_hotel[1]
                else:
                    hotel_info = i_hotel
                info, photos = hotel_info[1].replace(',', '\n'), [InputMediaPhoto(i_url) for i_url in hotel_info[2]]
                bot.send_message(call.message.chat.id, info, reply_markup=make_url(hotel_info[0]))
                try:
                    bot.send_media_group(call.message.chat.id, photos[:6])
                except telebot.apihelper.ApiException:
                    bot.send_message(call.message.chat.id, 'Не удалось подгрузить фотки :(')
        else:
            bot.edit_message_text('Ваша история поиска пуста', call.message.chat.id, call.message.message_id)

    @bot.message_handler(content_types=['text'])
    def choose_date(message):
        """
        RU:
            Выбор даты заезда (дата)
        EN:
            Choosing the check-in date (date)

        :param message: Message
        :return:
        """
        keyboard = choose_check_in()
        bot.send_message(message.chat.id, "Выберите дату заезда", reply_markup=keyboard)
        bot.register_next_step_handler(message, check_in)

    @bot.message_handler(content_types=['text'])
    def check_in(message: Message):
        """
        RU:
            Функция обработки выбранной даты заезда (дата, choose_date)
        EN:
            The function of handling the selected check-in date (date, choose_date)

        :param message: Message
        :return:
        """
        tg_user = bot_users.get_user_from_id(message.from_user.id)
        if message.text.lower() == "сегодня":
            tg_user.check_in = datetime.utcnow().date()
            return check_out(message, flag=False)
        elif message.text.lower() == "завтра":
            tg_user.check_in = datetime.utcnow().date() + timedelta(days=1)
            return check_out(message, flag=False)
        elif message.text.lower() == "другая дата":
            calendar, step = MyStyleCalendar(calendar_id=1).build()
            bot.send_message(message.from_user.id, f"Выберите дату заезда", reply_markup=calendar)
        else:
            keyboard = choose_check_in()
            bot.send_message(message.from_user.id, "Я вас не понял, выберите одну из команд на вашей клавиатуре.",
                             reply_markup=keyboard)
            bot.register_next_step_handler(message, check_in)

    @bot.message_handler(content_types=['text'])
    def check_out(message: Message, flag: bool):
        """
        RU:
            Выбор даты отъезда (дата)
        EN:
            Choosing the check-out date (date)

        :param message: Message
        :param flag: bool, True if user selected 'Другая дата'
        :return:
        """
        calendar = MyStyleCalendar(calendar_id=2).build()[0]
        if flag:
            bot.edit_message_text(text='Выберите дату отъезда', chat_id=message.chat.id,
                                  message_id=message.message_id)
            bot.edit_message_reply_markup(message.chat.id, message.message_id,
                                          reply_markup=calendar)
        else:
            bot.send_message(message.from_user.id, "Дата отъезда", reply_markup=calendar)

    @bot.message_handler(content_types=['text'])
    def range_prices(message: Message):
        """
        RU:
            '/bestdeal' ветка, запрос диапазона цен отелей.
        EN:
            '/bestdeal' branch, request for a range of hotel prices.

        :param message: Message
        :return:
        """
        if re.findall(r'^\d+-\d+$', message.text):
            tg_user = bot_users.get_user_from_id(message.from_user.id)
            price_range = message.text.split("-")
            price_min, price_max = int(price_range[0]), int(price_range[1])
            if price_min > price_max:
                price_min, price_max = price_max, price_min
            tg_user.hotel.price_range = {'priceMin': price_min, 'priceMax': price_max}
            bot.send_message(message.from_user.id, "Укажите максимально допустимое расстояние до центра в км.")
            bot.register_next_step_handler(message, distance_from_centre)
        else:
            bot.send_message(message.from_user.id, "Некорректный ввод, введите два числа в формате 'число'-'число'.")
            bot.register_next_step_handler(message, range_prices)

    @bot.message_handler(content_types=['text'])
    def distance_from_centre(message: Message):
        """
        RU:
            '/bestdeal' ветка, запрос максимально допустимого расстояния от отеля до центра.
        EN:
            '/bestdeal' branch, request the maximum allowable distance from the hotel to the center

        :param message: Message
        :return:
        """
        tg_user = bot_users.get_user_from_id(message.from_user.id)
        if re.findall(r'^\d+$', message.text):
            tg_user.hotel.distance = int(message.text)
            keyboard = choose_check_in()
            bot.send_message(message.from_user.id, "Выберите дату заезда", reply_markup=keyboard)
            bot.register_next_step_handler(message, check_in)
        else:
            bot.send_message(message.from_user.id, "Введите число...")
            bot.register_next_step_handler(message, distance_from_centre)

    def hotels_iterator(tg_user_id: int) -> None:
        """
        RU:
            Десериализация отелей, вывод отелей в чат (отель)
        EN:
            Deserialization of hotels, the output of hotels in the chat (hotel)

        :param tg_user_id: integer
        :return:
        """
        tg_user = bot_users.get_user_from_id(tg_user_id)
        test_iter = search_hotels(tg_user=tg_user, check_gen=True)
        if check_iter(test_iter):
            tg_user = set_data(tg_user)
            bot.send_photo(tg_user_id, tg_user.hotel.photos.next(), caption=tg_user.hotel.description,
                           reply_markup=photo_alb_kb(tg_user.hotel.hotel_url))
        else:
            bot.send_message(tg_user_id, "К сожалению, по данному запросу отелей не нашлось.")

    @bot.message_handler(content_types=["text"])
    def finally_block(message: Message):
        """
        RU:
            Конечная точка работы с запросом пользователя.
        EN:
            The endpoint of working with the user's request.

        :param message: Message
        :return:
        """
        tg_user = bot_users.get_user_from_id(message.from_user.id)
        tg_user.keyboard_control = True
        if message.text.lower() == "да":
            return commands_print(message)
        elif message.text.lower() == "нет":
            bot.send_message(message.from_user.id, "До свидания!\n/start - чтобы начать заново")
            bot.register_next_step_handler(message, commands_print)
        else:
            bot.send_message(message.from_user.id, f"{message.from_user.first_name}, я Вас не понял, введите Да/Нет")
            bot.register_next_step_handler(message, finally_block)


if __name__ == '__main__':
    class MyStyleCalendar(WMonthTelegramCalendar):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.min_date = datetime.utcnow().date()

        prev_button = "⬅"
        next_button = "➡"
        empty_month_button = ""
        empty_year_button = ""


    token = getenv("TOKEN")
    bot = telebot.TeleBot(token)
    bot_users = TelegramUsers()
    main()
    bot.polling(none_stop=True)
