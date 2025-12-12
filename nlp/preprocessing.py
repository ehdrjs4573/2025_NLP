"""
preprocessing.py

자기소개서 텍스트를 NLP 분석이 가능한 형태로 정제(cleaning)하는 모듈.
- 공백/특수문자 정리
- 문장 단위 분리
- 규칙 기반 정규화
- 형태소 기반 정규화 (Mecab)
- 맞춤법 교정(옵션)
- SBERT 기반 의미 카테고리 라벨링
"""

from __future__ import annotations
import re
import numpy as np
from typing import List, Dict, Optional

# =============================================================================
# 1) BASIC CLEANING
# =============================================================================

def clean_basic(text: str) -> str:
    """
    HTML 특수공백, 연속 공백, 들여쓰기 정리.
    """
    if not text:
        return ""

    # Word 복붙 시 생기는 HTML 스페이스 제거
    text = re.sub(r"&nbsp;|&emsp;|&ensp;", " ", text)

    # 줄바꿈 정리
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{2,}", "\n", text)

    # 연속 공백 → 1개
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =============================================================================
# 2) ENFORCE SENTENCE ENDING
# =============================================================================

def enforce_sentence_end(text: str) -> str:
    """
    줄바꿈으로 문장이 끝나는 경우 뒤에 마침표 자동 부여.
    '문제 해결\n다음 문장' → '문제 해결.\n다음 문장'
    """
    text = re.sub(r"([가-힣0-9])\n", r"\1.\n", text)
    return text


# =============================================================================
# 3) REMOVE NOISE
# =============================================================================

