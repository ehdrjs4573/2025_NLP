# selfintro_app/scripts/fetch_career_job_details.py

import requests
import json
import time

API_KEY = "0fcfa4210e7fd4b7685e2b403f859ab7"
DETAIL_URL = "https://www.career.go.kr/cnet/front/openapi/job.json"


def load_jobcd_list():
    """목록 파일에서 job_cd만 추출"""
    with open("career_job_list.json", "r", encoding="utf-8") as f:
        jobs = json.load(f)

    job_cds = sorted({ j["job_cd"] for j in jobs if "job_cd" in j })
    print(f"📌 job_cd {len(job_cds)}개 발견")
    return job_cds


def fetch_details():
    job_cds = load_jobcd_list()
    results = []

    for idx, job_cd in enumerate(job_cds, start=1):

        params = {
            "apiKey": API_KEY,
            "seq": job_cd,  # 상세조회는 job_cd가 seq가 됨
        }

        try:
            res = requests.get(DETAIL_URL, params=params, timeout=10)
        except Exception as e:
            print(f"[{idx}/{len(job_cds)}] job_cd={job_cd} 요청 에러: {e}")
            continue

        if res.status_code != 200:
            print(f"[{idx}/{len(job_cds)}] job_cd={job_cd} HTTP {res.status_code}")
            continue

        try:
            data = res.json()
        except Exception as e:
            print(f"[{idx}/{len(job_cds)}] job_cd={job_cd} JSON 파싱 에러: {e}")
            print(res.text[:200])
            continue

        # baseInfo가 없거나 null이면 스킵
        if not data.get("baseInfo"):
            print(f"[{idx}/{len(job_cds)}] job_cd={job_cd} baseInfo 없음, 스킵")
            continue

        results.append(data)

        if idx % 20 == 0:
            print(f"✔ {idx}개 처리 (누적 {len(results)}개 유효)")

        time.sleep(0.25)  # API 차단 방지용


    print(f"\n✅ 최종 유효 상세 데이터 개수: {len(results)}개")

    with open("career_job_details.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("📁 career_job_details.json 저장 완료")


if __name__ == "__main__":
    fetch_details()