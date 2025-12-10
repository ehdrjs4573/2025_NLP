from nlp.loaders import (
    load_job_embeddings,
    load_company_embeddings,
    get_job_vector,
    get_company_vector,
)
from nlp.embedding import embed_document_mean
from nlp.similarity import compute_fit_scores

# 1) 직무/기업 데이터 로드
jobs = load_job_embeddings()
companies = load_company_embeddings()

job_id = next(iter(jobs.keys()))
company_id = next(iter(companies.keys()))

print("사용할 job_id:", job_id)
print("사용할 company_id:", company_id)

job_vec = get_job_vector(job_id)
company_vec = get_company_vector(company_id)

# 2) 자소서 예시 텍스트
essay_text = """
저는 대학 시절 팀 프로젝트와 캡스톤 디자인을 통해 백엔드 개발과 협업 경험을 쌓았습니다.
Spring Boot와 데이터베이스를 활용해 REST API를 설계하고,
장애 발생 시 로그 분석과 예외 처리를 통해 문제를 해결한 경험이 있습니다.
"""

# 3) 자소서 임베딩 + 적합도 계산
sents, essay_vec, sent_embs = embed_document_mean(essay_text)
scores = compute_fit_scores(job_vec, company_vec, essay_vec)

print("\n적합도 점수:", scores)