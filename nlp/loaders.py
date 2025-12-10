from pathlib import Path
import json
import numpy as np

# NLP_final 프로젝트 루트 기준
BASE_DIR = Path(__file__).resolve().parent.parent

# JSON 데이터 실제 경로
# NLP_final/selfintro_app/scripts/data
DATA_DIR = BASE_DIR / "selfintro_app" / "scripts" / "data"

JOB_EMBED_PATH = DATA_DIR / "career_job_vectors_embed.json"
COMPANY_EMBED_PATH = DATA_DIR / "company_profiles_embed.json"


def load_job_embeddings():
    with open(JOB_EMBED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {item["job_cd"]: item for item in data}


def load_company_embeddings():
    with open(COMPANY_EMBED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {item["company_id"]: item for item in data}


def get_job_vector(job_id: str) -> np.ndarray:
    jobs = load_job_embeddings()
    if job_id not in jobs:
        raise ValueError(f"존재하지 않는 job_id: {job_id}")
    return np.array(jobs[job_id]["embedding"], dtype=float)


def get_company_vector(company_id: str) -> np.ndarray:
    companies = load_company_embeddings()
    if company_id not in companies:
        raise ValueError(f"존재하지 않는 company_id: {company_id}")
    return np.array(companies[company_id]["embedding"], dtype=float)


if __name__ == "__main__":
    print("=== loaders.py test ===")

    jobs = load_job_embeddings()
    companies = load_company_embeddings()

    print(f"직무 개수: {len(jobs)}")
    print(f"기업 개수: {len(companies)}")

    sample_job_id = next(iter(jobs.keys()))
    sample_company_id = next(iter(companies.keys()))

    print("샘플 job_id:", sample_job_id)
    print("샘플 company_id:", sample_company_id)

    job_vec = get_job_vector(sample_job_id)
    company_vec = get_company_vector(sample_company_id)

    print("job_vec shape:", job_vec.shape)
    print("company_vec shape:", company_vec.shape)

    # ----------------------------------------
# RAW 직무 데이터 로딩 (career_job_vectors.json)
# ----------------------------------------
RAW_JOB_VECTORS_PATH = DATA_DIR / "career_job_vectors.json"

def load_raw_job_vectors() -> dict:
    """임베딩 되기 전 RAW 직무 데이터 로드"""
    with open(RAW_JOB_VECTORS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # job_cd → job_info 맵으로 변환
    job_map = {}
    for item in data:
        job_cd = item.get("job_cd")
        if job_cd is not None:
            job_map[int(job_cd)] = item

    return job_map