"""
embedding.py

SBERT 기반 한국어 문장/문서 임베딩 유틸 모듈.

- 한국어 문장을 kss로 분리
- Sentence-BERT(ko-sroberta-multitask) 로드 (lazy loading)
- 문장 리스트 → 임베딩 벡터 (numpy array)
- 문서 전체 임베딩 = 문장 임베딩 평균

이 모듈은 프로젝트 전체 NLP 분석의 '벡터 뇌' 역할
"""

from __future__ import annotations

from typing import List, Tuple, Optional

import numpy as np
import kss
from sentence_transformers import SentenceTransformer

# 내부 전역 모델 (lazy loading)

_MODEL: Optional[SentenceTransformer] = None

DEFAULT_MODEL_NAME = "jhgan/ko-sroberta-multitask"


def get_sbert_model(model_name: str = DEFAULT_MODEL_NAME) -> SentenceTransformer:
    """
    전역 SentenceTransformer 모델을 lazy-loading 방식으로 반환.
    여러 모듈에서 호출해도 실제로는 한 번만 로드되도록 한다.
    """
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(model_name)
    return _MODEL


# 문장 분리 & 전처리

def split_sentences_ko(text: str) -> List[str]:
    """
    한국어 문단을 문장 단위로 분리.

    - kss를 사용해 문장 분리
    - 공백/개행만 있는 문장은 제거
    """
    if not text:
        return []

    # kss가 개행 기준도 처리하므로 굳이 미리 나눌 필요는 없음
    sents = kss.split_sentences(text)
    sents = [s.strip() for s in sents if s and s.strip()]

    return sents

# 임베딩 관련 함수

def embed_sentences(
    sentences: List[str],
    model_name: str = DEFAULT_MODEL_NAME,
    to_numpy: bool = True,
) -> np.ndarray:
    """
    문장 리스트를 SBERT 임베딩으로 변환.

    Parameters
    ----------
    sentences : List[str]
        임베딩할 문장 리스트.
    model_name : str
        사용할 SBERT 모델 이름 (기본: ko-sroberta-multitask).
    to_numpy : bool
        True이면 numpy.ndarray를 반환.

    Returns
    -------
    np.ndarray
        shape = (num_sentences, dim)
    """
    if not sentences:
        # 문장이 없으면 (0, 0)짜리 배열 반환
        return np.zeros((0, 0), dtype=np.float32)

    model = get_sbert_model(model_name)
    embs = model.encode(sentences, convert_to_numpy=to_numpy)

    return embs


def embed_document_mean(
    text: str,
    model_name: str = DEFAULT_MODEL_NAME,
) -> Tuple[List[str], Optional[np.ndarray], np.ndarray]:
    """
    문단/자소서 전체 텍스트를 입력받아:

    1) 문장 리스트
    2) 문서 전체 임베딩 (문장 벡터 평균)
    3) 개별 문장 임베딩 배열

    을 반환한다.

    Returns
    -------
    sentences : List[str]
        분리된 문장 리스트.
    doc_vector : Optional[np.ndarray]
        문서 전체 임베딩 벡터 (dim,)  — 문장이 없으면 None.
    sent_embs : np.ndarray
        문장 임베딩 배열 (num_sentences, dim)
    """
    sentences = split_sentences_ko(text)

    if not sentences:
        return [], None, np.zeros((0, 0), dtype=np.float32)

    sent_embs = embed_sentences(sentences, model_name=model_name, to_numpy=True)

    # 문장 벡터들의 평균을 문서 임베딩으로 사용
    doc_vector = sent_embs.mean(axis=0)

    return sentences, doc_vector, sent_embs


def embed_phrases(
    phrases: List[str],
    model_name: str = DEFAULT_MODEL_NAME,
) -> np.ndarray:
    """
    직무/기업 핵심 키워드 등 짧은 phrase 리스트를 임베딩하는 유틸.
    keyword_coverage.py 등에서 재사용하기 좋게 분리해둠.
    """
    if not phrases:
        return np.zeros((0, 0), dtype=np.float32)

    model = get_sbert_model(model_name)
    embs = model.encode(phrases, convert_to_numpy=True)
    return embs


# 간단 테스트용 main (옵션)

if __name__ == "__main__":
    sample_text = (
        "저는 대학 생활 동안 여러 팀 프로젝트를 수행하며 협업의 중요성을 배웠습니다. "
        "특히 캡스톤 디자인에서 팀장을 맡아 일정 관리와 역할 분담을 주도했습니다."
    )

    sents, doc_vec, sent_embs = embed_document_mean(sample_text)
    print("문장 개수:", len(sents))
    for i, s in enumerate(sents):
        print(f"[{i}] {s}")
    print("문서 임베딩 차원:", None if doc_vec is None else doc_vec.shape)