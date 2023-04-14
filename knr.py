from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import random
import os
from multiprocessing.dummy import Pool as ThreadPool
import requests

data_dir = f'С:\\Akari Bot\\seleniumData'
workdir = 'Q:/ЭМШ/ЭМШ-2022/КНР/Работы Raw'
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('==profile-directory=Default')
chrome_options.add_argument(f'==user-data-dir={data_dir}')
dcap = dict(DesiredCapabilities.CHROME)
chrome = webdriver.Remote(command_executor='http://127.0.0.1:9515', desired_capabilities=dcap, options=chrome_options)

script = "arguments[0].style.opacity=1; arguments[0].style['transform']='translate(0px, 0px) scale(1)';arguments[0].style['MozTransform']='translate(0px, 0px) scale(1)'; arguments[0].style['WebkitTransform']='translate(0px, 0px) scale(1)'; arguments[0].style['msTransform']='translate(0px, 0px) scale(1)'; arguments[0].style['OTransform']='translate(0px, 0px) scale(1)'; return true;"
chrome.get('https://suip.biz/ru/?act=file-metadata-cleaner')
works = os.listdir(workdir)
for i in works:
    upload_button = chrome.find_element(By.CSS_SELECTOR, "input[type=file]")
    chrome.execute_script(script, upload_button)
    upload_button.send_keys(workdir + '/' + i)
    # chrome.find_element(By.CSS_SELECTOR, 'Submit1').click()





