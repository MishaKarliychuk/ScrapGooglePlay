import string

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


def get_urls_to_parse_from_main_page(urls_to_parse, proxies):
    html = requests.get(url_main, proxies=proxies)
    soup = BeautifulSoup(html.content, 'html.parser')

    # Достаем все ссылки с главного меню
    green_buttons = soup.findAll("div", class_="W9yFB")
    for button in green_buttons:
        urls_to_parse.append(domain + button.find("a").get("href"))


def get_app_urls(app_urls, urls_to_parse, proxies):
    for url_to_parse in urls_to_parse:
        print("Парсим такую ссылку ", url_to_parse, sep="   ---->    ")
        html = requests.get(url_to_parse, proxies=proxies)
        soup = BeautifulSoup(html.content, 'html.parser')

        apps = soup.findAll("div", class_="wXUyZd")
        for app in apps:
            app_urls.append(domain + app.find("a").get("href"))


def get_email_of_app(html):
    blocks = html.findAll("div", class_="hAyfc")
    for block in blocks:
        if '@' in block.text:
            a = block.find("a", class_="hrTbp euBY6b")
            if a is None:
                return None
            return a.text


def main_get_app_urls(app_urls, proxy):
    proxy_data = proxy.split(':')
    proxies = {
        "http": f"http://{proxy_data[2]}:{proxy_data[3]}@{proxy_data[0]}:{proxy_data[1]}", # @{proxy_data[2]}:{proxy_data[3]}
        # "https": f"socks5://{proxy_data[0]}:{proxy_data[1]}@{proxy_data[2]}:{proxy_data[3]}",
    }

    urls_to_parse = []

    # достаем ссылки на страницы, откуда будем парсить
    get_urls_to_parse_from_main_page(urls_to_parse, proxies)

    geo = read_geo_file().replace(" ", "")
    geo_list = geo.split(",")
    for g in geo_list:
        urls_to_parse.append(url_searching.format(g))

    symbols = string.ascii_lowercase
    for symbol in symbols:
        urls_to_parse.append(url_searching.format(symbol))

    words = (requests.get("https://www.randomlists.com/data/nouns.json").json())['data'][:50:]
    for word in words:
        urls_to_parse.append(url_searching.format(word))

    for word in ARABIC_WORDS:
        urls_to_parse.append(url_searching.format(word))

    get_app_urls(app_urls, urls_to_parse, proxies)
