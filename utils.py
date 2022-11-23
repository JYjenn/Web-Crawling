from bs4 import BeautifulSoup
# from urllib import parse
# from urllib.request import urlopen
from selenium import webdriver
import requests


# 창 뜨는 모드로 URL 열기
def Chrome_open(url):
    try:
        driver = webdriver.Chrome('C:\\Chromedriver\\chromedriver.exe')
        driver.implicitly_wait(10)
        driver.get(url)
    except (Exception, Warning) as e:
        driver = 0
        print(e)
        print("Chrome driver version check!")

    return driver


# 창 안뜨는 모드
def HeadlessChrome_open(url):

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument('disable-gpu')

    driver = webdriver.Chrome('C:\Chromedriver\chromedriver.exe', chrome_options=options)
    driver.implicitly_wait(10)

    driver.get(url)

    return driver


# webdriver --> html 구조 데이터 (soup) --> 업소명 리스트
def CompanyName_list(webdriver):

    soup, tr = PageSource(webdriver)
    option_list = soup.select('option')

    company_list = []
    for i in range(5, len(option_list)):
        company_list.append(option_list[i].text)

    return company_list


# requests 모듈 이용하여 html 얻기
def get_html(url):
    _html = ""
    resp = requests.get(url)
    if resp.status_code == 200:
        _html = resp.text

    return _html


# 페이지 이동 후 page source(soup) --> 상품 개수(tr)
def PageSource(web_driver):
    html = web_driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    tr = soup.select('div > table > tbody > tr')

    return soup, tr
