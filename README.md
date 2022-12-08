# Web-Crawling
### Crawling with using BeautifulSoup and Selenium
- 2022-11-22 시작! 😊
---
### 무엇을 Crawling 하는가?
- 국민건강보험 홈페이지 중 '양압기 등록제품' [페이지](https://www.nhis.or.kr/nhis/policy/retrievePAPPrdList.do)
- 등록업소별 제품종류/제품명 리스트 추출
<img width="80%" src="https://user-images.githubusercontent.com/118783464/204682722-e06926ec-69fc-42d6-a1b9-b830f4af9bc8.png"/>
<br>

### 왜 하는가?
- 해당 리스트를 추출하여 매주 csv파일을 생성(raw data)
<img width="40%" src="https://user-images.githubusercontent.com/118783464/204684983-831801ba-5591-4716-83a9-d80b59e652a2.png"/>

- raw data 활용하여 양압기의 지역별 증가율 및 제조사별 점유율 등의 현황 파악
- 제품등록이 꾸준히 증가(또는 유지) 되는 제조사들을 파악 ✨
- 이를 바탕으로 해당 제조사들과 컨택을 통해 비즈니스 관계 형성 🙌
- 또한, 업계 흐름과 관련 시장에 대해 원활히 조사할 수 있음 👍
<br>

### 어떻게 하는가?
- 페이지 개발자도구와 BeautifulSoup & Selenium 라이브러리로! :star2:
- nhis_PAP_product_list_page_crawling.py: 각 제조사의 제품 개수
- nhis_PAP_All_product_info_list_crawling.py: 각 제조사의 제품종류 및 제품명 리스트
