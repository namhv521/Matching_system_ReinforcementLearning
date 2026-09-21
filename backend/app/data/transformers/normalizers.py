"""Data normalization and sanitization utilities."""
from __future__ import annotations

import json
import math
from typing import Any, Dict, List, Optional
import pandas as pd


def clean_str(val: Any, default: str = "") -> str:
    if val is None or pd.isna(val):
        return default
    s = str(val).strip()
    return default if s.lower() == "nan" else s


def clean_opt_str(val: Any) -> Optional[str]:
    if val is None or pd.isna(val):
        return None
    s = str(val).strip()
    return None if (s.lower() == "nan" or s == "") else s


def clean_int(val: Any, default: int = 0) -> int:
    if val is None or pd.isna(val):
        return default
    try:
        f = float(val)
        return int(f) if not math.isnan(f) else default
    except (ValueError, TypeError):
        return default


def clean_float(val: Any, default: float = 0.0) -> float:
    if val is None or pd.isna(val):
        return default
    try:
        f = float(val)
        return default if math.isnan(f) else f
    except (ValueError, TypeError):
        return default


def clean_opt_float(val: Any) -> Optional[float]:
    if val is None or pd.isna(val):
        return None
    try:
        f = float(val)
        return None if math.isnan(f) else f
    except (ValueError, TypeError):
        return None


def parse_json_safely(val: Any) -> Any:
    if not val or pd.isna(val):
        return []
    if isinstance(val, (list, dict)):
        return val
    try:
        return json.loads(str(val))
    except Exception:
        return []


def extract_tech_stack(row: Dict[str, Any] | pd.Series) -> List[str]:
    keys = ["web_languages", "backend_frameworks", "frontend_frameworks", "ai_frameworks", "database_cache"]
    stack = []
    for k in keys:
        v = row.get(k)
        if v and pd.notna(v) and str(v).strip() and str(v).strip().lower() != "nan":
            parts = [p.strip() for p in str(v).split(",") if p.strip()]
            stack.extend(parts)
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for item in stack:
        if item.lower() not in seen:
            seen.add(item.lower())
            deduped.append(item)
    return deduped
