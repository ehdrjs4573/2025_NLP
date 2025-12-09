# selfintro_app/scripts/fetch_job_details.py
import requests
import json
import time
from pathlib import Path

API_KEY = "0fcfa4210e7fd4b7685e2b403f859ab7"
DETAIL_URL = "https://www.career.go.kr/cnet/front/openapi/job.json"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

JOB_LIST_PATH = DATA_DIR / "career_job_list.json"
OUTPUT_PATH = DATA_DIR / "career_job_details.json"

def load_jobcd_list():
    """목록 파일에서 job_cd만 추출"""
    with open(JOB_LIST_PATH, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    job_cds = sorted({ j["job_cd"] for j in jobs })
    print(f"job_cd {len(job_cds)}개 발견")
    return job_cds


def fetch_details():
    job_cds = load_jobcd_list()
    results = []

    for idx, job_cd in enumerate(job_cds, start=1):

        params = {"apiKey": API_KEY, "seq": job_cd}

        res = requests.get(DETAIL_URL, params=params)
        data = res.json()

        if not data.get("baseInfo"):
            print(f"[{idx}/{len(job_cds)}] job_cd={job_cd} baseInfo 없음 → 스킵")
            continue

        results.append(data)

        if idx % 20 == 0:
            print(f"✔ {idx}개 처리 (누적 {len(results)}개)")

        time.sleep(0.25)

    print(f"\n최종 수집: {len(results)}개")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"저장 완료 → {OUTPUT_PATH}")


if __name__ == "__main__":
    fetch_details()