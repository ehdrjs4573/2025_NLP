import json
from collections import defaultdict

def extract_keywords(text):
    """
    아주 단순한 키워드 추출 (나중에 NLP로 강화 가능)
    - 쉼표 기준 분리
    - '필요합니다', '있습니다' 같은 조사 제거 가능
    """
    if not text:
        return []
    parts = text.replace("·", ",").replace("/", ",").split(",")
    return [p.strip() for p in parts if len(p.strip()) > 1]


def build_profiles():
    with open("career_job_details.json", "r", encoding="utf-8") as f:
        details = json.load(f)

    profiles = []

    for item in details:

        base = item.get("baseInfo", {})

        job_name = base.get("job_nm") or item.get("job_nm")
        job_cd   = base.get("job_cd")
        category = base.get("aptit_name")

        # --- main abilities ---
        main_abilities = set()

        # 1) abilityList
        for a in item.get("abilityList", []):
            if a and a.get("ability_name"):
                main_abilities.add(a["ability_name"])

        # 2) aptitudeList (문장 → 키워드)
        for a in item.get("aptitudeList", []):
            kws = extract_keywords(a.get("aptitude", ""))
            for k in kws:
                main_abilities.add(k)

        # 3) interestList
        for it in item.get("interestList", []):
            kws = extract_keywords(it.get("interest", ""))
            for k in kws:
                main_abilities.add(k)

        # --- detailed performs (skills) ---
        performs_raw = item.get("performList", {}).get("perform", [])
        skills = []
        for p in performs_raw or []:
            name = p.get("perform")
            importance = p.get("importance")
            if name:
                skills.append({"name": name, "importance": importance})
                # 중요도가 높으면 메인역량에 승격
                if importance and importance >= 85:
                    main_abilities.add(name)

        # --- knowledge ---
        knowledge_raw = item.get("performList", {}).get("knowledge", [])
        knowledge = []
        for k in knowledge_raw or []:
            name = k.get("knowledge")
            importance = k.get("importance")
            if name:
                knowledge.append({"name": name, "importance": importance})

        profiles.append({
            "job_nm": job_name,
            "job_cd": job_cd,
            "category": category,
            "main_abilities": list(main_abilities),
            "skills": skills,
            "knowledge": knowledge,
        })

    # save result
    with open("job_skill_profile.json", "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)

    print("✔ job_skill_profile.json 생성 완료!")


if __name__ == "__main__":
    build_profiles()