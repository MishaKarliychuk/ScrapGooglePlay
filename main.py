import time
from services import *
import asyncio
import aiohttp
import csv


#
# API_TOKEN = '5255045109:AAEvvHJ_RpultbDrlRf4YRpJTuMuYX3au2o'
# import telebot
# bot = telebot.TeleBot(API_TOKEN, parse_mode=None)
#
# @bot.message_handler(func=lambda message: True)
# def send_welcome(message):
#     if message.text == 'start_scrap':
#         bot.reply_to(message, "Скрапинг начат, ждите файл (не пишите это сообщение еще раз)")


# Достаем прокси
proxy_list = str(read_proxy_file()).split('\n')
proxy_data = proxy_list[0].split(':')
proxi = {
    "http": f"http://{proxy_data[2]}:{proxy_data[3]}@{proxy_data[0]}:{proxy_data[1]}",
    # @{proxy_data[2]}:{proxy_data[3]}
}


async def main():
    # Парсим ссылки
    search_urls = generate_urls_search_page()
    app_urls = parse_app_urls_from_search_page(search_urls, proxi=proxi)
    emails = []

    """ Распределяем на равные к-во ссылки, которые будем парсить """
    for page in range(round(len(app_urls) / PAGINATION)):
        tasks = []
        from_ = page * PAGINATION
        to_ = (page + 1) * PAGINATION
        for app_url in list(app_urls)[from_:to_:]:
            tasks.append(asyncio.create_task(get_email_of_app(app_url)))
        new_emails = await asyncio.gather(*tasks)
        emails += new_emails
        # time.sleep(25)

    # Делаем подсчет
    emails = list(set(emails))
    print("Всего emails: ", len(emails), " Всего ошибок было: ", len(ERROR_APP_URL))
    # Записываем у файл
    with open("EMAILS.csv", "w") as file:
        wr = csv.writer(file)
        emails_row = []

        for email in emails:
            if email is not None and "gmail" in str(email):
                emails_row.append([email])

        wr.writerows(emails_row)


asyncio.run(main())


