"""
keyword_coverage.py

직무 벡터 내부의 핵심 키워드(knowledge, skills, abilities)를 기반으로
자기소개서 텍스트에 얼마나 포함되어 있는지 분석하는 모듈.

Output:
- coverage_score (%)
- matched_keywords
- missing_keywords
- recommended_phrases (부족한 키워드 기반 자동 추천 문구)
"""

from __future__ import annotations
from typing import List, Dict, Tuple
import re

from konlpy.tag import Okt
okt = Okt()


# ------------------------------
# 텍스트 → 형태소 기반 단어 목록 생성
# ------------------------------
def extract_nouns(text: str) -> List[str]:
    tokens = okt.nouns(text)
    return [t for t in tokens if len(t) > 1]  # 한 글자 제거(의미 적음)


# ------------------------------
# 직무 키워드 묶기
# ------------------------------
def collect_job_keywords(job_info: Dict) -> List[str]:
    """
    career_job_vectors.json 또는 career_job_vectors_embed.json의
    job_info(dict)에서 skills/knowledge/abilities/interest에서 키워드 추출
    """
    keywords = []

    for field in ["skills", "knowledge", "main_abilities", "interests"]:
        if field in job_info and isinstance(job_info[field], list):
            for item in job_info[field]:
                # '고장의 발견·수리'처럼 복합어면 나눔
                parts = re.split(r"[·,. ]+", item)
                keywords.extend([p.strip() for p in parts if p.strip()])

    # 중복 제거
    keywords = list(set(keywords))
    return keywords


# ------------------------------
# 매칭 / 커버리지 계산
# ------------------------------
def compute_keyword_coverage(job_info: Dict, essay_text: str) -> Dict:
    """
    직무 키워드 vs 자기소개서 의미 포함도 분석
    """
    job_keywords = collect_job_keywords(job_info)
    essay_nouns = extract_nouns(essay_text)

    matched = []
    missing = []

    for kw in job_keywords:
        if kw in essay_nouns:
            matched.append(kw)
        else:
            missing.append(kw)

    # coverage score (퍼센트)
    coverage = 0
    if len(job_keywords) > 0:
        coverage = round(len(matched) / len(job_keywords) * 100, 2)

    return {
        "coverage_score": coverage,
        "matched_keywords": matched,
        "missing_keywords": missing
    }


# ------------------------------
# 부족 키워드 기반 추천 문구 생성 (템플릿 방식)
# ------------------------------
def generate_recommend_phrases(missing_keywords: List[str]) -> List[str]:
    template = [
        "{}와 관련된 문제를 진단하고 해결한 경험을 구체적으로 작성해보세요.",
        "{}을(를) 점검하거나 품질을 관리한 사례가 있다면 추가하는 것이 좋습니다.",
        "{} 능력을 바탕으로 실행했던 행동 중심 경험을 작성해보세요."
    ]

    recs = []
    for kw in missing_keywords[:5]:  # 최대 5개만 추천
        for t in template:
            recs.append(t.format(kw))
    return recs


# ------------------------------
# 통합 함수
# ------------------------------
def analyze_keyword_coverage(job_info: Dict, essay_text: str) -> Dict:
    result = compute_keyword_coverage(job_info, essay_text)

    # 추천 문구
    result["recommended_phrases"] = generate_recommend_phrases(
        result["missing_keywords"]
    )

    return result


# ------------------------------
# 모듈 단독 실행 테스트
# ------------------------------
if __name__ == "__main__":
    sample_job = {
        "skills": ["고장의 발견·수리", "문제 해결", "품질관리분석"],
        "knowledge": ["안전과 보안", "기계", "통신"],
        "main_abilities": ["신체·운동능력"],
        "interests": ["서비스 정신", "책임감"]
    }

    essay = """
    저는 현장에서 기계 점검과 안전 기준을 준수하는 경험을 해왔습니다.
    문제를 해결하기 위해 기록을 분석하고 서비스를 제공한 경험이 있습니다.
    """

    print(analyze_keyword_coverage(sample_job, essay))