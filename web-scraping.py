from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import datetime
import time

def get_data(search_term):
    url = f"https://www.newegg.ca/p/pl?d={search_term}&N=4131"
    page = requests.get(url).text
    doc = BeautifulSoup(page, "html.parser")

    page_text = doc.find(class_="list-tool-pagination-text").strong
    pages = int(str(page_text).split("/")[-2].split(">")[-1][:-1])

    items_found = {}

    for page in range(1, pages + 1):
        # url = f"https://www.newegg.ca/p/pl?d={search_term}&N=4131&page={page}"
        url = f'https://www.newegg.ca/p/pl?d={search_term}&Order=1&page={page}'
        page = requests.get(url).text
        doc = BeautifulSoup(page, "html.parser")
        div = doc.find(class_="item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell")
        items = div.find_all(text=re.compile(search_term))

        for item in items:
            parent = item.parent
            if parent.name != "a":
                continue

            link = parent['href']
            next_parent = item.find_parent(class_="item-container")
            try:
                price = next_parent.find(class_="price-current").find("strong").string
                items_found[item] = {"price": int(price.replace(",", "")), "link": link}
            except:
                pass

    sorted_items = sorted(items_found.items(), key=lambda x: x[1]['price'])
    item_list=[sorted_items[i][0] for i in range(len(sorted_items))]
    price_list=[sorted_items[i][1]['price'] for i in range(len(sorted_items))]
    link_list=[sorted_items[i][1]['link'] for i in range(len(sorted_items))]
    return item_list, price_list, link_list

start = time.time()
# get iphone data
item_list, price_list, link_list = get_data('iphone')
brand_list, color_list, main_display_size_list, operating_system_list, RAM_list, built_in_storage_list, option_list, date_first_available_list, overview_list  = [], [],[],[],[],[],[],[],[]
for link in link_list:
    url = link
    page = requests.get(url).text
    doc = BeautifulSoup(page, "html.parser")
    for t in doc.find_all('div', attrs={'id':'arimemodetail'}):
        overview = t.text
    overview_list.append(overview)
    params = doc.find_all('td')
    params = [str(params[i]).split(">")[1].split("<")[0] for i in range(len(params))]
    variables = doc.find_all('th')
    variables = [str(variables[i]).split(">")[1].split("<")[0] for i in range(len(variables))]
    d = dict(zip(variables, params))
    try:
        brand_list.append(d['Brand'])
    except KeyError:
        brand_list.append('')
    try:
        color_list.append(d['Color'])
    except KeyError:
        color_list.append('')
    try:
        main_display_size_list.append(d['Main Display Size'])
    except KeyError:
        main_display_size_list.append('')
    try:
        operating_system_list.append(d['Operating System'])
    except KeyError:
        operating_system_list.append('')
    try:
        RAM_list.append(d['RAM'])
    except KeyError:
        RAM_list.append('')
    try:
        built_in_storage_list.append(d['Built-in Storage'])
    except KeyError:
        built_in_storage_list.append('')
    try:
        option_list.append(d['Option'])
    except KeyError:
        option_list.append('')
    try:
        date_first_available_list.append(d['Date First Available'])
    except KeyError:
        date_first_available_list.append('')


df = pd.DataFrame({'item': item_list,'price':price_list, 'link':link_list, 'brand':brand_list,
'color':color_list, 'main_display_size':main_display_size_list, 
'operating_system':operating_system_list, 'RAM':RAM_list, 'built_in_storage':built_in_storage_list, 
'option':option_list, 'date_first_available':date_first_available_list, "overview":overview_list})
df.to_csv('iphone1.csv', index=0)

# clean iphone data
ip = df.copy()
ip['date_first_available'] = [str(datetime.datetime.strptime(ip['date_first_available'][i], "%B %d, %Y").date()) if ip['date_first_available'][i] != "" else "" for i in range(len(ip))]
ip.to_csv('clean_iphone1.csv', index=0)


# keyboard
item_list, price_list, link_list = get_data('keyboard')
date_first_available_list, overview_list  = [], []
for link in link_list:
    url = link
    page = requests.get(url).text
    doc = BeautifulSoup(page, "html.parser")
    for t in doc.find_all('div', attrs={'id':'arimemodetail'}):
        overview = t.text
    overview_list.append(overview)
    params = doc.find_all('td')
    params = [str(params[i]).split(">")[1].split("<")[0] for i in range(len(params))]
    variables = doc.find_all('th')
    variables = [str(variables[i]).split(">")[1].split("<")[0] for i in range(len(variables))]
    d = dict(zip(variables, params))
    try:
        date_first_available_list.append(d['Date First Available'])
    except KeyError:
        date_first_available_list.append('')

df = pd.DataFrame({'item': item_list,'price':price_list, 'link':link_list, 'date_first_available':date_first_available_list, "overview":overview_list})
df.to_csv('keyboard1.csv', index=0)

# clean keyboard data
kb = df.copy()
kb['date_first_available'] = [str(datetime.datetime.strptime(kb['date_first_available'][i], "%B %d, %Y").date()) if kb['date_first_available'][i] != "" else "" for i in range(len(kb))]
kb.to_csv('clean_keyboard1.csv', index=0)
print(start - time.time(), 'seconds')
print('Done')