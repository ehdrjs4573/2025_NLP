"""
Semantic-based STAR detector
SBERT 임베딩을 활용한 문장 의미 기반 S/T/A/R 태깅
"""

from __future__ import annotations
from typing import List, Tuple
import re
import numpy as np

from nlp.embedding import embed_sentences   # 여러 문장 임베딩


# 문장 나누기
def split_sentences(text: str) -> List[str]:
    sentences = re.split(r"[.!?]\s*|\n", text)
    return [s.strip() for s in sentences if s.strip()]

# STAR 예시 문장 정의
S_examples = [
    "프로젝트를 진행하던 중 예기치 못한 문제가 발생했습니다.",
    "팀 전체가 해결하기 어려운 상황에 직면했습니다.",
    "업무 환경이 급격히 변하면서 혼란이 있었습니다.",
    "초기 설계 단계에서 큰 오류가 발견되는 상황이었습니다.",
    "담당하던 기능에서 지속적인 장애가 발생했습니다.",
    "프로젝트 일정이 지연되는 문제가 있었습니다.",
    "사용자 수가 급증하여 서버가 불안정해졌습니다.",
    "팀 내 의사소통 부족으로 갈등이 생겼습니다.",
    "새로운 기술을 적용해야 하는 상황이었습니다.",
    "예상보다 복잡한 요구사항이 추가되었습니다.",
    "테스트 과정에서 치명적인 버그가 발견되었습니다.",
    "서비스 배포 직전 심각한 성능 저하가 발생했습니다.",
    "외부 API 변경으로 기능이 정상적으로 동작하지 않았습니다.",
    "기획 변경으로 전체 구조를 수정해야 하는 상황이었습니다.",
    "고객의 불만이 지속적으로 접수되는 상황이었습니다.",
    "데이터 손실 위험이 있는 문제가 발생했습니다.",
    "주요 담당자가 갑작스러운 부재로 프로젝트가 정체되었습니다.",
    "문제 해결을 위한 자료가 부족한 상황이었습니다.",
    "주어진 시간 대비 과업량이 과도하게 많은 상황이었습니다.",
    "프로젝트 방향성이 모호해 혼란이 있었습니다."
]

T_examples = [
    "저는 이 프로젝트에서 백엔드 개발을 맡았습니다.",
    "제가 맡은 역할은 문제의 원인을 분석하는 일이었습니다.",
    "프로젝트 전체 구조를 개선하는 책임을 맡았습니다.",
    "저는 팀 내에서 데이터 처리 모듈을 담당했습니다.",
    "제 임무는 장애를 신속하게 해결하는 것이었습니다.",
    "저는 팀원 간 협업을 조율하는 역할을 맡았습니다.",
    "제가 담당한 업무는 성능 개선을 위한 분석 작업이었습니다.",
    "저에게 주어진 목표는 기능 안정성을 확보하는 것이었습니다.",
    "저는 사용자 요구사항을 기술적으로 해석하는 임무를 맡았습니다.",
    "저는 프로젝트 일정 관리를 담당했습니다.",
    "제가 맡은 역할은 테스트 자동화 환경을 구축하는 것이었습니다.",
    "저는 오류 로그를 정리하고 패턴을 분석하는 업무를 담당했습니다.",
    "제 과제는 문제 해결 방안을 제시하는 일이었습니다.",
    "저는 서비스 품질을 높이기 위한 개선안을 도출하는 임무를 맡았습니다.",
    "제가 수행해야 할 목표는 배포 안정성 확보였습니다.",
    "저는 팀에서 기술적 의사결정을 지원하는 역할을 맡았습니다.",
    "제가 맡은 업무는 신규 기능 개발과 유지보수였습니다.",
    "저는 데이터 정확성을 검증하는 역할을 담당했습니다.",
    "제 임무는 문제 상황을 팀에 명확히 공유하는 것이었습니다.",
    "저는 프로젝트의 핵심 기능을 책임지는 역할을 맡았습니다."
]

