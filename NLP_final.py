import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


# -------------------------
# 1) User-Agent 생성
# -------------------------
ua = UserAgent()
HEADERS = {
    "User-Agent": ua.random,
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}


# -------------------------
# 2) 검색 함수
# -------------------------
def search_cover_letters(company: str, job: str, max_results=10):
    """
    회사명 + 직무명으로 링커리어 자소서를 검색하고,
    상세 URL 리스트를 반환한다.
    """
    query = f"{company} {job}"
    url = f"https://linkareer.com/cover-letter/search?query={query}"

    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print("❌ 검색 페이지 요청 실패:", r.status_code)
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    result_cards = soup.select("a.cover-letter-card")
    results = []

    for card in result_cards[:max_results]:
        title = card.select_one(".title").text.strip() if card.select_one(".title") else "제목 없음"
        link = card.get("href")

        # 절대경로로 변환
        full_url = "https://linkareer.com" + link

        results.append({
            "title": title,
            "url": full_url
        })

    return results


# -------------------------
# 3) 상세 페이지 크롤링
# -------------------------
def get_cover_letter_text(url: str):
    """
    상세 페이지에서 문항 + 답변 텍스트를 모두 가져와
    하나의 문자열로 반환한다.
    """
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print("❌ 상세 페이지 요청 실패:", r.status_code)
        return ""

    soup = BeautifulSoup(r.text, "html.parser")

    # 자소서 문항 & 답변 영역
    qa_blocks = soup.select(".question-item")

    paragraphs = []

    for block in qa_blocks:
        question_el = block.select_one(".question-text")
        answer_el = block.select_one(".answer-text")

        question = question_el.text.strip() if question_el else ""
        answer = answer_el.text.strip() if answer_el else ""

        if question:
            paragraphs.append(f"[문항] {question}")
        if answer:
            paragraphs.append(f"[답변] {answer}")

    return "\n\n".join(paragraphs)


# -------------------------
# 4) 통합 크롤링 함수
# -------------------------
def crawl_linkareer(company: str, job: str, limit=5):
    """
    회사명, 직무명으로 검색 → N개 자소서를 상세 크롤링해서
    리스트 형태로 반환한다.
    """
    results = search_cover_letters(company, job, max_results=limit)

    cover_letters = []
    for item in results:
        print(f"📘 크롤링 중: {item['title']}")
        text = get_cover_letter_text(item["url"])

        cover_letters.append({
            "title": item["title"],
            "url": item["url"],
            "text": text
        })

    return cover_letters



# -------------------------
# 테스트 실행
# -------------------------
if __name__ == "__main__":
    company = "한국전력공사"
    job = "전산직"

    data = crawl_linkareer(company, job, limit=3)

    print("\n===== 크롤링 결과 =====\n")
    for idx, item in enumerate(data, 1):
        print(f"🎯 {idx}. {item['title']}")
        print(item["url"])
        print(item["text"][:300], "...\n")  # 앞부분만 출력