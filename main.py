import time
from aiogram import Bot, Dispatcher, types
from aiogram import executor
from services import *
import asyncio
import aiohttp
import csv
from aiogram.types import InputFile


API_TOKEN = '5255045109:AAEvvHJ_RpultbDrlRf4YRpJTuMuYX3au2o'
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler()
async def process_start_command(message: types.Message):
    if message.text == 'start_scrap':
        await message.answer("Скрапинг начат, ждите файл (не пишите это сообщение еще раз)")
        app_urls = []
        emails = []
        proxy_list = str(read_proxy_file()).split('\n')

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

        # async def main():
        for page in range(round(len(app_urls) / PAGINATION)):
            tasks = []
            from_ = page * PAGINATION
            to_ = (page+1) * PAGINATION
            for app_url in list(app_urls)[from_:to_:]:
                tasks.append(asyncio.create_task(get_html_of_app_page(app_url)))
            await asyncio.gather(*tasks)
            time.sleep(25)

        # asyncio.run(main())
        print("Всего emails: ", len(set(emails)), " Всего ошибок было: ", len(MISTAKEN_APP_URL))
        emails = list(set(emails))
        with open("EMAILS.csv", "w") as file:
            wr = csv.writer(file)
            emails_row = [[email] for email in emails]
            wr.writerows(emails_row)
        
        file = open("EMAILS.csv", "rb")
        await message.reply_document(file)
        file.close()

executor.start_polling(dp, skip_updates=True)