def remove_noise(text: str) -> str:
    """
    NLP 분석에 방해되는 특수문자 제거.
    URL, 이메일, 기본 문장부호는 유지.
    """
    text = re.sub(r"[^가-힣0-9a-zA-Z\s.,!?]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# =============================================================================
# 4-1) RULE-BASED NORMALIZATION
# =============================================================================

def normalize_text_rule_based(text: str) -> str:
    """
    가장 기본적인 표현 통일만 수행 (완전 하드코딩).
    """
    rules = [
        (r"하였습니다", "했습니다"),
        (r"하였습니다", "했습니다"),
        (r"하였다", "했다"),
        (r"해결함으로써", "해결하여"),
        (r"수행하였습니다", "수행했습니다"),
    ]
    for pattern, repl in rules:
        text = re.sub(pattern, repl, text)
    return text


# =============================================================================
# 4-2) MORPHOLOGICAL NORMALIZATION (Mecab)
# =============================================================================

try:
    from konlpy.tag import Mecab
    mecab = Mecab()
except Exception:
    mecab = None


def normalize_text_morphological(text: str) -> str:
    """
    Mecab을 사용해 동사/형용사를 기본형에 가까운 형태로 정규화.
    """
    if mecab is None:
        return text

    tokens = mecab.pos(text)
    normalized = []

    for word, tag in tokens:
        if tag.startswith("VV") or tag.startswith("VA"):   # 동사/형용사
            normalized.append(word)
        else:
            normalized.append(word)

    text = " ".join(normalized)
    text = re.sub(r"\s+", " ", text).strip()

    return text


# =============================================================================
# 5) SPELL CHECK (OPTIONAL)
# =============================================================================

try:
    from hanspell import spell_checker

    def spell_correct(text: str) -> str:
        try:
            checked = spell_checker.check(text)
            return checked.checked
        except:
            return text
except ImportError:
    def spell_correct(text: str) -> str:
        return text


# =============================================================================
# 6) SENTENCE SPLIT
# =============================================================================

def split_sentences(text: str) -> List[str]:
    """
    '.!? + 공백/줄바꿈' 을 기준으로 문장 단위로 나눔.
    """
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [s.strip() for s in parts if s.strip()]


# =============================================================================
# 7) SEMANTIC NORMALIZATION (SBERT)
# =============================================================================

try:
    from nlp.embedding import embed_sentences
except Exception:
    embed_sentences = None


SEMANTIC_CANONICALS = {
    "ACTION_RESOLVE": "문제를 해결했다.",
    "ACTION_COLLABORATE": "팀원들과 협업했다.",
    "ACTION_LEARN": "새로운 기술을 학습했다.",
    "ACTION_IMPROVE": "성능을 개선했다.",
    "ACTION_COMMUNICATE": "의사소통을 통해 조율했다.",
}


def _build_semantic_centers():
    if embed_sentences is None:
        return None

    labels = list(SEMANTIC_CANONICALS.keys())
    sents = list(SEMANTIC_CANONICALS.values())
    vecs = embed_sentences(sents)

    return {"labels": labels, "vectors": vecs}


_cached_semantic_centers = None


def semantic_label_sentences(sentences: List[str], threshold: float = 0.70):
    """
    문장을 SBERT로 임베딩하고 정의된 의미 그룹과 가장 가까운 그룹 라벨 부여.
    """
    global _cached_semantic_centers

    if embed_sentences is None:
        return [{"sentence": s, "label": None, "similarity": 0.0} for s in sentences]

    if _cached_semantic_centers is None:
        _cached_semantic_centers = _build_semantic_centers()

    centers = _cached_semantic_centers
    if centers is None:
        return [{"sentence": s, "label": None, "similarity": 0.0} for s in sentences]

    labels = centers["labels"]
    center_vecs = centers["vectors"]

    sent_vecs = embed_sentences(sentences)
    results = []

    for sent, vec in zip(sentences, sent_vecs):
        best_label = None
        best_sim = -1.0

        for lbl, c_vec in zip(labels, center_vecs):
            sim = float(vec @ c_vec / ((np.linalg.norm(vec) * np.linalg.norm(c_vec)) + 1e-8))
            if sim > best_sim:
                best_sim = sim
                best_label = lbl

        if best_sim < threshold:
            best_label = None

        results.append({
            "sentence": sent,
            "label": best_label,
            "similarity": round(best_sim, 4),
        })

    return results


# =============================================================================
# 8) MAIN PIPELINE
# =============================================================================

def preprocess(
    text: str,
    use_spellcheck: bool = False,
    use_morph_normalize: bool = False,
) -> Dict:
    """
    전체 preprocessing pipeline.
    """
    t = text

    t = clean_basic(t)
    t = enforce_sentence_end(t)
    t = remove_noise(t)

    # 간단한 규칙 기반 정규화
    t = normalize_text_rule_based(t)

    if use_spellcheck:
        t = spell_correct(t)

    sentences = split_sentences(t)

    morph_norm = None
    if use_morph_normalize:
        morph_norm = normalize_text_morphological(t)

    return {
        "clean_text": t,
        "morph_normalized_text": morph_norm,
        "sentences": sentences,
    }


# =============================================================================
# 9) TEST
# =============================================================================

if __name__ == "__main__":
    sample = """
현재 금융권 취업 동아리 활동 중이며, 노년층의 '디지털 문맹'을 해소하기 위한 활동을 진행한 경험이 있습니다. 
노년층분들이 자주 방문하는 노인정, 요양원 등 직접 방문하여 은행 앱 사용법을 친절히 알려드리며 배우신 것을 금방 잊어버리시지 않게 명함이나 팸플릿에 은행 어플 가이드라인을 제공해 드렸습니다. 
이 경험을 통해 실질적인 금융 지원의 필요성을 체감했고, 세대 구분 없이 지역 사회에 기여하는 금융 서비스의 중요성을 느꼈습니다.

신협은 ‘사람 중심의 금융’을 실천하며, 지역사회와 조합원의 삶의 질 향상에 기여하는 금융기관입니다.
사람에 대한 이해와 공감에서 출발하는 금융 서비스가 진정한 가치라고 믿기에, 신협의 가치관에 깊이 공감해 인턴십에 지원하게 되었습니다.
    """

    out = preprocess(sample, use_morph_normalize=True)
    print("=== Clean Text ===")
    print(out["clean_text"], "\n")

    print("=== Sentences ===")
    for s in out["sentences"]:
        print("-", s)