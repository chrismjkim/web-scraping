# web-scraping
Selenium Webdriver를 이용해 재사용성 높도록 scraping에 필요한 코드만 정리했습니다.
단, 웹사이트마다 static file이나 url의 구조 등이 다르므로 html 분석 후 약간의 customization이 필요합니다.

# 사용 방법(예제)
새 폴더를 생성해서 crawl.py를 다운로드받아 사용 가능합니다.
Web Crawwling의 위키피디아 문서를 예시로 스크래핑합니다(https://en.wikipedia.org/wiki/Web_crawler)
## URL 작성
탐색할 URL을 URL 변수에 작성합니다.
```URL = "https://en.wikipedia.org/wiki/Web_crawler"```
## fetch_html()
패러미터에 URL을 넣으면 html의 문자열을 반환받습니다. 이후 다른 함수들은 해당 문자열을 param으로 받고 처리합니다.
## save_html()
html 문자열을 BeautifulSoup 객체로 변환한 뒤, .txt 파일로 변환합니다.
to_html=True 로 설정하면 .txt 파일 대신 .html 파일로 변환 가능합니다.
prettify=True로 설정하면 들여쓰기가 적용된 문서로 바뀝니다.
## get_image_urls()
페이지에 있는 이미지들의 url을 리스트로 반환합니다.
img 태그의 src를 확인한 후 리스트에 저장합니다.
## get_links()
펭이지에 있는 모든 a 태그의 href를 확인해서 링크를 리스트로 반환합니다.
set()을 list()로 변환하는 과정이 있으므로, 중복되는 링크가 포함되지 않습니다.
## save_images()
list 요소를 받고 이미지를 저장합니다. 기본적으로 이미지의 원본 이름으로 저장되며, kwarg로 쉽게 custom 가능합니다.
