import requests
import json
import time

API_KEY = "0fcfa4210e7fd4b7685e2b403f859ab7"
BASE_URL = "https://www.career.go.kr/cnet/front/openapi/jobs.json"

def fetch_all_jobs():
    print("📌 직업백과 전체 목록 가져오는 중...")

    page = 1
    results = []

    while True:
        params = {
            "apiKey": API_KEY,
            "pageIndex": page
        }

        res = requests.get(BASE_URL, params=params)
        data = res.json()

        jobs = data.get("jobs", [])
        count = data.get("count", 0)

        if not jobs:
            break

        results.extend(jobs)

        print(f"➡ {page} 페이지 수집 완료 ({len(jobs)}개)")

        if len(results) >= count:
            break

        page += 1
        time.sleep(0.2)

    print(f"\n✔ 총 {len(results)}개 직업 데이터 수집 완료")

    # 결과 저장
    with open("career_job_list.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("📁 career_job_list.json 저장 완료")


if __name__ == "__main__":
    fetch_all_jobs()