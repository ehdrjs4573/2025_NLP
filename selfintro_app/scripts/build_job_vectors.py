# selfintro_app/scripts/build_job_vectors.py
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

JOB_LIST_PATH = DATA_DIR / "career_job_list.json"
JOB_DETAIL_PATH = DATA_DIR / "career_job_details.json"
OUTPUT_PATH = DATA_DIR / "career_job_vectors.json"


def load_job_list():
    """career_job_list.json에서 job_cd → top_nm, aptit_name 매핑 생성"""
    with open(JOB_LIST_PATH, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    mapping = {}
    for j in jobs:
        job_cd = j.get("job_cd")
        if job_cd is None:
            continue
        mapping[job_cd] = {
            "top_nm": j.get("top_nm"),
            "aptit_name": j.get("aptit_name"),
            "job_nm_from_list": j.get("job_nm"),
        }
    print(f" 목록 기준 직업 수: {len(mapping)}개")
    return mapping


def build_vectors():
    job_meta = load_job_list()

    with open(JOB_DETAIL_PATH, "r", encoding="utf-8") as f:
        details = json.load(f)

    results = []

    for idx, item in enumerate(details, start=1):
        base = item.get("baseInfo") or {}
        job_cd = base.get("job_cd")
        job_nm = (base.get("job_nm") or "").strip()

        if job_cd is None:
            print(f"[{idx}] job_cd 없음 → 스킵")
            continue

        meta = job_meta.get(job_cd, {})
        top_nm = meta.get("top_nm")
        aptit_name = meta.get("aptit_name") or base.get("aptit_name")

        # 1) work summary
        work_list = item.get("workList") or []
        work_texts = [
            (w.get("work") or "").strip()
            for w in work_list
            if w.get("work")
        ]
        work_summary = " ".join(work_texts)

        # 2) core abilities
        ability_list = item.get("abilityList") or []
        main_abilities = sorted({
            (a.get("ability_name") or "").strip()
            for a in ability_list
            if a.get("ability_name")
        })

        # 3) skills
        perform_list = (item.get("performList") or {}).get("perform") or []
        skills = sorted({
        (p.get("perform") or "").strip()
        for p in perform_list
        if isinstance(p, dict) and p.get("perform")
        })

        # 4) knowledge
        knowledge_list = (item.get("performList") or {}).get("knowledge") or []
        knowledge = sorted({
        (k.get("knowledge") or "").strip()
        for k in knowledge_list
        if isinstance(k, dict) and k.get("knowledge")
        })

        # 5) interests
        interest_list = item.get("interestList") or []
        interests = [
            (i.get("interest") or "").strip()
            for i in interest_list
            if i.get("interest")
        ]

        result_item = {
            "job_cd": job_cd,
            "job_nm": job_nm,
            "top_nm": top_nm,
            "aptit_name": aptit_name,
            "work_summary": work_summary,
            "main_abilities": main_abilities,
            "skills": skills,
            "knowledge": knowledge,
            "interests": interests,
        }

        results.append(result_item)

    print(f" 변환 완료 : 직무 벡터 {len(results)}개 생성")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f" 저장 완료 → {OUTPUT_PATH}")


if __name__ == "__main__":
    build_vectors()