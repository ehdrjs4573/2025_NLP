"""
report_builder.py

자기소개서 분석 결과를 하나의 리포트(dict)로 통합하는 모듈.
각 NLP 분석 모듈의 출력을 모아 최종 결과를 구성한다.
"""

from __future__ import annotations
from typing import Dict

from nlp.preprocessing import preprocess
from nlp.loaders import (
    get_job_vector,
    get_company_vector,
    load_raw_job_vectors,
)
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
    sent_embeddings = embed_sentences(sentences)
    essay_vector = sent_embeddings.mean(axis=0)

    # 3. 직무 / 기업 벡터 로딩
    job_vector = get_job_vector(job_id)
    company_vector = get_company_vector(company_id)

    # 4. 유사도 분석
    similarity_result = compute_fit_scores(
        job_vector=job_vector,
        company_vector=company_vector,
        essay_vector=essay_vector,
    )

    # 5. 직무 RAW 정보 로딩 (키워드 커버리지용)
    raw_jobs = load_raw_job_vectors()
    job_info = raw_jobs[job_id]

    keyword_result = analyze_keyword_coverage(
        job_info=job_info,
        essay_text=prep["clean_text"],
    )

    # 6. 반복 표현 분석
    repetition_result = analyze_repetition(prep["clean_text"])

    # 7. STAR 분석
    star_result = tag_star_semantic(essay_text)

    # 8. 최종 리포트 구성
    report = {
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

    return report


# ------------------------------------------
# 테스트용 (제출 시 삭제해도 무방)
# ------------------------------------------
if __name__ == "__main__":
    sample_text = """
현재 금융권 취업 동아리 활동 중이며, 노년층의 '디지털 문맹'을 해소하기 위한 활동을 진행한 경험이 있습니다. 
노년층분들이 자주 방문하는 노인정, 요양원 등 직접 방문하여 은행 앱 사용법을 친절히 알려드리며 배우신 것을 금방 잊어버리시지 않게 명함이나 팸플릿에 은행 어플 가이드라인을 제공해 드렸습니다. 
이 경험을 통해 실질적인 금융 지원의 필요성을 체감했고, 세대 구분 없이 지역 사회에 기여하는 금융 서비스의 중요성을 느꼈습니다.

신협은 ‘사람 중심의 금융’을 실천하며, 지역사회와 조합원의 삶의 질 향상에 기여하는 금융기관입니다.
사람에 대한 이해와 공감에서 출발하는 금융 서비스가 진정한 가치라고 믿기에, 신협의 가치관에 깊이 공감해 인턴십에 지원하게 되었습니다
    """

    result = build_report(
        essay_text=sample_text,
        job_id=1,
        company_id="samsung",
    )

    from pprint import pprint
    pprint(result)