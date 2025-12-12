"""
keyword_coverage.py

SBERT 기반 의미 매칭으로
직무 핵심 키워드(Skills / Knowledge / Abilities)가
자기소개서 문장에 얼마나 반영되었는지 분석하는 모듈.
"""

from __future__ import annotations
from typing import Dict, List
import re
import numpy as np

from nlp.embedding import embed_sentences
from nlp.preprocessing import preprocess
from nlp.loaders import load_raw_job_vectors
from nlp.similarity import cosine_similarity


# ==============================
# 설정
# ==============================
SIM_THRESHOLD = 0.35  # 🔥 널널한 의미 매칭 기준


# ==============================
# 직무 키워드 수집
# ==============================
def collect_job_keywords_by_group(job_info: Dict) -> Dict[str, List[str]]:
    """
    직무 정보를 Skills / Knowledge / Abilities 그룹으로 분리
    """
    groups = {
        "skills": [],
        "knowledge": [],
        "main_abilities": []
    }

    field_map = {
        "skills": "skills",
        "knowledge": "knowledge",
        "main_abilities": "main_abilities"
    }

    for group, field in field_map.items():
        items = job_info.get(field, [])
        for item in items:
            # '고장의 발견·수리' 같은 복합어 분리
            parts = re.split(r"[·,()/ ]+", item)
            groups[group].extend([p.strip() for p in parts if len(p.strip()) > 1])

    # 중복 제거
    for k in groups:
        groups[k] = list(set(groups[k]))

    return groups


# ==============================
# 의미 기반 키워드 매칭
# ==============================
def semantic_keyword_match(
    keywords: List[str],
    sentences: List[str],
    sentence_embeddings: np.ndarray
) -> Dict:

    if not keywords or not sentences:
        return {
            "matched": {},
            "missing": keywords,
            "coverage_score": 0.0
        }

    keyword_embeddings = embed_sentences(keywords)

    matched = {}
    missing = []

    for idx, kw_vec in enumerate(keyword_embeddings):
        max_sim = 0.0
        max_idx = -1

        # 🔥 여기서 for로 문장 하나씩 비교
        for sent_idx, sent_vec in enumerate(sentence_embeddings):
            sim = cosine_similarity(kw_vec, sent_vec)
            if sim > max_sim:
                max_sim = sim
                max_idx = sent_idx

        if max_sim >= SIM_THRESHOLD:
            matched[keywords[idx]] = {
                "sentence": sentences[max_idx],
                "similarity": round(float(max_sim), 3)
            }
        else:
            missing.append(keywords[idx])

    coverage = round(len(matched) / len(keywords) * 100, 2) if keywords else 0.0

    return {
        "matched": matched,
        "missing": missing,
        "coverage_score": coverage
    }
# ==============================
# 추천 문장 생성
# ==============================
def generate_recommend_phrases(missing_keywords: List[str]) -> List[str]:
    templates = [
        "{}과(와) 관련된 구체적인 경험을 행동 중심으로 서술해보세요.",
        "{}을(를) 활용해 문제를 해결하거나 판단했던 사례를 추가해보세요.",
        "{} 역량이 드러나는 결과나 성과를 함께 제시하면 좋습니다."
    ]

    recs = []
    for kw in missing_keywords[:5]:
        for t in templates:
            recs.append(t.format(kw))

    return recs


# ==============================
# 메인 분석 함수
# ==============================
def analyze_keyword_coverage(job_id: int, essay_text: str) -> Dict:
    """
    report_builder에서 호출되는 메인 함수
    """
    # 직무 정보 로드
    raw_jobs = load_raw_job_vectors()
    job_info = raw_jobs.get(job_id)

    if job_info is None:
        return {}

    # 전처리
    prep = preprocess(essay_text)
    sentences = prep["sentences"]

    if not sentences:
        return {}

    sentence_embeddings = embed_sentences(sentences)

    # 키워드 그룹 수집
    groups = collect_job_keywords_by_group(job_info)

    group_results = {}
    all_matched = {}
    all_missing = []

    for group_name, keywords in groups.items():
        result = semantic_keyword_match(
            keywords,
            sentences,
            sentence_embeddings
        )

        group_results[group_name] = {
            "coverage_score": result["coverage_score"],
            "matched_keywords": result["matched"],
            "missing_keywords": result["missing"]
        }

        all_matched.update(result["matched"])
        all_missing.extend(result["missing"])

    overall_coverage = round(
        sum(g["coverage_score"] for g in group_results.values()) / len(group_results),
        2
    )

    return {
        "coverage_score": overall_coverage,
        "group_coverage": group_results,
        "matched_keywords": list(all_matched.keys()),
        "missing_keywords": list(set(all_missing)),
        "matched_evidence": all_matched,
        "recommended_phrases": generate_recommend_phrases(all_missing)
    }