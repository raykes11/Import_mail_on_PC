import asyncio
import datetime
import email
import imaplib
import json
import re
import time
from email.header import decode_header

from aioimaplib import aioimaplib
from bs4 import BeautifulSoup
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Email


@database_sync_to_async
def get_all(user_id):
    return list(Email.objects.filter(user_id=user_id).all().values())


@database_sync_to_async
def get_bytes_message(user_id):
    print("Get email")
    list_ = list(Email.objects.filter(user_id=user_id).values_list('bytes_message', flat=True))
    return list_


@database_sync_to_async
def save_db_bulk(data_list):
    objects = [Email(**item) for item in data_list]
    Email.objects.bulk_create(objects)
    print("Add_DB")


class WSConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print(f"Adding client {self.channel_name} to group 'updates'")
        await self.channel_layer.group_add("updates", self.channel_name)
        await self.accept()
        user = self.scope.get("user")
        user_id = user.id
        print(user)
        # Подключение к почте и мониторинг ее
        await self.conect_to_email()
        # Получить все писма пользователя
        user_list = await get_all(user_id)
        await self.send(text_data=json.dumps({
            'type': 'initial_data',
            'user': user_list[::-1],
        }))

    async def conect_to_email(self):
        # Подключение к почте и мониторинг ее
        while True:
            await self.import_mail()
            await asyncio.sleep(30)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("updates", self.channel_name)

    async def send_update(self, event):
        # Отправка сообщения клиенту
        print("Received event in send_update:", type(event["text_data"]))
        await self.send(event["text_data"])

    async def import_mail(self):
        user = self.scope.get("user")
        user_id = user.id
        # Получение всех байт номера сообщений

        byte_numbers_in_db = await get_bytes_message(user_id)
        print("Get email complete")

        # Получить все писма пользователя
        user_list = await get_all(user_id)
        user_list = user_list[::-1]

        # Подключение к почте
        username = user.name
        mail_pass = user.mail_pass
        imap_server = user.imap_server
        imap = imaplib.IMAP4_SSL(imap_server)
        imap.login(username, mail_pass)

        # Получение всех писем
        imap.select("INBOX")
        unseen = imap.uid('search', "ALL", "ALL")

        # Получение перевод в список
        byte_iter = unseen[1][0].split()
        len_byte_iter = len(byte_iter)

        await self.send(text_data=json.dumps({
            'type': 'send_update',
            'user': user_list, 'email': 0,
            "add_email": 0,
            "max_email": len_byte_iter,
            'time': -1,
        }))
        # Поиск отсутствующих сообщений
        byte_numbers_list = [msg for msg in byte_iter if str(msg) not in byte_numbers_in_db]
        len_byte_numbers_list = len(byte_numbers_list)

        await self.send(text_data=json.dumps({
            'type': 'send_update',
            'user': user_list, 'email': 0,
            "add_email": len_byte_numbers_list,
            "max_email": len_byte_iter,
            'time': -1,
        }))
        await asyncio.sleep(2)

        list_number_uid = []  # Разбиваем строку UIDs на список
        # Преобразуем каждый UID в sequence number
        for uid in byte_numbers_list:
            status, data = imap.uid('fetch', uid, '(RFC822.SIZE)')
            if status == 'OK':
                seq_num = data[0].split()[0]
                list_number_uid.append((seq_num, uid))
                print(len(list_number_uid))
        imap.logout()

        print('next')
        await self.async_import_mail(username, mail_pass, imap_server, user_id, list_number_uid, len_byte_iter,
                                     len_byte_numbers_list, user_list)

    async def async_import_mail(self, username, mail_pass, imap_server, user_id, list_number_uid, len_byte_iter,
                                len_byte_numbers_list, user_list):
        # Подключаемся к серверу IMAP
        mail_pass = mail_pass
        username = username
        imap_server = imap_server
        imap = aioimaplib.IMAP4_SSL(imap_server, timeout=600)

        await imap.wait_hello_from_server()
        await imap.login(username, mail_pass)
        await imap.select("INBOX")

        # Обрабатываем сообщения пачками
        batch_size = 20  # количество сообщений для обработки за раз
        len_list_number_uid = len(list_number_uid)

        # Обработка отсутствия новых сообщений
        if len_list_number_uid == 0:
            await self.send(text_data=json.dumps({
                'type': 'send_update',
                'user': user_list, 'email': 0,
                "add_email": len_byte_numbers_list,
                "max_email": len_byte_iter,
                'time': 0,
            }))

        else:

            for i in range(0, len_list_number_uid, batch_size):
                # Начало таймера
                start_time = datetime.datetime.now()
                byte_iter_batch = list_number_uid[i:i + batch_size]

                # Обработка сообщений
                await self.process_messages(user_id, imap, byte_iter_batch)
                await asyncio.sleep(2)

                # Конец таймера
                elapsed_time = datetime.datetime.now() - start_time
                speed = batch_size / (elapsed_time.total_seconds() / 60)
                time_complite = len_list_number_uid / speed
                time_complite = int(round(time_complite, 0))

                await self.send(text_data=json.dumps({
                    'type': 'send_update',
                    'user': user_list, 'email': i + 1,
                    "add_email": len_byte_numbers_list,
                    "max_email": len_byte_iter,
                    'time': time_complite,
                }))
                len_list_number_uid = len_list_number_uid - batch_size

            await self.send(text_data=json.dumps({
                'type': 'send_update',
                'user': user_list, 'email': len_byte_numbers_list + 20,
                "add_email": len_byte_numbers_list,
                "max_email": len_byte_iter,
                'time': time_complite,
            }))

        await imap.logout()

    async def process_messages(self, user_id, imap, byte_iter_batch):
        list_dict = []
        for number in byte_iter_batch:
            res, msg = await imap.fetch(number[0].decode(), '(RFC822)')
            if res == 'OK':
                list_attachment = []
                print(number, ' ', res)
                msg = email.message_from_bytes(msg[1])

                # Обработка сообщений
                letter_date = email.utils.parsedate_tz(msg["Date"])
                struct_time = letter_date[:9]
                timestamp = time.mktime(struct_time)
                date = datetime.datetime.fromtimestamp(timestamp)

                # # Форматирование даты
                date = date.strftime('%Y-%m-%d %H:%M:%S %Z%z')
                letter_id = msg["Message-ID"]
                letter_from = msg["Return-path"]
                print(date)

                # # Расшифровка заголовка
                if msg["Subject"] is None or decode_header(msg["Subject"])[0][1] is None:
                    title = 'None'
                else:
                    title = decode_header(msg["Subject"])[0][0]
                    if isinstance(title, bytes):
                        try:
                            title = title.decode(decode_header(msg["Subject"])[0][1] or 'utf-8')
                        except LookupError:
                            pass

                # # Расшифровка сообщений
                cleaned_text = None
                for payload in msg.walk():
                    content_type = payload.get_content_type().lower()
                    if content_type == "text/plain" or content_type == "text/html":
                        text_content = payload.get_payload(decode=True)
                        charset = payload.get_content_charset() or "utf-8"

                        try:
                            decoded_text = text_content.decode(charset)
                        except (UnicodeDecodeError, AttributeError):
                            decoded_text = text_content.decode("utf-8", errors="ignore")

                        if content_type == "text/html":
                            soup = BeautifulSoup(decoded_text, "html.parser")
                            decoded_text = soup.get_text()

                        cleaned_text = re.sub(r'\n\s*\n+', '\n', decoded_text).strip()
                    if payload.get_content_disposition() == 'attachment':
                        list_attachment.append(decode_header(payload.get_filename())[0][0].decode())

                dict_ = {
                    'id_message': letter_id,
                    'bytes_message': number[1],
                    'title': title,
                    'data_export': letter_from,
                    'data_import': date,
                    'message': cleaned_text,
                    'attachment': list_attachment,
                    'user_id': user_id
                }
                list_dict.append(dict_.copy())
                print(dict_)

        await save_db_bulk(list_dict)
