import os, requests
import time
import re
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://en.wikipedia.org/wiki/" # 이미지 URL과 합칠 기본 URL
URL = "https://en.wikipedia.org/wiki/Web_crawler" # 탐색할 URL
HEADERS = {"User-Agent": "Mozilla/5.0"}

# 크롤링한 이미지 저장 폴더 설정
SAVE_DIR = "images/"
# 최대 로딩 대기 시간
DRIVER_TIMEOUT_SEC = 20

# ===== 크롬 드라이버 옵션 (창 띄우지 않고 실행) =====
opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--proxy-server='direct://'")
opts.add_argument("--proxy-bypass-list=*")
# 인증 관련
opts.add_argument("--ignore-certificate-errors")
opts.set_capability("acceptInsecureCerts", True)
# 안정성 관련
#opts.add_argument("--lang=en-US")
#opts.add_argument("--window-size=1400,1000")
#opts.add_argument("--log-level=3")
driver = webdriver.Chrome(options=opts)  # 자동으로 맞는 드라이버 준비
# WebDriverWait: 동적 로딩을 기다림
wait = WebDriverWait(driver, DRIVER_TIMEOUT_SEC)

# -------------------------------------------------------------------------------------------------------------
def fetch_html(url: str, *args, **kwargs) -> str:
    """
    url을 받고 html 문자열을 반환\n
    select: By 클래스 지정\n select_value: 문자열
    """
    # depth = kwargs.get("depth", 0)
    select = kwargs.get("select", None)
    select_value = kwargs.get("select_value", None)
    
    try:
        driver.get(url)
        """
        페이지 전체가 로드될 때까지 기다림. 
        성능 향상이 필요할 시 Selenium Webdriver의 EC(expceted conditions) 사용할 것
        """
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        if select is None or select_value is None:
            html = driver.page_source
        else: 
            element = driver.find_element(select, select_value)
            html = element.get_attribute("outerHTML")
    except Exception as err:
        print(err)
        html = ""
    return html

# soup.select("table.jquery-tablesorter tbody tr"): 해당 CSS를 가진 html 요소 선택
# 연결된 링크들을 csv 로 저장하는 함수
def get_image_urls(html: str, *args, **kwargs) -> list:
    """html 문자열을 받고 포함된 이미지 url의 리스트 반환"""
    extensions:list = kwargs.get("extensions", ["png", "jpg", "jpeg", "svg", "webp", "gif"])
    
    soup = BeautifulSoup(html, "html.parser")
    img_tags = soup.find_all("img")
    
    img_urls = []
    for img in img_tags:
        img_url = img['src']
        ext = img_url.split(".")[-1]
        if ext in extensions:
            img_urls.append(img_url)
    return img_urls # 리스트로 반환

def get_links(html: str) -> list:
    """html 문자열을 받고 연결된 페이지 링크들의 리스트 반환(BASE_URL과 합침)"""
    soup = BeautifulSoup(html, "html.parser")
    
    a_tags = soup.find_all("a")
    links = set()
    
    for a in a_tags:
        try:
            link = a["href"]
            links.add(link)
        except:
            pass
    links = [urljoin(BASE_URL, l) for l in list(links)]
    return links

def save_html(html: str, *args, **kwargs) -> list:
    """html 문자열을 받고 txt파일로 저장"""
    save_as_html = kwargs.get("to_html", False)
    prettify = kwargs.get("prettify", False)
    filename = kwargs.get("filename", "html")
    if save_as_html:
        filename = filename + ".html"
    else:
        filename = filename + ".txt"
    with open(filename, "w", encoding="utf-8") as f:
        if prettify:
            soup = BeautifulSoup(html, "html.parser")
            f.write(soup.prettify())
        else:
            f.write(html)
    print(f"html saved as {filename}")

def save_text(html: str, *args, **kwargs) -> str:
    "페이지의 모든 텍스트를 문자열로 반환"
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "iframe"]): # 방해되는 태그들
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    text = re.sub(r"\n{2,}", "\n\n", text)
    filename = kwargs.get("filename", "text") + ".txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"text saved as {filename}")

def save_images(urls: list, *args, **kwargs):
    "URL 리스트를 받고 이미지들을 다운로드"
    os.makedirs(SAVE_DIR, exist_ok=True) # 폴더 존재하지 않을 시 생성 보장
    img_n = len(urls)
    for i, url in enumerate(urls):
        name = url.split("/")[-1]
        path = os.path.join(SAVE_DIR, name)
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
        else:
            print(f"{url}: status code not 200")
        print(f"{i} / {img_n} images saved, {i/img_n*100:03f} done")
    return
    


def df_to_csv(dataframe: pd.DataFrame):
    dataframe.to_csv("spriteless_items.csv", index=False, encoding="utf-8-sig")
    
def list_to_csv(list: list, *args, **kwargs):
    filename = kwargs.get("filename", "list") + ".csv"
    df = pd.DataFrame(list)
    df.to_csv(filename, index=True, encoding="utf-8-sig")
    
# -------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    
    # 1. 스크래핑할 웹페이지를 str로 받아옴
    html = fetch_html(URL)
    
    # 2. html을 html/텍스트로 저장
    """주의: to_html=True로 저장 시 syntax를 보장하지 않습니다."""
    save_html(html)
    save_html(html, to_html=True)
    
    # 3. 페이지 내 텍스트만 .txt로 저장
    save_text(html)
    
    # 4. 이미지 url 확인
    urls = get_image_urls(html)
    list_to_csv(urls, filename="url_list")
    
    # 5. CUSTOM: 코드 짜서 직접 url 처리 규칙 만들고 포맷팅하기
    for i in range(len(urls)):
        url:str = urls[i]
        if url.startswith("//upload"):
            urls[i] = urljoin("https:", urls[i])
        else:
            urls[i] = urljoin(BASE_URL, urls[i])
    
    # 6. 이미지 저장
    print(urls)
    save_images(urls)
    
    # 7. 페이지에 연결된 링크
    links = get_links(html)
    
    # 8. 링크 저장
    list_to_csv(links, filename="link_list")