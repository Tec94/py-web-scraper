from operator import add
import requests, re
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept-Language': 'en,en-US;q=0.9'
}

search_query = input('Which product do you want to scrape? ').replace(' ', '+')
base_url = 'https://www.amazon.com/s?k={0}'.format(search_query)

items = []
for i in range(1, 5):
    print('Processing {0}...'.format(base_url + '&page={0}'.format(i)))
    response = requests.get(base_url + '&page={0}'.format(i), headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    results = soup.find_all('div', {'class': 's-result-item', 'data-component-type': 's-search-result'})


    for result in results:
        product_name = result.h2.text

        try:
            rating = result.find('i', {'class': 'a-icon'}).text
            rating_count = result.find_all('span', {'aria-label': True})[1].text
        except AttributeError:
            continue

        try:
            price1 = result.find('span', {'class': 'a-price-whole'}).text
            price2 = result.find('span', {'class': 'a-price-fraction'}).text
            price = float((price1 + price2).replace(',', ''))

            product_url = 'https://amazon.com' + result.h2.a['href']

            # Scrape additional data from the product page
            response = requests.get(product_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            extras = soup.find('div', attrs={'class': 'a-section', 'id': 'prodDetails'}).div.find('div', {'class': 'a-expander-content a-expander-section-content a-section-expander-inner'})

            additional_data = []
            try:                
                max_res = extras.find('th', string=re.compile('Max Screen Resolution')).find_next_sibling().text.replace('\u200e', '').strip() # Max screen resolution
            except AttributeError:
                max_res = 'N/A'
            try:                
                mem_speed = extras.find('th', string=re.compile('Memory Speed')).find_next_sibling().text.replace('\u200e', '').strip() # Memory speed
            except AttributeError:
                mem_speed = 'N/A'
            try:
                graphics = extras.find('th', string=re.compile('Graphics Coprocessor')).find_next_sibling().text.replace('\u200e', '').strip() # Graphics coprocessor
            except AttributeError:
                graphics = 'N/A'
            try:
                brand = extras.find('th', string=re.compile('Chipset Brand')).find_next_sibling().text.replace('\u200e', '').strip() # Brand
            except AttributeError:
                brand = 'N/A'
            try:
                vram = extras.find('th', string=re.compile('Graphics Card Ram Size')).find_next_sibling().text.replace('\u200e', '').strip() # VRAM
            except AttributeError:
                vram = 'N/A'
            additional_data.append([max_res, mem_speed, graphics, brand, vram])
            items.append([product_name, rating, rating_count, price, product_url, additional_data[0][0], additional_data[0][1], additional_data[0][2], additional_data[0][3], additional_data[0][4]])
        except AttributeError:
            continue
        sleep(1)
    sleep(1)
    
df = pd.DataFrame(items, columns=['product', 'rating', 'rating count', 'price', 'product url', 'max screen resolution', 'memory speed', 'graphics coprocessor', 'brand', 'vram'])
df.to_csv('C://Users//caoda//Desktop//coding//py-web-scraper//{0}.csv'.format(search_query), index=False)

