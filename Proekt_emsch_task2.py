from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from lxml import html
import requests
from bs4 import BeautifulSoup
import time
import random
import sqlite3
import os

#Ввести путь к папке с проектом
project_path = 'C:\\Akari Bot'

#Создание базы данных
DIR = os.path.dirname(__file__)
db = sqlite3.connect(
                os.path.join(DIR, "ege.db"))  # connecting to DB if this file is not there it will create it
SQL = db.cursor()
SQL.execute('CREATE TABLE if not exists tasks('
                        '"num" integer, '
                        '"id" integer, '
                        '"zad" text, '
                        '"av1" text, '
                        '"av2" text, '
                        '"av3" text, '
                        '"av4" text, '
                        '"av5" text, '
                        '"ans" text, '
                        '"act" text, '
                        '"dif" text, '
                        '"tex" text, '
                        '"kod" text)')

#Эмулятор браузера
chrome_options = webdriver.ChromeOptions()
data_dir = f'{project_path}\\seleniumData'
chrome_options.add_argument(f"--user-data-dir={data_dir}")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
dcap = dict(DesiredCapabilities.CHROME)
chrome = webdriver.Remote(command_executor='http://127.0.0.1:9515', desired_capabilities=dcap, options=chrome_options)
chrome.get('https://rus-ege.sdamgia.ru/test?theme=339')

last_height = chrome.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    chrome.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(0.5)

    # Calculate new scroll height and compare with last scroll height
    new_height = chrome.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

r = chrome.page_source
pages = BeautifulSoup(r, 'html.parser')
chrome.quit()
#print (pages.find_all('div', class_='problem_container')[0].prettify())

pages = pages.find_all('div', class_='problem_container')

#Парсинг задания
def task(page):
    global act_TorF
    p = page.find_all('p', class_ = 'left_margin')
    p = [e.text.replace('\xa0', ' ') for e in p]
    a = page.find_all('span')
    a = [e.text for e in a]
    t = page.find_all('i')
    t = [e.text.replace('\xa0', ' ') for e in t]

    zad = p[0]
    tex = t[0]
    num = int(a[0].split("\xa0")[0].split("Задание ")[1])
    id = int(a[0].split("\xa0")[-1])

    act_TorF = False
    for aa in a:
        if aa.startswith('Ответ: '):
            ans = aa.split('Ответ: ')[1]
        elif aa.startswith('Актуальность: '):
            act = aa.split('Актуальность: ')[1]
            act_TorF = True
        elif aa.startswith('Сложность: '):
            dif = aa.split('Сложность: ')[1]
        elif aa.startswith('Раздел кодификатора: '):
            kod = aa.split('Раздел кодификатора: ')[1]
    if act_TorF == True:
    # Задание: zad, Варианты ответа: av, Номер задания в ЕГЭ: num, Ответ: ans, Актуальность: act, Сложность: dif, Тема в кодификаторе: kod, Текст задания: tex
        return {'zad':zad, 'num':num, 'id':id, 'ans':ans, 'act':act, 'dif':dif, 'kod':kod, 'tex':tex}
    else:
        return {'zad': zad, 'num': num, 'id': id, 'ans': ans, 'tex': tex}



#Сохранение в файл
fileid = random.randint(1, 99999)
file = open(f'ege_t2-{fileid}.txt', 'a', encoding='utf-8')

for i,page in enumerate(pages):
    t = task(page)
    file.write(str(i+1)+''+str(t)+'\n')

    #В базу данных
    if act_TorF == True:
        sql_insert = 'INSERT INTO tasks(num, id, zad, ans, act, dif, kod, tex) VALUES (?,?,?,?,?,?,?,?)'
        SQL.execute(sql_insert, (t['num'], t['id'], t['zad'], t['ans'], t['act'], t['dif'], t['kod'], t['tex']))
    else:
        sql_insert = 'INSERT INTO tasks(num, id, zad, ans, tex) VALUES (?,?,?,?,?)'
        SQL.execute(sql_insert, (t['num'], t['id'], t['zad'], t['ans'], t['tex']))
    db.commit()

    #Печать
    print(i+1)
    print(t['id'],t['ans'])

file.close()
db.close()