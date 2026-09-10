"""Crawl FIT NEU curriculum/course tables from official major pages."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data" / "raw" / "courses.json"
MAJOR_URLS = [
    "https://fit.neu.edu.vn/major/cong-nghe-thong-tin-7480201",
    "https://fit.neu.edu.vn/major/ky-thuat-phan-mem-EP17",
    "https://fit.neu.edu.vn/major/khoa-hoc-may-tinh-7480101",
    "https://fit.neu.edu.vn/major/an-toan-thong-tin-7480202",
    "https://fit.neu.edu.vn/major/cong-nghe-thong-tin-va-chuyen-doi-so-clc-7480201",
]
MAJOR_NAMES = {
    "cong-nghe-thong-tin-7480201": "Công nghệ thông tin",
    "ky-thuat-phan-mem-EP17": "Kỹ thuật phần mềm",
    "khoa-hoc-may-tinh-7480101": "Khoa học máy tính",
    "an-toan-thong-tin-7480202": "An toàn thông tin",
    "cong-nghe-thong-tin-va-chuyen-doi-so-clc-7480201": "CNTT và Chuyển đổi số CLC",
}


def _cell_text(cell) -> str:
    return " ".join(cell.get_text(" ", strip=True).split())


def parse_major_page(html: str, url: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    major_name = MAJOR_NAMES.get(slug, slug)
    rows: list[dict] = []
    for table_index, table in enumerate(soup.find_all("table")):
        headers = [_cell_text(x) for x in table.find_all("th")]
        for tr in table.find_all("tr"):
            cells = [_cell_text(x) for x in tr.find_all(["td", "th"])]
            if len(cells) < 5 or cells == headers:
                continue
            # FIT curriculum tables use: global order, group order, name, code,
            # credits, semester allocation... Group/header rows have no code.
            course_name = cells[2].strip()
            course_code = cells[3].strip().upper()
            credits = cells[4].strip()
            if not course_name or not re.fullmatch(r"[A-ZĐ]{2,}[A-Z0-9.-]{2,}", course_code):
                continue
            rows.append({
                "major_name": major_name,
                "major_url": url,
                "table_index": table_index,
                "course_name": course_name,
                "course_code": course_code,
                "credits": credits if re.fullmatch(r"\d+(?:\.\d+)?", credits) else "",
                "raw_cells": cells,
            })
    return rows


def crawl(urls: list[str] | None = None) -> list[dict]:
    results: list[dict] = []
    for url in urls or MAJOR_URLS:
        response = requests.get(url, timeout=60, headers={"User-Agent": "KLTN-data-pipeline/1.0"})
        response.raise_for_status()
        results.extend(parse_major_page(response.text, url))
    payload = {"source": "FIT NEU official major pages", "crawled_at": datetime.now(timezone.utc).isoformat(), "courses": results}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Crawled {len(results)} curriculum rows -> {OUTPUT}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", action="append", default=[])
    args = parser.parse_args()
    crawl(args.url or None)
