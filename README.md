# 2025_NLP

NLP 기반 자기소개서 분석 시스템

## 1. 프로젝트 소개
현재 자기소개서는 취업준비생에게 과도한 부담을 주고 있으며, 이에 따라 보다 객관적이고 지표 기반의 분석 서비스에 대한 필요성이 커지고 있다. 본 프로젝트는 단순히 자기소개서의 합격 여부를 판단하는 것을 넘어서, 강점과 약점, 역량을 분석해 작성에 실질적인 도움을 주는 것을 목표로 한다.
이를 위해 한국어 자기소개서 텍스트를 입력받아 직무,기업 정보와 비교하고, 의미 기반 분석을 통해 핵심 키워드, 직무 적합도, 문장 품질 등을 평가하는 NLP 파이프라인을 구현한다.

## 2. 프로젝트 개요
- 분석 대상
	- 직무(커리어넷 직업 데이터 기반)
	- 기업(주요 기업 정보 직접 정리)
	- 사용자 자기소개서 텍스트
- 핵심 기술
	- SBERT 한국어 문장 임베딩 (jhgan/ko-sbert-multitask)
	- Cosine Similarity 기반 의미 유사도 계산
	- Rule-based + Semantic Hybrid 분석
- 구현 방식
	- Streamlit 기반 웹 UI
	- JSON 기반 데이터 관리
	- 로컬 SBERT 모델 사용

## 3. NLP 분석 파이프라인
본 프로젝트의 핵심은 자기소개서 텍스트를 직무 요구사항과
동일한 의미 공간에서 비교하는 NLP 분석 파이프라인에 있다.

1) 텍스트 전처리
- 입력된 자기소개서를 문장 단위로 분리
- 불필요한 기호 및 공백 제거
- 문장 단위 의미 분석을 위한 구조화

2) 직무 및 기업 정보 수집
- CareerNet OpenAPI를 활용하여 직무 목록 및 상세 정보 수집
- 직무 설명, 핵심 능력, 수행 기술, 필요 지식 항목 정리
- 기업 정보는 서비스 목적에 맞게 직접 조사 및 정리하여 텍스트화

3) 직무 특징 텍스트 구성
- 다음 항목을 하나의 직무 텍스트로 결합
  - 하는 일 요약
  - 핵심 능력 (Abilities)
  - 수행 기술 (Skills)
  - 필요 지식 (Knowledge)
- NLP 분석에 바로 활용 가능한 구조로 정규화

4) SBERT 기반 임베딩 생성
- 한국어 문장 임베딩 모델 `jhgan/ko-sbert-multitask` 사용
- 직무 텍스트, 기업 텍스트, 자기소개서 문장을 동일한 임베딩 공간(768차원)으로 변환
- Cosine Similarity 계산을 위한 기반 데이터 구축

5) 자기소개서 분석
- 자기소개서 문장별 SBERT 임베딩 생성
- 직무 벡터와의 의미 유사도 계산
- 직무 핵심 역량(Skills / Knowledge / Abilities) 대비 의미 매칭 분석
- 반복 표현 탐지 및 문장 스타일 개선 포인트 도출
- STAR 구조(Situation / Task / Action / Result) 기반 문장 분류

본 프로젝트는 단순 키워드 매칭 방식의 한계를 극복하기 위해
문장 임베딩 기반 의미 유사도 분석을 사용한다.

예를 들어,
- "문제를 분석하여 해결했다"
- "이슈를 파악하고 개선 방안을 도출했다"

와 같이 표면적인 단어가 달라도,
SBERT 임베딩 공간에서는 유사한 의미 벡터로 표현된다.
이를 통해 동일한 역량이 다양한 표현으로 서술된 경우도
의미적으로 인식할 수 있다.

6) 최종 분석 리포트 생성
- 직무 적합도 점수
- 직무 핵심 역량 커버리지
- 부족한 핵심 역량 키워드
- 문장 개선을 위한 추천 문구
- 반복 표현 분석 결과
- STAR 구조 분석 요약

## 4. 사용방법
1) 직무 선택
	•	직무 데이터를 기반으로
대분류 → 중분류 → 세부 직무 3단 드롭다운 구조 제공
	•	많은 직무 데이터도 탐색 가능하도록 계층화

2) 기업 선택
	•	기업 리스트 기반 단일 드롭다운
	•	직무 선택과 독립적으로 동작

3) 자기소개서 입력
	•	실제 자기소개서 전문 입력 가능
	•	입력 텍스트를 분석 대상으로 사용
<img width="1394" height="770" alt="스크린샷 2025-12-12 오후 11 55 18" src="https://github.com/user-attachments/assets/bfc2c3c0-9978-4554-b468-a7467acea4f7" />


4) 분석 결과 확인

사용자는 분석 결과를 다음 항목으로 확인할 수 있습니다.
	•	직무 적합도 요약
	•	직무 핵심 역량 커버리지(Skills / Knowledge / Abilities)
	•	부족한 핵심 역량 키워드
	•	문장 개선을 위한 추천 문구
	•	반복 표현 분석 결과
	•	STAR 구조 분석 결과
<img width="1371" height="623" alt="스크린샷 2025-12-12 오후 11 55 54" src="https://github.com/user-attachments/assets/2dc2bd8a-82af-4717-8bb2-8a6519519dcc" />
<img width="1351" height="520" alt="스크린샷 2025-12-12 오후 11 56 09" src="https://github.com/user-attachments/assets/f9457511-e6f2-47ea-b8d7-b44ec18439f5" />
<img width="1351" height="649" alt="스크린샷 2025-12-12 오후 11 56 21" src="https://github.com/user-attachments/assets/dfc05613-0a3b-4970-bcf5-773e14f76210" />
<img width="1351" height="738" alt="스크린샷 2025-12-12 오후 11 56 26" src="https://github.com/user-attachments/assets/727a88e9-0379-4fb3-a0eb-b842bd1947a7" />


## 5. 기술 스택
- Language: Python
- NLP Model: SBERT (jhgan/ko-sbert-multitask)
- Framework: Streamlit
- Visualization: Altair
- Data Format: JSON
- Similarity Metric: Cosine Similarity
