import requests
import csv
import json
import re
import traceback
import time
import codecs

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


EXE_PATH = r'chromedriver.exe'
PROXY = "23.23.23.23:3128"
exceptions = []
url = 'http://185.130.105.123:5053/'    # URL для парсинга
pages = []                              # Обработка ошибок при загрузке с Proxy
links_request = ["https://play.google.com/store/search?q=asdasd&c=apps&hl=en", "https://play.google.com/store/search?q=gta&c=apps&hl=en", "https://play.google.com/store/search?q=afr&c=apps&hl=en"]

with open("data_parse.csv", 'a', encoding="latin1", newline='') as file:
    fields = ['name', 'url', 'company', 'installs', 'reviews', 'rating', 'website']
    writer = csv.DictWriter(file, fields)
    writer.writeheader()

def get_page_by_selenium(link):
    opts = Options()
    opts.headless = True
    webdriver.DesiredCapabilities.CHROME['proxy'] = {
        "httpProxy": PROXY,
        "ftpProxy": PROXY,
        "sslProxy": PROXY,
        "proxyType": "MANUAL",

    }
    with webdriver.Chrome(executable_path=EXE_PATH, options=opts) as driver:
    # driver = webdriver.Chrome(executable_path=EXE_PATH, options=opts)
        driver.get(link)
        print('opening browser')
        i = 0
        while i < 8:
            print('scrolling down')
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            i += 1
    # driver.refresh()
        html = driver.page_source
        driver.close()
    return html



def check_platform(url):
    parts = url.split('/')
    if parts[2] == 'play.google.com':
        return 'google'
    elif parts[2] == 'apps.apple.com':
        return 'apple'
    pass

def prepare_data(links):                # Подготавливает url для запроса на proxy parser
    print('Packing data')
    start = time.time()
    data = { 'URLS': []}
    i = 0
    for link in links:
        url_link = {
         "URL": str(link),
         "Headers":{
            "Connection":"keep-alive",
            "User-Agent":"Mozilla\/5.0 (Macintosh; Intel Mac OS X 10.15; rv:71.0) Gecko/20100101 Firefox/71.0",
            "Upgrade-Insecure-Requests":"1"
         },
         "userId":"ID-" + str(i)
            }
        i += 1
        data['URLS'].append(url_link)
    amount = time.time() - start
    print('Packing loaded data for ' + str(amount))
    print('Loaded data is' + str(data))
    return json.dumps(data)

def get_html_links(url, dataset):                         # Обрабатывает полученные в response ссылки,
    urls = {}                                          # Пакует их в словарь вместе с url на
    json = prepare_data(dataset)
    print('Retrieving the html')
    start = time.time()
    r = requests.post(url, json)
    #r.encoding = 'utf8'
    print('Working with response ' + str(r.json))
    print('The response come in ' + str(time.time() - start))
    r = r.json()
    index = 0
    print(str(r))
    for key in r:
        if r[key]['status'] == 996:
            print('Cannot get one of the html\'s, trying again')
            pages.append(dataset[index])
        if r[key]['link'] != '':
            url = { 'link': r[key]['link'],
                    'url': dataset[index]
                     }
            urls[key] = url
        index += 1
    print('URL\'s are ' + str(urls))
    return urls

def get_html(url):
    print('Getting html')
    r = requests.get(url)
    #r.encoding = 'ISO-8859-1'
    print(r.encoding)
    return r.text

def get_url_app_store(html):
    print('Getting URL\'s')
    pass

def get_urls_google_play(html):
    print('Getting urls')
    product_urls = []
    soup = BeautifulSoup(html, 'html5lib')
    item_cards = soup.find('div', class_='Ktdaqe').find_all('c-wiz')
    print(len(item_cards))
    for item in item_cards:
        if item.find('div', class_='vU6FJ p63iDd') != None:
            a_tag = item.find('div', class_='vU6FJ p63iDd').find('a')
            link = 'https://play.google.com' + a_tag.get('href')
            print(link)
            product_urls.append(link)
    return product_urls


def get_product_data(url, urls):
    global exceptions
    product_links = get_html_links(url, urls)
    index = 0
    for product in product_links.values():
        product_html = get_html(product['link'])
        print(product)
        try:
            data = get_data(product_html, product['url'])
            index += 1
            csv_read(data)
        except BaseException as e:
            print(e, traceback.format_exc())
            exceptions.append(product['url'])
            print('The exceptions happened with this url ' + str(product['link']))
    if len(exceptions) != 0:
        print('While the parsing error happened. Trying to reload some of the html')
        return get_product_data(url, exceptions)


def get_data(html, product_url):
    soup = BeautifulSoup(html, 'html5lib')
    soup.encode('latin1')
    if 'html' in locals():
        print('html exists ' + product_url)
    name = soup.find('h1').find('span').text
    url = product_url
    company = soup.find('a', class_='hrTbp R8zArc').text
    reviews = 'there are no reviews yet'
    rating = 'there are no rating'
    installs = 'no information about installs'
    website = 'there is no website'
    if soup.find('span', class_='EymY4b') != None:
        reviews_span = soup.find('span', class_='EymY4b').find_all('span')
        reviews = str(reviews_span[1].text)
    if soup.find('div', class_='BHMmbe') != None:
        rating = soup.find('div', class_='BHMmbe').text
    #mail Возможно его нет

    pool = soup.find_all('div', class_='W4P4ne')
    for info in pool:
        if info.find_all('div', class_='hAyfc') != None:
            add_info = info.find_all('div', class_='hAyfc')
    if len(add_info) > 2:
        installs = add_info[2].find('span', class_='htlgb').text
    for item in add_info:
        if item.find('a', text=re.compile("Visit website")):
            website = item.find('a', class_='hrTbp').get('href')
        if item.find('div', text=re.compile("Installs")):
            installs = item.find('div', class_='IQ1z0d').find('span').text

    data_dic = {"name": name,
                "url": url,
                "company": company,
                "installs": installs,
                "reviews": reviews,
                "rating": rating,
  #              "mail": mail,
                "website": website}
    return data_dic


def csv_read(data):
    with open("data_parse.csv", 'a', encoding='latin1', newline='') as file:
        fields = ['name', 'url', 'company', 'installs', 'reviews', 'rating', 'website']
        writer = csv.DictWriter(file, fields)
        print(data)
        writer.writerow(data)

def parse_pages(url, request):
    # links = get_html_links(url, request)
    # for link in links.values():
    #     print(link['link'])
    #     html = get_html(link['link'])
    for link in request:
        platform = check_platform(link)
        if platform == 'google':
            html = get_page_by_selenium(link)
            urls = get_urls_google_play(html)
            print("Final urls are " + str(urls))
            get_product_data(url, urls)
            # urls = get_urls_google_play(html)
            # print("Final urls are " + str(urls))
            # product_links = get_html_links(url, urls)
            # index = 0
            # for product in product_links:
                # product_html = get_html(product)
                # print(product)
                # data = get_data(product_html, urls[index])
                # index += 1
                # csv_read(data)
        elif platform == 'apple':
            urls = get_url_app_store(html)
            print("Final urls are " + str(urls))
        else:
            print(platform)
        print('these links didn\' connected' + str(pages))

parse_pages(url, links_request)

