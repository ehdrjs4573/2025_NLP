import streamlit as st
import pandas as pd
import altair as alt

from nlp.report_builder import build_report
from nlp.loaders import load_job_embeddings, load_company_embeddings


# ==================================================
# 페이지 설정
# ==================================================
st.set_page_config(
    page_title="자기소개서 NLP 분석 서비스",
    layout="wide",
)

st.title("자기소개서 의미 기반 분석")
st.markdown(
    "지원하는 **직무**와 **기업**을 선택한 후 자기소개서를 입력하세요."
)


# ==================================================
# 데이터 로드 (캐싱)
# ==================================================
@st.cache_data
def load_data():
    return load_job_embeddings(), load_company_embeddings()


jobs, companies = load_data()


# ==================================================
# 직무 필터링 구조 생성
# ==================================================
job_tree = {}

for job_cd, job in jobs.items():
    top = job.get("top_nm", "기타")
    mid = job.get("aptit_name", "기타")

    job_tree.setdefault(top, {})
    job_tree[top].setdefault(mid, [])
    job_tree[top][mid].append(job_cd)


# ==================================================
# UI: 직무 선택
# ==================================================
st.subheader("직무 선택")

col1, col2, col3 = st.columns(3)

with col1:
    top_category = st.selectbox("직무 대분류", list(job_tree.keys()))

with col2:
    mid_category = st.selectbox(
        "직무 중분류",
        list(job_tree[top_category].keys())
    )

with col3:
    job_id = st.selectbox(
        "세부 직무",
        job_tree[top_category][mid_category],
        format_func=lambda x: jobs[x]["job_nm"]
    )


# ==================================================
# UI: 기업 선택
# ==================================================
st.subheader("기업 선택")

company_id = st.selectbox(
    "기업",
    list(companies.keys()),
    format_func=lambda x: companies[x]["company_name"]
)


# ==================================================
# 자기소개서 입력
# ==================================================
st.subheader("자기소개서 입력")

essay_text = st.text_area(
    "자기소개서 본문",
    height=300,
    placeholder="자기소개서를 입력하세요."
)


# ==================================================
# 분석 실행
# ==================================================
st.markdown("---")

if st.button("분석하기"):
    if not essay_text.strip():
        st.warning("자기소개서를 입력해주세요.")
        st.stop()

    with st.spinner("자기소개서를 분석 중입니다..."):
        report = build_report(
            essay_text=essay_text,
            job_id=job_id,
            company_id=company_id
        )

    st.success("분석 완료")
    st.markdown("---")

# ==================================================
# 1. 전체 요약 (점수만 컬럼)
# ==================================================
st.subheader("전체 분석 요약")

sim = report["similarity"]

col1, col2 = st.columns(2)

with col1:
    st.metric("직무 적합도", f"{sim['job_fit']}점")

with col2:
    st.metric("기업 적합도", f"{sim['company_fit']}점")

if sim["job_fit"] >= 70:
    st.success("지원 직무와 매우 잘 맞는 경험이 드러납니다.")
elif sim["job_fit"] >= 50:
    st.info("직무와 연결되는 경험은 있으나 핵심 역량 표현이 부족합니다.")
else:
    st.warning("직무 요구 역량과의 연결성이 낮아 보완이 필요합니다.")

    # ==================================================
    # 2. 직무·기업 적합도 해석
    # ==================================================
    st.subheader("직무·기업 적합도 해석")

    st.write(
        f"""
- **직무 적합도 {sim['job_fit']}점**  
  → 직무 관련 경험은 있으나, 역할·행동·기술 중심 서술을 강화하면 좋습니다.

- **기업 적합도 {sim['company_fit']}점**  
  → 기업의 실제 사업·조직 맥락과 직접 연결된 표현이 부족합니다.
"""
    )


    # ==================================================
    # 3. 직무 핵심 역량 커버리지
    # ==================================================
    st.subheader("직무 핵심 역량 커버리지")

    kc = report["keyword_coverage"]
    group_cov = kc["group_coverage"]

    df = pd.DataFrame({
        "역량": ["기술(Skills)", "지식(Knowledge)", "핵심역량(Abilities)"],
        "커버리지(%)": [
            group_cov["skills"]["coverage_score"],
            group_cov["knowledge"]["coverage_score"],
            group_cov["main_abilities"]["coverage_score"],
        ]
    })

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            y=alt.Y("역량", title="역량 유형", sort=None),
            x=alt.X(
                "커버리지(%)",
                title="반영률 (%)",
                scale=alt.Scale(domain=[0, 100])
            ),
            tooltip=["커버리지(%)"]
        )
    )

    st.altair_chart(chart, use_container_width=True)

    st.write(f"전체 키워드 반영률: **{kc['coverage_score']}%**")

    st.write("부족한 핵심 요소 예시:")
    for kw in kc["missing_keywords"][:5]:
        st.write("-", kw)

    st.write("개선 제안 문장:")
    for rec in kc.get("recommended_phrases", [])[:5]:
        st.write("•", rec)


    # ==================================================
    # 4. 반복 표현 분석
    # ==================================================
    st.subheader("반복 표현 분석")

    rep = report["repetition"]

    if rep["repeated_words"]:
        st.write("반복 사용된 단어:")
        for w, c in rep["repeated_words"].items():
            st.write(f"- '{w}' : {c}회")

    st.write("문장 스타일 개선 제안:")
    for s in rep["suggestions"]:
        st.write("•", s)


    # ==================================================
    # 5. STAR 구조 분석
    # ==================================================
    st.subheader("STAR 구조 분석")

    star = report["star_analysis"]
    count = {"S": 0, "T": 0, "A": 0, "R": 0}

    for _, label in star:
        if label in count:
            count[label] += 1

    st.write(
        f"""
- 상황(S): {count['S']}문장  
- 과제(T): {count['T']}문장  
- 행동(A): {count['A']}문장  
- 결과(R): {count['R']}문장
"""
    )

    if count["A"] < 2 or count["R"] < 2:
        st.warning(
            "행동(Action)과 결과(Result) 중심 문장을 보강하면 "
            "자기소개서의 설득력이 크게 향상됩니다."
        )

    st.write("문장별 분석:")
    for sent, label in star:
        st.write(f"[{label}] {sent}")