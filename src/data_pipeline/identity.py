"""Canonical Vietnamese person-name handling for advisor identity resolution."""
from __future__ import annotations

import re
import unicodedata
import math
from dataclasses import dataclass
from difflib import SequenceMatcher


TITLE_PATTERNS = (
    ("GS.TS", r"\b(?:gs\s*\.?\s*ts|giao\s+su\s+tien\s+si)\b"),
    ("PGS.TS", r"\b(?:pgs\s*\.?\s*ts|pho\s+giao\s+su\s+tien\s+si)\b"),
    ("PGS", r"\b(?:pgs|pho\s+giao\s+su)\b"),
    ("TS", r"\b(?:ts|tien\s+si)\b"),
    ("ThS", r"\b(?:ths|th\s*\.?\s*s|thac\s+si)\b"),
    ("CN", r"\b(?:cn|cu\s+nhan)\b"),
)


def clean_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return " ".join(str(value).replace("\u200b", " ").split()).strip()


def ascii_words(value: object) -> str:
    text = unicodedata.normalize("NFKD", clean_text(value)).lower()
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("đ", "d")
    return " ".join(re.findall(r"[a-z0-9]+", text))


def split_title_name(value: object, fallback_title: str = "") -> tuple[str, str]:
    raw = clean_text(value)
    folded = ascii_words(raw)
    title = clean_text(fallback_title)
    for canonical, pattern in TITLE_PATTERNS:
        if re.search(pattern, folded):
            title = canonical
            folded = re.sub(pattern, " ", folded)
            break
    # Remove common role labels that are not academic titles.
    folded = re.sub(r"\b(?:gv|giang vien|truong khoa|pho khoa)\b", " ", folded)
    key = "".join(folded.split())

    # Preserve Vietnamese spelling from the source by removing a leading title only.
    name = raw
    name = re.sub(
        r"^\s*(?:(?:PGS|GS)\s*\.?\s*)?(?:TS|Th\s*\.?\s*S|ThS|CN|NCS|Tiến\s+sĩ|Thạc\s+sĩ|Cử\s+nhân)\s*\.?\s*",
        "", name, flags=re.IGNORECASE,
    ).strip(" .,-")
    return title, name if name else key


def advisor_key(value: object) -> str:
    _, name = split_title_name(value)
    return "".join(ascii_words(name).split())


def display_name(title: str, name: str) -> str:
    return f"{clean_text(title)} {clean_text(name)}".strip()


@dataclass(frozen=True)
class Match:
    source_name: str
    advisor_id: str | None
    canonical_name: str | None
    method: str
    score: float


class AdvisorResolver:
    """Resolve noisy advisor strings against an authoritative FIT roster."""

    def __init__(self, roster: list[dict], aliases: dict[str, str] | None = None):
        self.roster = roster
        self.by_key = {advisor_key(r["canonical_name"]): r for r in roster}
        self.aliases = {advisor_key(k): advisor_key(v) for k, v in (aliases or {}).items()}

    def resolve(self, value: object) -> Match:
        source = clean_text(value)
        key = advisor_key(source)
        if not key:
            return Match(source, None, None, "empty", 0.0)
        key = self.aliases.get(key, key)
        if key in self.by_key:
            row = self.by_key[key]
            return Match(source, row["advisor_id"], row["canonical_name"], "exact_normalized", 1.0)

        scores = sorted(
            ((SequenceMatcher(None, key, candidate).ratio(), candidate) for candidate in self.by_key),
            reverse=True,
        )
        if not scores:
            return Match(source, None, None, "unmatched", 0.0)
        best_score, best_key = scores[0]
        second = scores[1][0] if len(scores) > 1 else 0.0
        # Conservative fuzzy match: high similarity and a useful margin over runner-up.
        if best_score >= 0.88 and best_score - second >= 0.05:
            row = self.by_key[best_key]
            return Match(source, row["advisor_id"], row["canonical_name"], "fuzzy", round(best_score, 4))
        return Match(source, None, None, "unmatched", round(best_score, 4))
