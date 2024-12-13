# Import mail on PC

## Описание
Import_mail_on_PC — это Python проект, который позволяет выгружать сообщение с почты на ваш ПК, представляяет результат в виде таблице HTML

## Установка
Для работы с Import_mail_on_PC необходимо установить библиотеку 
1. Django	4.2+
2. Djangorestframework=3.14.0 
3. Channels==4.0.0
4. Channels-redis==4.1.0
5. Daphne==4.0.0
6. aiomapplib==1.1.0
7. beautifulsoup==4.12.3

Установить:
pip install -r requirements.txt

## Запуск проекта
Настройте почту для работы сторонними программами через IMAP протокол. Создайте пароль для стороннего приложения.

Для [Yandex](https://yandex.ru/support/id/ru/authorization/app-passwords.html).

Для [Google](https://support.google.com/mail/answer/7126229?hl=ru#zippy=%2C%D0%BD%D0%B5-%D1%83%D0%B4%D0%B0%D0%B5%D1%82%D1%81%D1%8F-%D0%B2%D0%BE%D0%B9%D1%82%D0%B8-%D0%B2-%D0%BF%D0%BE%D1%87%D1%82%D0%BE%D0%B2%D1%8B%D0%B9-%D0%BA%D0%BB%D0%B8%D0%B5%D0%BD%D1%82)

Для [Mail](https://help.mail.ru/mail/security/protection/external/)

Запустить manage.py.

## Особенности проекта

Проект реализован с использованием асинхронной библиотеке *aiomapplib* для работы с почтой.
Что позволит ускорить работу проектов связных обработки писем.
Приблизительное время обработки сообщений 200 сообщений в минуту. 