A_examples = [
    "문제를 해결하기 위해 로그를 면밀히 분석했습니다.",
    "서비스의 안정성을 높이기 위해 코드를 재구성했습니다.",
    "장애 원인을 파악하여 구조적 개선을 수행했습니다.",
    "팀원들과 소통하며 해결책을 조율했습니다.",
    "데이터 패턴을 분석하여 오류 지점을 찾았습니다.",
    "테스트 코드를 작성해 문제 재발을 방지했습니다.",
    "이슈를 추적하기 위해 모니터링 시스템을 구축했습니다.",
    "새로운 알고리즘을 설계하여 성능을 개선했습니다.",
    "코드 리뷰를 진행하며 품질을 향상시켰습니다.",
    "기능 구현을 위해 여러 기술적 시도를 수행했습니다.",
    "문제 구간을 직접 디버깅하며 해결책을 찾았습니다.",
    "기존 시스템의 취약점을 분석해 보완했습니다.",
    "사용자 피드백을 반영하여 기능을 수정했습니다.",
    "팀이 사용할 문서화를 작성해 협업 효율을 높였습니다.",
    "프로젝트 구조를 재설계해 유지보수성을 높였습니다.",
    "원인을 빠르게 파악하기 위해 반복 테스트를 진행했습니다.",
    "새로운 기술을 도입하기 위해 학습하고 적용했습니다.",
    "성능 병목을 찾아 개선 작업을 수행했습니다.",
    "문제 발생 가능성을 줄이기 위해 예외 처리를 강화했습니다.",
    "협업을 위해 Git Flow 전략을 활용했습니다."
]
R_examples = [
    "그 결과 문제를 성공적으로 해결할 수 있었습니다.",
    "서비스의 안정성이 크게 향상되었습니다.",
    "프로젝트를 일정에 맞춰 마무리할 수 있었습니다.",
    "오류율이 눈에 띄게 감소했습니다.",
    "사용자 만족도가 증가했습니다.",
    "팀의 업무 효율이 향상되었습니다.",
    "새로운 기능이 정상적으로 배포되었습니다.",
    "장애가 재발하지 않는 결과를 얻었습니다.",
    "전체 성능이 이전보다 크게 향상되었습니다.",
    "협업 과정이 더 원활해졌습니다.",
    "서비스 로딩 시간이 개선되었습니다.",
    "문제 해결 속도가 빨라졌습니다.",
    "기능이 안정적으로 운영되었습니다.",
    "데이터 정확성이 높아졌습니다.",
    "팀 내 의사소통이 개선되었습니다.",
    "업무 프로세스가 간소화되었습니다.",
    "모든 테스트를 성공적으로 통과했습니다.",
    "사용자 불만이 감소했습니다.",
    "프로젝트 목표를 달성했습니다.",
    "팀의 기술적 역량이 향상되었습니다."
]
# SBERT로 대표 벡터 생성
def get_center_vector(sentences: List[str]) -> np.ndarray:
    vectors = embed_sentences(sentences)
    return np.mean(vectors, axis=0)

S_vec = get_center_vector(S_examples)
T_vec = get_center_vector(T_examples)
A_vec = get_center_vector(A_examples)
R_vec = get_center_vector(R_examples)


