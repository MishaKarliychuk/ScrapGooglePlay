import string
import time

import aiohttp
import requests
from bs4 import BeautifulSoup

from config import *


# def get_app_urls(html):
#     apps = html.findAll("div", class_="wXUyZd")
#     urls = [domain + app.find("a").get("href") for app in apps]
#     return urls

def read_proxy_file():
    with open("proxy.txt", "r") as file:
        geo = file.read()
    return geo


def read_geo_file():
    with open("geo.txt", "r") as file:
        geo = file.read()
    return geo


# def get_urls_to_parse_from_main_page(urls_to_parse, proxies):
#     html = requests.get(url_main, proxies=proxies)
#     soup = BeautifulSoup(html.content, 'html.parser')
#
#     # Достаем все ссылки с главного меню
#     green_buttons = soup.findAll("div", class_="W9yFB")
#     for button in green_buttons:
#         urls_to_parse.append(domain + button.find("a").get("href"))


def parse_email_of_app_url(html):
    """ Парсит со страницы приложения почту """
    block = html.find("div", class_="SfzRHd", attrs={"id": "developer-contacts"})
    if block:
        chapters = block.findAll("div", class_="pSEeg")
        for chapter in chapters:
            if '@' in chapter.text:
                return chapter.text


async def get_email_of_app(app_url):
    """ Делает запрос на страницу приложения и возвращает email """
    try:
        async with aiohttp.request('GET', app_url) as res:
            text = await res.text()
            soup = BeautifulSoup(text, 'html.parser')
            email = parse_email_of_app_url(soup)
            return email

    except aiohttp.client_exceptions.ServerDisconnectedError:
        print("dddd")
        time.sleep(3)
    except aiohttp.client_exceptions.ClientOSError:
        print("Disconnect server. COUNT_OF_MISTAKE: ", len(ERROR_APP_URL))
        ERROR_APP_URL.append(app_url)
    except aiohttp.client_exceptions.ClientPayloadError:
        ERROR_APP_URL.append(app_url)
        time.sleep(10)

# def get_app_urls(app_urls, urls_to_parse, proxies):
#     """ Парсит со страницы выбора приложений ссылки на приложения """
#     for url_to_parse in urls_to_parse:
#         print("Парсим такую ссылку ", url_to_parse, sep="   ---->    ")
#         html = requests.get(url_to_parse, proxies=proxies)
#         soup = BeautifulSoup(html.content, 'html.parser')
#
#         apps = soup.findAll("div", class_="ULeU3b")
#         print(len(apps))
#         for app in apps:
#             a_tag = app.find("a")
#             if a_tag is None:
#                 continue
#             app_urls.append(domain + a_tag.get("href"))
#


def parse_app_urls_from_search_page(search_urls, proxi):
    """ Парсит ссылки на приложения из страницы поиска гугл плей """
    app_urls = []

    for url in search_urls:
        print("Парсим такую ссылку ", url, sep="   ---->    ")
        html = requests.get(url, proxies=proxi)
        soup = BeautifulSoup(html.content, 'html.parser')

        apps = soup.findAll("div", class_="ULeU3b")
        print(len(apps))
        for app in apps:
            a_tag = app.find("a")
            if a_tag is None:
                continue
            app_urls.append(domain + a_tag.get("href"))

    return app_urls


def generate_urls_search_page():
    """ Генерирует ссылки поиска гугл плей """
    search_urls = []

    # proxy_data = proxy.split(':')
    # proxies = {
    #     "http": f"http://{proxy_data[2]}:{proxy_data[3]}@{proxy_data[0]}:{proxy_data[1]}", # @{proxy_data[2]}:{proxy_data[3]}
    #     # "https": f"socks5://{proxy_data[0]}:{proxy_data[1]}@{proxy_data[2]}:{proxy_data[3]}",
    # }

    geo = read_geo_file().replace(" ", "")
    geo_list = geo.split(",")
    for g in geo_list:
        search_urls.append(url_searching.format(g))

    symbols = string.ascii_lowercase
    for symbol in symbols:
        search_urls.append(url_searching.format(symbol))

    words = (requests.get("https://www.randomlists.com/data/nouns.json").json())['data'][:50:]
    for word in words:
        search_urls.append(url_searching.format(word))

    for word in ARABIC_WORDS:
        search_urls.append(url_searching.format(word))

    return search_urls
