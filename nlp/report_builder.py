"""
report_builder.py

자기소개서 분석 결과를 하나의 리포트(dict)로 통합하는 모듈.
각 NLP 분석 모듈의 출력을 모아 최종 결과를 구성한다.
"""

from __future__ import annotations
from typing import Dict

from nlp.preprocessing import preprocess
from nlp.loaders import get_job_vector, get_company_vector
from nlp.embedding import embed_sentences
from nlp.similarity import compute_fit_scores
from nlp.keyword_coverage import analyze_keyword_coverage
from nlp.repetition_detector import analyze_repetition
from nlp.star_detector import tag_star_semantic


def build_report(
    essay_text: str,
    job_id: int,
    company_id: str,
) -> Dict:
    """
    전체 NLP 파이프라인을 실행하고 결과를 하나의 리포트로 반환한다.
    """

    # 1. 전처리
    prep = preprocess(essay_text)
    sentences = prep["sentences"]

    # 2. 임베딩
    sentence_embeddings = embed_sentences(sentences)
    essay_vector = sentence_embeddings.mean(axis=0)

    # 3. 직무 / 기업 벡터 로딩
    job_vector = get_job_vector(job_id)
    company_vector = get_company_vector(company_id)

    # 4. 의미 유사도 분석 (calibration 적용)
    similarity_result = compute_fit_scores(
        job_vector=job_vector,
        company_vector=company_vector,
        essay_vector=essay_vector,
    )

    # 5. 직무 핵심 역량 커버리지 (의미 기반)
    keyword_result = analyze_keyword_coverage(
        job_id=job_id,
        essay_text=prep["clean_text"],
    )

    # 6. 반복 표현 분석
    repetition_result = analyze_repetition(prep["clean_text"])

    # 7. STAR 구조 분석
    star_result = tag_star_semantic(essay_text)

    # 8. 최종 리포트
    return {
        "job_id": job_id,
        "company_id": company_id,
        "preprocessing": {
            "sentence_count": len(sentences),
        },
        "similarity": similarity_result,
        "keyword_coverage": keyword_result,
        "repetition": repetition_result,
        "star_analysis": star_result,
    }


# ------------------------------------------
# 테스트용 (로컬 확인용, 제출 시 삭제 가능)
# ------------------------------------------
if __name__ == "__main__":
    sample_text = """
    금융권 취업 동아리 활동을 통해 노년층 대상 금융 앱 교육을 진행했습니다.
    """

    result = build_report(
        essay_text=sample_text,
        job_id=1,
        company_id="samsung",
    )

    from pprint import pprint
    pprint(result)