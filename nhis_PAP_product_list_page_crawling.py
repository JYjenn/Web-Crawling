import pandas as pd
import datetime
from time import sleep
from utils import *


# 업소별 제품 개수 확인
def product_total_num(web_driver, company_num):

    # 업소명 클릭 --> 검색버튼 클릭
    web_driver.find_element_by_xpath('//*[@id="jeJoSa"]/option[' + str(company_num) + ']').click()
    web_driver.find_element_by_xpath('//*[@id="adaWbmkbVO"]/div[2]/button[1]').click()
    sleep(1.5)

    # 첫번째 페이지 소스 확인
    first_page_soup, first_page_tr = PageSource(web_driver)

    # 첫페이지 상품 개수
    product_counts = len(first_page_tr)
    # 페이지 정보 및 개수
    page_info = first_page_soup.select('div.pagination > div > div')
    paging = first_page_soup.select('div.pagination > div > div > a')
    page_counts = len(paging)

    # case 1. None 또는 상품 1개
    if product_counts == 1:
        if first_page_tr[0].text == '\n검색된 자료가 없습니다.\n':
            product_counts = 0
        else:
            product_counts = 1

    # case 2. 상품 2개 ~ 10개 미만
    elif (product_counts > 1) and (product_counts < 10):
        product_counts = product_counts

    # case 3. 상품 딱 10개 (페이지 수 1개)
    elif (product_counts == 10) and (page_counts == 0):
        product_counts = 10

    # case 4. 상품 10개 이상 (페이지 수 1개 이상)
    else:
        # %% case 4-1. 페이지 수 10개 이하
        if (page_counts > 0) and (page_counts <= 9) and (page_info[0].nextSibling == '\n'):
            web_driver.find_element_by_xpath('//*[@id="adaWbmkbVO"]/div[5]/div/div/a[' + str(page_counts) + ']').click()

            last_page_soup, last_page_tr = PageSource(web_driver)
            product_counts = 10 * page_counts + len(last_page_tr)

        # %% case 4-2. 페이지 수 10개 초과
        elif (page_counts == 9) and (page_info[0].nextSibling != '\n'):
            # 마지막 페이지로 이동 (<<)
            web_driver.find_element_by_xpath('//*[@id="adaWbmkbVO"]/div[5]/div/a[4]').click()

            last_page_soup, last_page_tr = PageSource(web_driver)
            last_page_1st_product_num = int(last_page_tr[0].text.split('\n')[1])
            last_page_num = int(last_page_1st_product_num / 10) + 1

            product_counts = 10 * (last_page_num - 1) + len(last_page_tr)

    return product_counts


# 업소명 & 상품개수 --> csv 저장
def company_with_product_counts(web_driver, company_name_list):
    num_list = []

    for idx, tmp_company in enumerate(company_name_list):
        print(tmp_company)
        num_list.append([tmp_company, product_total_num(web_driver, int(idx+2))])

    result_df = pd.DataFrame(num_list)

    now = datetime.datetime.now()
    now_date = now.strftime('%Y-%m-%d')
    result_df.columns = ['회사명 & 등록개수', now_date]

    # csv 파일로 저장
    result_df.to_csv('result.csv', encoding='ms949', index=False)

    return result_df


if __name__ == '__main__':

    try:
        # 홈페이지 접속
        url = 'https://www.nhis.or.kr/nhis/policy/retrievePAPPrdList.do'
        driver = Chrome_open(url)
        # 업소명 리스트
        company_list = CompanyName_list(driver)
        # web crawling 작업
        result_file = company_with_product_counts(driver, company_list)

    except Exception as e:
        print("에러발생: ", e)
