"""
similarity.py

직무 임베딩 / 기업 임베딩 / 자기소개서 임베딩 간
코사인 유사도를 계산하고,
anchor 기반 calibration을 통해 적합도 점수를 산출한다.
"""

from __future__ import annotations
from typing import Dict, List
import numpy as np


# -----------------------------
# 기본 코사인 유사도
# -----------------------------
def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    v1 = np.array(v1, dtype=float)
    v2 = np.array(v2, dtype=float)

    denom = (np.linalg.norm(v1) * np.linalg.norm(v2)) + 1e-8
    if denom == 0:
        return 0.0

    return float(np.dot(v1, v2) / denom)


# -----------------------------
# Anchor 기반 calibration
# -----------------------------
def calibrate_similarity(
    sim: float,
    low: float,
    mid: float,
    high: float
) -> float:
    """
    좁은 코사인 유사도 분포를 0~100 점수로 보정
    """

    if sim <= low:
        score = 30 * (sim / low) if low != 0 else 30
    elif sim <= mid:
        score = 30 + (sim - low) / (mid - low) * 20
    elif sim <= high:
        score = 50 + (sim - mid) / (high - mid) * 30
    else:
        score = 80 + min((sim - high) * 100, 20)

    return round(float(np.clip(score, 0, 100)), 2)


# -----------------------------
# 메인 함수
# -----------------------------
def compute_fit_scores(
    job_vector: np.ndarray,
    company_vector: np.ndarray,
    essay_vector: np.ndarray
) -> Dict[str, float]:
    """
    직무·기업·자소서 적합도 계산 (calibration 적용)
    """

    # raw similarity
    job_sim = cosine_similarity(job_vector, essay_vector)
    company_sim = cosine_similarity(company_vector, essay_vector)
    job_company_sim = cosine_similarity(job_vector, company_vector)

    # 🔥 공통 anchor (지금 데이터 분포 기준)
    ANCHOR = {
        "low": -0.08,
        "mid": 0.02,
        "high": 0.12
    }

    return {
        "job_fit": calibrate_similarity(job_sim, **ANCHOR),
        "company_fit": calibrate_similarity(company_sim, **ANCHOR),
        "job_company_alignment": calibrate_similarity(job_company_sim, **ANCHOR),
        "raw": {
            "job_sim": round(job_sim, 4),
            "company_sim": round(company_sim, 4),
            "job_company_sim": round(job_company_sim, 4)
        }
    }


# -----------------------------
# 문장 단위 유사도 (그대로 유지)
# -----------------------------
def compute_sentence_level_similarity(
    job_vector: np.ndarray,
    company_vector: np.ndarray,
    sentence_embeddings: np.ndarray
) -> Dict[str, List[float]]:

    job_sims = []
    comp_sims = []

    for vec in sentence_embeddings:
        job_sims.append(cosine_similarity(job_vector, vec))
        comp_sims.append(cosine_similarity(company_vector, vec))

    return {
        "job_sims": job_sims,
        "company_sims": comp_sims
    }


# -----------------------------
# 테스트
# -----------------------------
if __name__ == "__main__":
    v_job = np.random.rand(768)
    v_company = np.random.rand(768)
    v_essay = np.random.rand(768)

    print(compute_fit_scores(v_job, v_company, v_essay))