import requests
from bs4 import BeautifulSoup
import csv
import json

url = 'https://play.google.com/store/search?q=adblock%20for%20samsung&c=apps&hl=en'
# Создать отдельную функцию которая получает всю инфу, и в нее поместить этот массив

def get_html(url):
    r = requests.get(url)
    r.encoding = 'utf8'
    return r.text

def get_urls(html):
    product_urls = []
    soup = BeautifulSoup(html, 'lxml')
    links = soup.find('div', class_='ZmHEEd').find_all('a', class_='poRVub')
    for i in links:
        link = 'https://play.google.com' + i.get('href')
        product_urls.append(link)
    return product_urls

def get_data(html):
    soup = BeautifulSoup(html, 'lxml')
    #name = soup.find()
    #url Видимо нужно взять из массива, который в этот момент обрабатывается
    #company
    #installs
    #reviews
    #rating
    #mail Возможно его нет
    #website

def csv_read(data):
    with open("data.csv", 'a') as file:
        writer = csv.writer(file)
        writer.writerow([data["link"]])

#csv_read(get_urls(get_html(url)))

# Находим ссылку через json.load (цикл)
# Реквест на DOM
# Получаем Dom
# Находим ссылки на карточки товаров
# Открываем в новом запросе (цикл)
# Берем всю инфу
# Парсим ее в файл
