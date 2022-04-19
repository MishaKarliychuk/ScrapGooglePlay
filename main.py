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

app_urls = []
emails = []
proxy_list = str(read_proxy_file()).split('\n')

while True:
    for proxy in proxy_list:
        main_get_app_urls(app_urls, proxy)

    app_urls = list(set(app_urls))

    async def get_html_of_app_page(url):
        global COUNT_OF_MAX_MISTAKE, COUNT_OF_MISTAKE
        try:
            async with aiohttp.request('GET', url) as res:
                text = await res.text()
                soup = BeautifulSoup(text, 'html.parser')
                email = get_email_of_app(soup)
                print(email)
                emails.append(email)
        except aiohttp.client_exceptions.ServerDisconnectedError:
            time.sleep(3)
        except aiohttp.client_exceptions.ClientOSError:
            print("Disconnect server. COUNT_OF_MISTAKE: ", COUNT_OF_MAX_MISTAKE)
            MISTAKEN_APP_URL.append(url)

    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    async def main():
        for page in range(round(len(app_urls) / PAGINATION)):
            tasks = []
            from_ = page * PAGINATION
            to_ = (page+1) * PAGINATION
            for app_url in list(app_urls)[from_:to_:]:
                tasks.append(asyncio.ensure_future(get_html_of_app_page(app_url)))
            await asyncio.gather(*tasks)
            time.sleep(25)
    event_loop.run_until_complete(main())

    print("Всего emails: ", len(set(emails)), " Всего ошибок было: ", len(MISTAKEN_APP_URL))
    emails = list(set(emails))
    with open("EMAILS.csv", "w") as file:
        wr = csv.writer(file)
        emails_row = [[email] for email in emails]
        wr.writerows(emails_row)

    time.sleep(2*60)