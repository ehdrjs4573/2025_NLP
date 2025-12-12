# selfintro_app/scripts/06_build_company_embeddings_sbert.py

import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "scripts/data"

INPUT_PATH = DATA_DIR / "company_profiles.json"
OUTPUT_PATH = DATA_DIR / "company_profiles_embed.json"

# SBERT 한국어 멀티태스크 모델 (직무 임베딩과 동일 모델 사용)
model = SentenceTransformer("jhgan/ko-sbert-multitask")


def build_company_embeddings():
    print(f"{INPUT_PATH.name} 로드 중...")
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        companies = json.load(f)

    print(f"총 {len(companies)}개 기업 임베딩 생성 시작")

    results = []

    for idx, c in enumerate(companies, start=1):
        cid = c.get("company_id")
        name = c.get("company_name")

        # 하나의 긴 문장으로 병합
        merged_text = (
            f"기업명: {name}. "
            f"산업: {c.get('industry', '')}. "
            f"기업요약: {c.get('summary', '')}. "
            f"핵심가치: {c.get('values', '')}. "
            f"인재상: {c.get('talent', '')}. "
            f"기술키워드: {c.get('tech_keywords', '')}. "
        )

        print(f"[{idx}/{len(companies)}] company_id={cid} SBERT 임베딩 생성 중...")

        embedding = model.encode(merged_text).tolist()

        results.append(
            {
                **c,
                "embedding": embedding,
            }
        )

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"기업 임베딩 생성 완료 → {OUTPUT_PATH}")


if __name__ == "__main__":
    build_company_embeddings()