from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException
import time
import csv
import sys

# 🌟 로그인 URL 재변경 (초기 URL로 돌아가 시도)
LOGIN_URL = "https://www.jobkorea.co.kr/Login/Login" 
SEARCH_URL = "https://www.jobkorea.co.kr/starter/passassay?schTxt={}&tabType=1"

# 👉 여기 네 잡코리아 ID / PW 입력
ID = "ehdrjs4573"
PW = "qwerty4573!"


# ---------------------------------------------
# 1) Selenium Driver 생성 (탐지 우회 옵션)
# ---------------------------------------------
def create_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"❌ WebDriver 생성 실패: {e}")
        sys.exit()


# ---------------------------------------------
# 2) 로그인 기능 (최종 간소화 및 URL 변경)
# ---------------------------------------------
def login(driver):
    driver.get(LOGIN_URL)

    try:
        # 1. ID/PW 입력 요소 대기 및 찾기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "M_ID"))
        )
        
        id_box = driver.find_element(By.ID, "M_ID")
        pw_box = driver.find_element(By.ID, "M_PWD")
        
        # 🌟 로그인 버튼을 ID로 다시 시도 (가장 최신 HTML에서는 CSS Selector였지만, 혹시 모를 경우를 대비)
        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, "button.login-button") 
        except NoSuchElementException:
            # 이전 ID도 시도해봅니다.
            login_btn = driver.find_element(By.ID, "loginsubmit")


        # 2. 입력 및 클릭
        id_box.send_keys(ID)
        pw_box.send_keys(PW)
        login_btn.click()
        
        # 🌟 페이지 전환 대기 (로그인 성공 여부 확인 로직 제거)
        time.sleep(5) 
        
        # 🌟 TimeoutException 회피: 로그인 시도했으면 무조건 성공으로 간주하고 다음 단계로 진행
        return True

    except Exception as e:
        print(f"❌ 로그인 실패: {e.__class__.__name__} - 로그인 입력 요소(M_ID, M_PWD, 버튼)를 찾지 못했습니다.")
        return False


# ---------------------------------------------
# 3) 검색 결과 목록 크롤링
# ---------------------------------------------
def crawl_list(driver, keyword):
    url = SEARCH_URL.format(keyword)
    driver.get(url)
    time.sleep(2) 
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.list-default > ul > li"))
        )
    except:
        print("⚠ 검색 결과 목록 로딩 실패 또는 요소 찾기 실패.")
        return []

    items = driver.find_elements(By.CSS_SELECTOR, "div.list-default > ul > li")
    result = []

    for li in items:
        try:
            detail_link = li.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            company = li.find_element(By.CSS_SELECTOR, ".titTx").text
            
            career = li.find_element(By.CSS_SELECTOR, ".linkArray .career").text if li.find_elements(By.CSS_SELECTOR, ".linkArray .career") else ""
            fields = [f.text for f in li.find_elements(By.CSS_SELECTOR, ".linkArray .field")]
            question = li.find_element(By.CSS_SELECTOR, ".item.question").text
            answer_preview = li.find_element(By.CSS_SELECTOR, ".item.answer").text

            result.append({
                "company": company,
                "career": career,
                "fields": fields,
                "question": question,
                "short_answer": answer_preview,
                "url": detail_link
            })

        except Exception as e:
            continue

    return result


# ---------------------------------------------
# 4) 상세 자기소개서 텍스트 크롤링 (팝업 닫기 로직 유지)
# ---------------------------------------------
def crawl_detail(driver, url):
    driver.get(url)
    time.sleep(3) 

    # 1. 로그인 팝업이 뜨는지 확인하고 닫기 (.devLyBtnClose)
    try:
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".devLyBtnClose"))
        )
        print("    [팝업 감지] 로그인 팝업창 닫기 시도...")
        close_button.click()
        time.sleep(1) 
        
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".popupModal.popupLogin"))
        )

    except TimeoutException:
        pass
    except Exception as e:
        print(f"❌ 팝업 닫기 중 오류: {e.__class__.__name__}")
        
    # 2. 상세 자소서 텍스트 크롤링
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.tx"))
        )

        blocks = driver.find_elements(By.CSS_SELECTOR, "div.tx")
        txt = "\n".join([b.text for b in blocks])
        return txt.strip()
    except:
        return ""


# ---------------------------------------------
# 5) 메인 실행부
# ---------------------------------------------
def main():
    driver = create_driver()

    print("🔵 로그인 시도 중...")
    
    if login(driver):
        print("✔ 로그인 완료 (성공으로 간주)\n")
    else:
        # 로그인 요소 찾기 실패 시 (NoSuchElementException, TimeoutException 등)
        print("❌ 로그인 입력 단계에서 실패하여 크롤링을 진행할 수 없습니다.")
        driver.quit()
        return

    keyword = input("🔎 검색할 기업명 또는 직무를 입력하세요 (예: 삼성전자): ")
    if not keyword:
        keyword = "삼성전자"
        print(f"입력된 키워드가 없어 기본값 '{keyword}'로 검색합니다.")
        
    print(f"🔍 '{keyword}' 검색 중...\n")

    list_items = crawl_list(driver, keyword) 
    print(f"📌 수집된 자소서 개수: {len(list_items)}\n")
    
    if not list_items:
        # 만약 로그인 시도는 성공으로 간주했으나, 실제 로그인이 실패했다면 여기서 0개가 나옵니다.
        print("⛔ 수집할 항목이 없거나, 실제 로그인이 실패하여 목록을 가져오지 못했습니다. 종료합니다.")
        driver.quit()
        return

    for item in list_items:
        print(f"➡ 상세 수집: {item['company']} / {item['question'][:20]}...")
        full_text = crawl_detail(driver, item["url"])
        item["full_text"] = full_text
        time.sleep(1)

    csv_file_name = f"jobkorea_result_{keyword}.csv"
    with open(csv_file_name, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["회사", "경력", "직무", "질문", "답변 요약", "전체 자소서", "URL"])

        for it in list_items:
            writer.writerow([
                it["company"],
                it["career"],
                ", ".join(it["fields"]),
                it["question"],
                it["short_answer"],
                it["full_text"],
                it["url"]
            ])

    print(f"\n🎉 모든 작업 완료! {csv_file_name} 저장됨")
    driver.quit()


if __name__ == "__main__":
    main()