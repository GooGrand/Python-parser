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

def get_data(html, product_url):
    soup = BeautifulSoup(html, 'lxml')
    name = soup.find('main', class_='LXrl4c').find('h1', class_='AHFaub').find('span').text
    url = product_url
    company = soup.find('a', class_='hrTbp R8zArc').text
   # installs = soup.find('div', class_='IQ1z0d').find('span', class_='htlgb')
    reviews = soup.find('span', class_='AYi5wd TBRnV').find('span').text
    rating = soup.find('div', class_='BHMmbe').text
    #mail Возможно его нет
    #website = soup.find('span', class_='htlgb').find('div').find('a', class_='hrTbp')

    pool = soup.find_all('div', class_='W4P4ne')
    add_info = pool[3].find_all('div', class_='IQ1z0d')
    installs = add_info[3].find('span', class_='htlgb').text
    website = add_info[11].find('span', class_='htlgb').find('a', class_='hrTbp')
    print(website)

    link = website.get('href')

    data_dic = {"name": name,
                "url": url,
                "company": company,
                "installs": installs,
                "reviews": reviews,
                "rating": rating,
  #              "mail": mail,
                "website": link}
    return data_dic


def csv_read(data):
    with open("data.csv", 'a') as file:
        writer = csv.writer(file)
        writer.writerow([data["name"]])
        writer.writerow([data["url"]])
        writer.writerow([data["company"]])
        writer.writerow([data["installs"]])
        writer.writerow([data["reviews"]])
        writer.writerow([data["rating"]])
        writer.writerow([data["website"]])

#csv_read(get_urls(get_html(url)))

# Находим ссылку через json.load (цикл)
# Реквест на DOM
main_html = get_html(url)
# Находим ссылки на карточки товаров
urls = get_urls(main_html)
# Открываем в новом запросе (цикл)
product_page = get_html(urls[0])
# Берем всю инфу
data = get_data(product_page, urls[0])
# Парсим ее в файл
csv_read(data)