# 코사인 유사도
def cosine_similarity(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    return float(np.dot(v1, v2) / ((np.linalg.norm(v1) * np.linalg.norm(v2)) + 1e-8))


# 문장 하나 태깅
def label_sentence(sentence: str) -> str:
    vec = embed_sentences([sentence])[0]

    sims = {
        "S": cosine_similarity(vec, S_vec),
        "T": cosine_similarity(vec, T_vec),
        "A": cosine_similarity(vec, A_vec),
        "R": cosine_similarity(vec, R_vec),
    }

    best = max(sims, key=sims.get)
    best_score = sims[best]

    if best_score < 0.20:
        return "O"

    return best


# 전체 문장 태깅
def tag_star_semantic(text: str) -> List[Tuple[str, str]]:
    sentences = split_sentences(text)
    return [(s, label_sentence(s)) for s in sentences]


# STAR 에피소드로 묶기
def group_star_episodes(
    tagged: List[Tuple[str, str]],
    min_sentences: int = 1
):
    """
    (sentence, label) 리스트를 받아 STAR 에피소드 단위로 묶는다.
    S가 나오면 새로운 에피소드 시작으로 간주한다.
    S 없이 T/A/R만 나오는 경우도 하나의 에피소드로 묶어준다.
    """
    episodes = []
    cur_sents = []
    cur_labels = []

    for sent, label in tagged:
        # 공백 문장 방어
        if not sent.strip():
            continue

        if label == "S":
            # 이전 에피소드 저장
            if cur_sents:
                if len(cur_sents) >= min_sentences:
                    episodes.append(
                        {"sentences": cur_sents, "labels": cur_labels}
                    )
                cur_sents = []
                cur_labels = []

            # 새 에피소드 시작
            cur_sents.append(sent)
            cur_labels.append(label)
        else:
            # 아직 아무것도 없는데 O만 나오면 스킵
            if not cur_sents and label == "O":
                continue
            # 그 외(T/A/R/O)는 현재 에피소드에 붙이기
            cur_sents.append(sent)
            cur_labels.append(label)

    # 마지막 에피소드 처리
    if cur_sents and len(cur_sents) >= min_sentences:
        episodes.append(
            {"sentences": cur_sents, "labels": cur_labels}
        )

    return episodes


# 에피소드별 STAR 완성도 평가
def evaluate_episode(episode: dict):
    labels = episode["labels"]
    label_set = set(labels)

    has_S = "S" in label_set
    has_T = "T" in label_set
    has_A = "A" in label_set
    has_R = "R" in label_set

    num_A = labels.count("A")
    num_R = labels.count("R")

    # 기본 점수: S/T/A/R 각 25점씩
    base_score = (
        (1 if has_S else 0) +
        (1 if has_T else 0) +
        (1 if has_A else 0) +
        (1 if has_R else 0)
    ) / 4 * 100

    # 행동/결과가 풍부하면 약간 보너스 (최대 +10)
    bonus = 0
    if num_A >= 2:
        bonus += 5
    if num_R >= 2:
        bonus += 5

    score = min(100.0, round(base_score + bonus, 1))

    feedback = []

    if not has_S:
        feedback.append("상황(S)이 드러나지 않아, 언제·어디서·무슨 계기로 시작된 경험인지 보완하면 좋습니다.")
    if not has_T:
        feedback.append("역할/목표(T)가 약해, 내가 맡은 책임과 구체적인 목표를 명확히 쓰면 좋습니다.")
    if not has_A:
        feedback.append("행동(A)이 부족해, 실제로 무엇을 어떻게 했는지를 단계별로 풀어 쓰면 좋습니다.")
    if not has_R:
        feedback.append("결과(R)가 없거나 약해, 숫자·변화·배운 점 등을 통해 성과를 명확히 드러내면 좋습니다.")

    if has_A and has_R and score >= 75:
        feedback.append("행동과 결과가 잘 연결된 STAR 구조입니다. 이 경험은 자소서 핵심 카드로 활용할 수 있습니다.")

    return {
        "score": score,
        "has_S": has_S,
        "has_T": has_T,
        "has_A": has_A,
        "has_R": has_R,
        "num_actions": num_A,
        "num_results": num_R,
        "feedback": feedback,
    }


# 전체 텍스트 STAR 구조 분석
def analyze_star_structure(text: str):
    """
    텍스트 한 편에 대해:
    - 문장별 S/T/A/R 태깅
    - 에피소드 단위로 묶기
    - 에피소드별 점수 & 피드백 생성
    를 한 번에 수행.
    """
    tagged = tag_star_semantic(text)
    episodes = group_star_episodes(tagged)

    episode_results = []
    for idx, ep in enumerate(episodes, start=1):
        eval_result = evaluate_episode(ep)
        episode_results.append(
            {
                "episode_index": idx,
                "sentences": ep["sentences"],
                "labels": ep["labels"],
                "evaluation": eval_result,
            }
        )

    return {
        "tagged_sentences": tagged,
        "episodes": episode_results,
    }


# 1테스트 실행
if __name__ == "__main__":
    sample = """
    팀 프로젝트에서 API 서버 오류가 반복되는 상황이었습니다.
    저는 원인 분석과 복구 역할을 맡았습니다.
    로그 분석을 통해 문제 구간을 찾았습니다.
    그 결과 장애를 해결할 수 있었습니다.

    또 다른 프로젝트에서는 데이터 정합성 문제가 발생했습니다.
    저는 수집 과정을 점검하고 ETL 파이프라인을 재설계했습니다.
    그 결과 오류율을 크게 줄일 수 있었습니다.
    """

    analysis = analyze_star_structure(sample)

    print("=== [1] 문장별 STAR 태깅 ===")
    for s, l in analysis["tagged_sentences"]:
        print(f"[{l}] {s}")

    print("\n=== [2] 에피소드별 STAR 분석 ===")
    for ep in analysis["episodes"]:
        ev = ep["evaluation"]
        print(f"\n[Episode {ep['episode_index']}]")
        for s, l in zip(ep["sentences"], ep["labels"]):
            print(f"  [{l}] {s}")

        print(f"  → STAR 점수: {ev['score']}점")
        print(f"    포함 요소: S={ev['has_S']}, T={ev['has_T']}, A={ev['has_A']}, R={ev['has_R']}")
        if ev["feedback"]:
            print("    피드백:")
            for fb in ev["feedback"]:
                print(f"      - {fb}")