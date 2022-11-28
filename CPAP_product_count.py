import os
import datetime
import random
import pandas as pd
from tqdm import tqdm
from time import sleep
from utils import *
from selenium.webdriver.support.ui import Select


def select_company(web_driver, company_name):
    # 등록업소 -> 제조사 선택 -> 검색버튼
    select = Select(web_driver.find_element_by_id('jeJoSa'))
    select.select_by_visible_text(company_name)
    web_driver.find_element_by_xpath('//*[@id="adaWbmkbVO"]/div[2]/button[1]').click()
    web_driver.implicitly_wait(10)


def make_company_product_info_db(html_table_rows):
    tr_header = html_table_rows[0].findAll('th')
    column_name = [tr_header[1].text, tr_header[2].text, tr_header[3].text]
    ## td -> db 데이터프레임화
    info_db = []
    for tmp_row in html_table_rows[1:]:
        tr_data = tmp_row.findAll('td')
        prod_info = {
            column_name[0]: tr_data[1].text,
            column_name[1]: tr_data[2].text,
            column_name[2]: tr_data[3].text
        }
        info_db.append(prod_info)

    return info_db


def page_count(web_driver):
    pagination = web_driver.find_element_by_css_selector('#adaWbmkbVO > div.pagination > div > div')
    pagination_text = pagination.text
    pagination_count = len(pagination_text.split('\n'))
    
    return pagination_count


def page_source(web_driver):
    page_html = web_driver.page_source
    page_soup = BeautifulSoup(page_html, 'html.parser')

    return page_html, page_soup


def find_table_rows(page_soup):
    page_table = page_soup.find('table')
    page_tr = page_table.findAll('tr')
    return page_tr


def page_crawling(web_driver, html_table_rows):
    current_page_count = page_count(web_driver)
    page_db = make_company_product_info_db(html_table_rows)  # 첫번째 화면은 strong 으로 고정되어 있음

    for tmp_page in tqdm(range(2, current_page_count + 1)):  # 두번째 페이지부터 for 루프
        tmp_selector = '#adaWbmkbVO > div.pagination > div > div > a:nth-child(' + str(tmp_page) + ')'
        web_driver.find_element_by_css_selector(tmp_selector).click()
        web_driver.implicitly_wait(10)

        tmp_html, tmp_soup = page_source(web_driver)
        tmp_tr = find_table_rows(tmp_soup)
        tmp_db = make_company_product_info_db(tmp_tr)
        page_db.extend(tmp_db)
        sleep(random.uniform(1.0, 2.5))
        
    return page_db


if __name__ == '__main__':
    try:
        # url 접속
        url = 'https://www.nhis.or.kr/nhis/policy/retrievePAPPrdList.do'
        driver = Chrome_open(url)
        # 모든 제조사 이름 리스트
        company_names = CompanyName_list(driver)
        # 제조사별 작업 진행
        all_company_db = []
        for tmp_name in company_names:
            print("제조사명: ", tmp_name)
            # 해당 업소 클릭 -> 페이지 정보추출
            select_company(driver, tmp_name)
            html, soup = page_source(driver)
            # 테이블 -> tr, th, td 정보 & 행길이
            table_rows = find_table_rows(soup)
            rows_length = len(table_rows)
            print('Rows Length: ', rows_length)
            # 행길이에 따라 작업 진행
            if rows_length == 2:
                empty_or_not_info = table_rows[1].text.split('\n')[1]
                if empty_or_not_info == '1':  # 1-(1). 제품 개수가 1개인 경우
                    product_db = make_company_product_info_db(table_rows)
                    all_company_db.append(product_db)
                else:  # 1-(2). 제품 개수가 0개인 경우
                    continue
            elif (rows_length > 2) & (rows_length < 11):
                ## 2. 제품이 10개 미만인 경우
                product_db = make_company_product_info_db(table_rows)
                all_company_db.append(product_db)

            elif rows_length == 11:
                ## 3. 제품이 10개 이상인 경우 --> 3-(1): 100개 이하인 경우, 3-(2): 100개 초과인 경우
                ## 맨 처음 화면에서 '마지막페이지' 유무 확인
                existing_last = soup.find('a', attrs={"class": "last"})
                ## 처음 1 ~ 10(이하) 페이지 크롤링
                first_page_db = page_crawling(driver, table_rows)
                ## 3-(1). 100개 이하 --> '마지막페이지' 등 화살표 모양의 페이지 이동 아이콘이 없음
                if existing_last is None:
                    all_company_db.append(first_page_db)
                ## 3-(2). 100개 초과
                elif existing_last is not None:
                    # 전체 페이지 수 구하기
                    last_page = driver.find_element_by_css_selector('#adaWbmkbVO > div.pagination > div > a.last')
                    last_page_num = int(last_page.get_attribute('onclick').split('(')[1].split(')')[0])
                    # 11 페이지 ~ 크롤링
                    for tmp_next_page in range(int(last_page_num // 10)):
                        # 다음 페이지 클릭
                        driver.find_element_by_css_selector('#adaWbmkbVO > div.pagination > div > a.next').click()
                        driver.implicitly_wait(10)
                        # 페이지 크롤링
                        _, pg_soup = page_source(driver)
                        pg_trs = find_table_rows(pg_soup)
                        tmp_page_db = page_crawling(driver, pg_trs)
                        first_page_db.extend(tmp_page_db)
                    all_company_db.append(first_page_db)

    except Exception as e:
        print(e)
        pass

    all_company = sum(all_company_db, [])
    data_frame = pd.DataFrame(all_company)

    # 저장
    save_path = './PAP_All_JeJoSa_ProductName_list'
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    now = datetime.datetime.now()
    now_date = now.strftime('%Y-%m-%d')
    data_frame.to_csv(os.path.join(save_path, '전체업소_제품정보(' + now_date + ').csv'), encoding='ms949', index=False)
