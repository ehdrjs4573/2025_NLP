import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent / "data"

INPUT_PATH = BASE_DIR / "career_job_vectors.json"
OUTPUT_PATH = BASE_DIR / "career_job_vectors_embed.json"

model = SentenceTransformer("jhgan/ko-sbert-multitask")

def build_embeddings():
    print("career_job_vectors.json 로딩 중")
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    print(f" 총 {len(jobs)}개 직업 임베딩 생성 시작")

    results = []

    for idx, job in enumerate(jobs, start=1):
        job_cd = job.get("job_cd")
        job_nm = job.get("job_nm")

        merged_text = (
            f"직업명: {job_nm}. "
            f"설명: {job.get('work_summary', '')}. "
            f"핵심능력: {', '.join(job.get('main_abilities', []))}. "
            f"스킬: {', '.join(job.get('skills', []))}. "
            f"지식요소: {', '.join(job.get('knowledge', []))}. "
        )

        print(f"[{idx}/{len(jobs)}] job_cd={job_cd} SBERT 임베딩 생성 중...")
        embedding = model.encode(merged_text).tolist()

        results.append({
            **job,
            "embedding": embedding
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"SBERT 임베딩 생성 완료 → {OUTPUT_PATH}")

if __name__ == "__main__":
    build_embeddings()