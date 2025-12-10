"""
repetition_detector.py

자기소개서 내부에서 반복되는 단어, 구절(phrase),문장 구조를 자동으로 감지하는 모듈.
하드코딩 없이 자기소개서에서 직접 통계 기반으로 반복 패턴을 추출합니다.
"""

from __future__ import annotations
import re
from typing import List, Dict
from collections import Counter
from konlpy.tag import Okt

okt = Okt()


# ---------------------------------------
# 1) 단어 반복 탐지
# ---------------------------------------
def detect_repeated_words(text: str, threshold: int = 3) -> Dict[str, int]:
    tokens = [t for t in okt.nouns(text) if len(t) > 1]
    counter = Counter(tokens)

    repeated = {word: cnt for word, cnt in counter.items() if cnt >= threshold}

    return repeated


# ---------------------------------------
# 2) 구절(n-gram) 반복 탐지 (2~4gram)
# ---------------------------------------
def extract_ngrams(tokens: List[str], n: int):
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]


def detect_repeated_phrases(text: str, threshold: int = 2) -> Dict[str, int]:
    tokens = [t for t in okt.morphs(text) if len(t) > 1]

    phrase_counter = Counter()

    for n in range(2, 5):  # 2~4 gram
        ngrams = extract_ngrams(tokens, n)
        for ngram in ngrams:
            phrase_counter[ngram] += 1

    repeated = {
        phrase: cnt for phrase, cnt in phrase_counter.items()
        if cnt >= threshold
    }

    return repeated


# ---------------------------------------
# 3) 문장 구조 반복 탐지
#    예: "저는 ~했습니다" 패턴
# ---------------------------------------
def detect_sentence_patterns(text: str) -> Dict[str, int]:
    sentences = re.split(r"[.!?]\s*|\n", text)
    pattern_counter = Counter()

    for s in sentences:
        s = s.strip()
        if not s:
            continue

        # 주요 문장 구조만 단순화 (더 발전 가능)
        pattern = re.sub(r"[가-힣0-9]+", "X", s)  
        # ex: "저는 프로젝트를 수행했습니다" → "X X X X"

        pattern_counter[pattern] += 1

    repeated = {p: c for p, c in pattern_counter.items() if c >= 2}
    return repeated


# ---------------------------------------
# 4) 통합 + 제안문 생성
# ---------------------------------------
def analyze_repetition(text: str) -> Dict:
    words = detect_repeated_words(text)
    phrases = detect_repeated_phrases(text)
    patterns = detect_sentence_patterns(text)

    suggestions = []

    for w, c in words.items():
        suggestions.append(f"단어 '{w}'가 {c}회 반복됩니다. 표현을 다양화하거나 구체적 사례로 바꾸는 것을 추천합니다.")

    for p, c in phrases.items():
        suggestions.append(f"구절 '{p}'가 {c}회 반복됩니다. 같은 문장이 반복되면 설득력이 떨어질 수 있습니다.")

    for p, c in patterns.items():
        suggestions.append("유사한 문장 구조가 반복됩니다. 문장 구조를 다양하게 작성하면 더 자연스러워집니다.")

    return {
        "repeated_words": words,
        "repeated_phrases": phrases,
        "repeated_sentence_patterns": patterns,
        "suggestions": suggestions
    }


# ---------------------------------------
# 5) 테스트용 (터미널 출력: 이모지/색 없음, 깔끔한 형식)
# ---------------------------------------
if __name__ == "__main__":
    sample = """
    저는 프로젝트를 수행하며 다양한 경험을 쌓았습니다.
    해당 프로젝트에서 문제를 해결했습니다.
    또 다른 프로젝트에서도 협업을 통해 문제를 해결했습니다.
    저는 문제 해결 능력을 키우기 위해 노력했습니다.
    """

    result = analyze_repetition(sample)

    print("\n============================================")
    print("            반복 표현 분석 결과")
    print("============================================\n")

    # 1) 단어 반복
    print("[1] 반복된 단어 (3회 이상)")
    if result["repeated_words"]:
        for w, c in result["repeated_words"].items():
            print(f" - {w}: {c}회")
    else:
        print(" - 없음")

    print("\n[2] 반복된 구절 (n-gram 분석)")
    if result["repeated_phrases"]:
        for p, c in result["repeated_phrases"].items():
            print(f" - {p}: {c}회")
    else:
        print(" - 없음")

    print("\n[3] 반복된 문장 구조")
    if result["repeated_sentence_patterns"]:
        for p, c in result["repeated_sentence_patterns"].items():
            print(f" - 패턴: {p}  |  등장 횟수: {c}회")
    else:
        print(" - 없음")

    print("\n[4] 개선 제안")
    if result["suggestions"]:
        for s in result["suggestions"]:
            print(f" - {s}")
    else:
        print(" - 없음")

    print("\n============================================\n")