"""
similarity.py

직무 임베딩 / 기업 임베딩 / 자기소개서 임베딩 간
코사인 유사도를 계산하여 적합도 점수를 산출하는 모듈.
"""

from __future__ import annotations

from typing import Dict, List
import numpy as np


# ---------------------------
# 기본 코사인 유사도
# ---------------------------

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """두 벡터의 코사인 유사도 계산."""
    v1 = np.array(v1, dtype=float)
    v2 = np.array(v2, dtype=float)

    denom = (np.linalg.norm(v1) * np.linalg.norm(v2)) + 1e-8
    if denom == 0:
        return 0.0

    return float(np.dot(v1, v2) / denom)


# ---------------------------
# 점수 변환: (-1~1) → (0~100)
# ---------------------------

def similarity_to_score(sim: float) -> float:
    """코사인 유사도를 0~100 스케일 점수로 변환."""
    score = (sim + 1) / 2 * 100
    return round(score, 2)


# ---------------------------
# 메인 함수: 직무/기업/자소서 적합도 계산
# ---------------------------

def compute_fit_scores(
    job_vector: np.ndarray,
    company_vector: np.ndarray,
    essay_vector: np.ndarray
) -> Dict[str, float]:
    """직무·기업·자소서 벡터로 적합도 계산"""

    job_sim = cosine_similarity(job_vector, essay_vector)
    company_sim = cosine_similarity(company_vector, essay_vector)
    job_company_sim = cosine_similarity(job_vector, company_vector)

    return {
        "job_fit": similarity_to_score(job_sim),
        "company_fit": similarity_to_score(company_sim),
        "job_company_alignment": similarity_to_score(job_company_sim),
        "raw": {
            "job_sim": job_sim,
            "company_sim": company_sim,
            "job_company_sim": job_company_sim
        }
    }


# ---------------------------
# 문장별 유사도 계산
# ---------------------------

def compute_sentence_level_similarity(
    job_vector: np.ndarray,
    company_vector: np.ndarray,
    sentence_embeddings: np.ndarray
) -> Dict[str, List[float]]:
    """각 문장별 직무/기업 유사도 계산"""
    job_sims = []
    comp_sims = []

    for vec in sentence_embeddings:
        job_sims.append(cosine_similarity(job_vector, vec))
        comp_sims.append(cosine_similarity(company_vector, vec))

    return {
        "job_sims": job_sims,
        "company_sims": comp_sims
    }


# ---------------------------
# 테스트
# ---------------------------

if __name__ == "__main__":
    v_job = np.random.rand(768)
    v_company = np.random.rand(768)
    v_essay = np.random.rand(768)

    print(compute_fit_scores(v_job, v_company, v_essay))