# RU: Подключение к базе данных и почтовому ящику
# EN: Connecting to a database and mailbox


import psycopg2
import smtplib
from os import getenv

host = getenv('YOUR_HOST')
user = getenv('YOUR_USER')
password = getenv('YOUR_DB_PASSWORD')
db_name = getenv('YOUR_DATABASE')

connection = psycopg2.connect(
    host=host,
    password=password,
    user=user,
    database=db_name
)
connection.autocommit = True


def send_mail(message: str, address: str) -> bool:
    """
    RU:
        Отправка сообщения на почту
    EN:
        Sending a message to the mail

    :param message: message you need to send
    :param address: address to send
    :return:
    """
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as mail:
            mail.starttls()
            mail.login(getenv('YOUR_EMAIL'), getenv('YOUR_EMAIL_PASSWORD'))
            mail.sendmail(from_addr=getenv('YOUR_EMAIL'), to_addrs=address, msg=message.encode('utf-8'))
            return True
    except smtplib.SMTPException as exc:
        print(f'WARNING!!!\n{exc}')
        return False
