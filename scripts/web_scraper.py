import sys 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time 
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import pandas as pd 
import json 


driver_path = '/usr/lib/chromium-browser/chromedriver'
sys.path.insert(0, driver_path)




# Today date
today = datetime.now()


''' Get the last date in a date list and cast to datetime object'''
def get_last_date(dates:list):
    last_date = dates.pop()
    last_date = list(map(lambda x: int(x), last_date.split(sep='/')))
    last_date_parsed = datetime(year = last_date[-1], day = last_date[0], month=last_date[1])
    return last_date_parsed



''' WebDriver Configuration '''
driver_options = webdriver.ChromeOptions()

driver_options.add_argument('--headless')
driver_options.add_argument('--no-sandbox')
driver_options.add_argument('--disable-dev-shm-usage')


web_browser = webdriver.Chrome('chromedriver', options=driver_options)


web_browser.get('https://elfarodeceuta.es/politica/')

last_height = web_browser.execute_script('return document.body.scrollHeight')
item_count = []


limit_date = datetime(2022, 11, 1)



''' Logic to get news urls '''
dates = [today.strftime('%d/%m/%Y')]
while get_last_date(dates) > limit_date:
    web_browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = web_browser.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break 
    last_height = new_height
    elements = web_browser.find_elements(By.CSS_SELECTOR, ".jeg_postblock_content")
    text_elements = []
    for element in elements:
        title = element.find_element(By.CSS_SELECTOR, ".jeg_post_title")
        date = element.find_element(By.CSS_SELECTOR, ".jeg_meta_date")
        link = title.find_element(By.TAG_NAME, 'a').get_attribute('href')
        text_elements.append(link)
        dates.append(date.text)
    item_count = text_elements


print(item_count)
print(len(item_count))


''' Get Comments from each link if exist'''
final_data = []
fechas = []
for link in item_count:
    new_page = requests.get(link)
    new_soup = BeautifulSoup(new_page.content, 'html.parser')
    title = new_soup.find('h1', class_='jeg_post_title').text 
    date = new_soup.find('div', class_='jeg_meta_date').text
    date = date.split()
    formatted_date = ''.join(date)
    fechas.append(date)
    list_comments = new_soup.find('ol', class_='commentlist')
    if list_comments:
        comments = list_comments.find_all('div', class_='comment-body')
        users_data = []
        for c in comments:
            user = c.find('cite')
            comment = c.find('div', class_='comment-content')
            users_data.append((user.text, comment.text)) 
        comments_data = []
        for user, comment in users_data:
            comments_data.append({"usuario": user, "comentario":comment})
        final_data.append({'fecha': formatted_date, 'titulo': title, 'comentarios': comments_data})
    else:
        final_data.append({'fecha':formatted_date, 'titulo': title, 'comentarios': 'NA'})


file_name = limit_date.strftime('%d%m%Y') + '_' + today.strftime('%d%m%Y') + '.json'

with open(file_name, 'w', encoding='utf-8', newline='') as f:
    json.dump(final_data, f)
