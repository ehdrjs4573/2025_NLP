"""
test_keyword.py

keyword_coverage 기능을 검증하기 위한 테스트 스크립트.
직무 임베딩 로딩 → 해당 직무의 원본 job_info 로딩 → 자기소개서 대비 키워드 매칭 분석
"""

from nlp.loaders import load_raw_job_vectors
from nlp.keyword_coverage import analyze_keyword_coverage

# ----------------------------------------
# 1) 직무 데이터 로드 (raw career_job_vectors.json)
# ----------------------------------------
jobs = load_raw_job_vectors()

# 첫 번째 직무 하나 선택 (필요하면 job_cd 직접 입력)
sample_job_id = next(iter(jobs.keys()))
job_info = jobs[sample_job_id]

print(f"[TEST] 선택된 직무 ID: {sample_job_id}")
print(f"[TEST] 직무명: {job_info.get('job_nm')}")

# ----------------------------------------
# 2) 테스트할 자기소개서 텍스트
# ----------------------------------------
essay_text = """
저는 현장에서 기계 점검과 안전 기준을 준수하는 경험이 있습니다.
문제 해결을 위해 데이터를 확인하고 필요한 조치를 수행했습니다.
또한 고객과의 소통을 통해 서비스 품질을 유지하려고 노력했습니다.
"""

print("\n[TEST] Essay Text:")
print(essay_text)

# ----------------------------------------
# 3) 키워드 커버리지 분석 실행
# ----------------------------------------
result = analyze_keyword_coverage(job_info, essay_text)

# ----------------------------------------
# 4) 결과 출력
# ----------------------------------------
print("\n===== Keyword Coverage Result =====")
print(f"Coverage Score: {result['coverage_score']}%")

print("\nMatched Keywords:")
for mk in result["matched_keywords"]:
    print(" -", mk)

print("\nMissing Keywords:")
for mk in result["missing_keywords"]:
    print(" -", mk)

print("\nRecommended Phrases:")
for rp in result["recommended_phrases"][:6]:  # 너무 많으면 6개만 표시
    print(" -", rp)

print("\n===================================")