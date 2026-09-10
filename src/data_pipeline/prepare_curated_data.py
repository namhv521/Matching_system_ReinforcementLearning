"""Build versioned, auditable ML-ready data without mutating raw inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.crawler.skill_extractor import SKILL_TAXONOMY, _extract_year, _time_weight
from src.data_pipeline.identity import AdvisorResolver, advisor_key, clean_text, display_name, split_title_name

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
CURATED = ROOT / "data" / "curated"

ROLE_RULES = {
    "frontend": ["react", "vue", "angular", "html", "css", "frontend", "giao diện"],
    "backend": ["django", "flask", "spring", "node", "express", "asp.net", "backend", "api", "microservice"],
    "mobile": ["flutter", "android", "ios", "react native", "mobile", "di động"],
    "data_ai": ["machine learning", "học máy", "deep learning", "học sâu", "ai", "llm", "rag", "nlp", "dữ liệu"],
    "game_graphics": ["unity", "unreal", "game", "trò chơi", "đồ họa", "vr", "ar"],
    "security_cloud": ["security", "bảo mật", "an toàn thông tin", "cloud", "blockchain", "mật mã"],
    "iot_embedded": ["iot", "nhúng", "arduino", "raspberry", "cảm biến", "vi điều khiển"],
    "research": ["nghiên cứu", "thuật toán", "mô hình", "thực nghiệm", "đánh giá"],
}


def _stable_id(prefix: str, value: str) -> str:
    return f"{prefix}-{hashlib.sha1(value.encode('utf-8')).hexdigest()[:16]}"


def _profile_title_name(profile: dict) -> tuple[str, str]:
    title = clean_text(profile.get("title"))
    name = clean_text(profile.get("name"))
    slug = clean_text(profile.get("slug"))
    slug_title, slug_name = split_title_name(slug.replace("-", " "), title)
    # Prefer accented page name, but repair legacy unaccented records from historical thesis names later.
    normalized_name = name or slug_name
    return title or slug_title, normalized_name.title()


def build_roster(profiles: list[dict], thesis_names: list[str]) -> list[dict]:
    historical: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for raw_name in thesis_names:
        title, name = split_title_name(raw_name)
        historical[advisor_key(name)].append((title, name))

    roster = []
    seen = set()
    for profile in profiles:
        if profile.get("slug") in {"lecturer", "lecturer-1"}:
            continue
        title, name = _profile_title_name(profile)
        key = advisor_key(name)
        if not key or key in seen:
            continue
        seen.add(key)
        # If the crawled legacy profile lost accents, recover the most frequent accented spelling.
        candidates = historical.get(key, [])
        accented = [item for item in candidates if any(ord(ch) > 127 for ch in item[1])]
        if accented and not any(ord(ch) > 127 for ch in name):
            title2, name2 = Counter(accented).most_common(1)[0][0]
            name, title = name2, title or title2
        roster.append({
            "advisor_id": profile.get("slug") or _stable_id("advisor", key),
            "canonical_name": display_name(title, name),
            "academic_title": title,
            "name": name,
            "profile_url": profile.get("profile_url", ""),
            "email": profile.get("email", ""),
            "department": profile.get("department", "Khoa Công nghệ thông tin"),
        })
    return roster


def _matches(text: str, keywords: list[str]) -> list[str]:
    lowered = text.lower()
    return sorted({kw for kw in keywords if kw.lower() in lowered})


def build_advisor_evidence(profiles: list[dict], roster: list[dict], theses: pd.DataFrame) -> pd.DataFrame:
    roster_by_id = {r["advisor_id"]: r for r in roster}
    rows = []
    for profile in profiles:
        advisor_id = profile.get("slug")
        if advisor_id not in roster_by_id:
            continue
        sources = {
            "research_area": profile.get("research_areas_raw", []),
            "teaching": profile.get("teaching_raw", []),
            "publication": profile.get("publications_raw", []),
        }
        supervised = theses.loc[theses["advisor_id"].eq(advisor_id), "thesis_title"].dropna().astype(str).tolist()
        sources["supervised_thesis"] = supervised
        for skill, keywords in SKILL_TAXONOMY.items():
            evidence = []
            score = 0.0
            for source, items in sources.items():
                for item in items:
                    hits = _matches(item, keywords)
                    if not hits:
                        continue
                    year = _extract_year(item) if source == "publication" else None
                    # Publications/research are stronger evidence; supervised theses are supporting evidence only.
                    weight = {"publication": 1.0, "research_area": 0.8, "teaching": 0.6, "supervised_thesis": 0.25}[source]
                    if source == "publication":
                        weight *= _time_weight(year)
                    score += weight
                    evidence.append({"source": source, "text": clean_text(item)[:500], "matched": hits, "year": year, "weight": round(weight, 3)})
            if evidence:
                rows.append({
                    "advisor_id": advisor_id,
                    "canonical_name": roster_by_id[advisor_id]["canonical_name"],
                    "skill": skill,
                    "skill_score": round(min(10.0, score), 3),
                    "publication_evidence_count": sum(e["source"] == "publication" for e in evidence),
                    "evidence_count": len(evidence),
                    "evidence_json": json.dumps(evidence, ensure_ascii=False),
                })
    return pd.DataFrame(rows)


def assign_student_roles(row: pd.Series) -> tuple[str, str]:
    text = " | ".join(clean_text(v) for v in row.values if clean_text(v))
    scores = {role: len(_matches(text, keywords)) for role, keywords in ROLE_RULES.items()}
    ranked = sorted(scores, key=lambda role: (-scores[role], role))
    positive = [r for r in ranked if scores[r] > 0]
    primary = positive[0] if positive else "generalist"
    secondary = ",".join(positive[1:3])
    return primary, secondary


def run() -> dict:
    CURATED.mkdir(parents=True, exist_ok=True)
    thesis = pd.read_csv(PROCESSED / "thesis_extracted.csv", encoding="utf-8-sig")
    profiles = json.loads((RAW / "lecturers_raw.json").read_text(encoding="utf-8"))
    supplements_path = ROOT / "configs" / "lecturer_supplements.json"
    if supplements_path.exists():
        supplements = json.loads(supplements_path.read_text(encoding="utf-8"))
        existing_slugs = {p.get("slug") for p in profiles}
        profiles.extend(p for p in supplements if p.get("slug") not in existing_slugs)
    profiles = [p for p in profiles if "error" not in p]
    thesis["advisor_name_raw"] = thesis["advisor_name"].map(clean_text)
    roster = build_roster(profiles, thesis["advisor_name_raw"].tolist())
    resolver = AdvisorResolver(roster)
    matches = thesis["advisor_name_raw"].map(resolver.resolve)
    thesis["advisor_id"] = matches.map(lambda m: m.advisor_id)
    thesis["advisor_name"] = matches.map(lambda m: m.canonical_name)
    thesis["advisor_match_method"] = matches.map(lambda m: m.method)
    thesis["advisor_match_score"] = matches.map(lambda m: m.score)

    usable = thesis["extraction_status"].fillna("").str.lower().eq("success")
    usable &= thesis["thesis_title"].fillna("").astype(str).str.strip().ne("")
    usable &= thesis["advisor_id"].notna()
    curated_theses = thesis[usable].copy()
    curated_theses["student_id"] = curated_theses["student_id"].astype(str).str.replace(r"\.0$", "", regex=True)
    role_cols = [c for c in curated_theses.columns if c not in {"source_file", "extraction_notes"}]
    roles = curated_theses[role_cols].apply(assign_student_roles, axis=1)
    curated_theses["primary_role"] = roles.map(lambda x: x[0])
    curated_theses["secondary_roles"] = roles.map(lambda x: x[1])
    curated_theses["record_id"] = curated_theses.apply(lambda r: _stable_id("thesis", f"{r.get('source_file','')}|{r.name}"), axis=1)

    roster_df = pd.DataFrame(roster)
    evidence_df = build_advisor_evidence(profiles, roster, curated_theses)
    identity_df = pd.DataFrame({
        "source_name": thesis["advisor_name_raw"],
        "advisor_id": thesis["advisor_id"],
        "canonical_name": thesis["advisor_name"],
        "match_method": thesis["advisor_match_method"],
        "match_score": thesis["advisor_match_score"],
    }).drop_duplicates().sort_values(["canonical_name", "source_name"], na_position="last")

    roster_df.to_csv(CURATED / "lecturers.csv", index=False, encoding="utf-8-sig")
    curated_theses.to_csv(CURATED / "theses.csv", index=False, encoding="utf-8-sig")
    curated_theses[["student_id", "student_name", "primary_role", "secondary_roles", "field_category", "record_id"]].to_csv(
        CURATED / "student_profiles.csv", index=False, encoding="utf-8-sig")
    evidence_df.to_csv(CURATED / "advisor_skill_evidence.csv", index=False, encoding="utf-8-sig")
    identity_df.to_csv(CURATED / "advisor_identity_map.csv", index=False, encoding="utf-8-sig")

    courses_path = RAW / "courses.json"
    course_count = 0
    if courses_path.exists():
        courses = json.loads(courses_path.read_text(encoding="utf-8")).get("courses", [])
        pd.DataFrame(courses).to_csv(CURATED / "courses.csv", index=False, encoding="utf-8-sig")
        course_count = len(courses)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_thesis_rows": len(thesis),
        "curated_thesis_rows": len(curated_theses),
        "lecturer_count": len(roster_df),
        "course_rows": course_count,
        "advisor_skill_rows": len(evidence_df),
        "unmatched_advisor_rows": int(thesis["advisor_id"].isna().sum()),
        "missing_advisor_success_rows": int((thesis["advisor_name_raw"].eq("") & thesis["extraction_status"].fillna("").str.lower().eq("success")).sum()),
        "unmatched_named_success_rows": int((thesis["advisor_id"].isna() & thesis["advisor_name_raw"].ne("") & thesis["extraction_status"].fillna("").str.lower().eq("success")).sum()),
        "fuzzy_matched_rows": int(thesis["advisor_match_method"].eq("fuzzy").sum()),
        "advisor_source_name_variants": int(thesis.loc[thesis["advisor_id"].notna(), "advisor_name_raw"].nunique()),
        "advisor_canonical_used": int(thesis.loc[thesis["advisor_id"].notna(), "advisor_id"].nunique()),
        "role_distribution": curated_theses["primary_role"].value_counts().to_dict(),
        "outputs": [p.name for p in sorted(CURATED.glob("*.csv"))],
    }
    (CURATED / "quality_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    argparse.ArgumentParser().parse_args()
    run()
