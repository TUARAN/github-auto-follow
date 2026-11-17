"""只读读取已采集的每日热门仓库清单，供 API 展示。

数据由 scripts/daily_trending.py 写入 data/trending/。
本模块不会调用 GitHub Star / Follow API。
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = REPO_ROOT / "data" / "trending"
DEFAULT_FALLBACK = "https://raw.githubusercontent.com/TUARAN/github-auto-follow/main/data/trending"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIMEOUT = 10


def data_dir() -> Path:
    raw = os.getenv("TRENDING_DATA_DIR")
    if raw:
        path = Path(raw)
        return path if path.is_absolute() else (Path.cwd() / path).resolve()
    return DEFAULT_DATA_DIR


def fallback_base() -> Optional[str]:
    value = os.getenv("TRENDING_FALLBACK_URL", DEFAULT_FALLBACK).strip()
    return value.rstrip("/") if value else None


def is_valid_date(value: str) -> bool:
    return bool(value) and bool(DATE_RE.match(value))


def _read_json_file(path: Path) -> Optional[dict]:
    if not path.is_file():
        return None
    try:
        import json
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _fetch_json(url: str) -> Optional[dict]:
    try:
        response = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "github-auto-follow-digest"})
        if response.status_code != 200:
            return None
        return response.json()
    except (requests.RequestException, ValueError):
        return None


def load_index() -> dict:
    local = _read_json_file(data_dir() / "index.json")
    if local and isinstance(local.get("dates"), list):
        dates = [d for d in local.get("dates") or [] if is_valid_date(str(d))]
        latest = local.get("latest") if is_valid_date(str(local.get("latest") or "")) else (dates[0] if dates else None)
        return {"latest": latest, "dates": dates}

    dates = sorted(
        (p.stem for p in data_dir().glob("*.json") if is_valid_date(p.stem)),
        reverse=True,
    )
    if dates:
        return {"latest": dates[0], "dates": dates}

    base = fallback_base()
    if base:
        remote = _fetch_json(f"{base}/index.json")
        if remote and isinstance(remote.get("dates"), list):
            dates = [d for d in remote.get("dates") or [] if is_valid_date(str(d))]
            latest = remote.get("latest") if is_valid_date(str(remote.get("latest") or "")) else (dates[0] if dates else None)
            return {"latest": latest, "dates": dates}

    return {"latest": None, "dates": []}


def load_digest(date: Optional[str] = None) -> Optional[dict]:
    index = load_index()
    target = date or index.get("latest")
    if not target or not is_valid_date(str(target)):
        return None

    local = _read_json_file(data_dir() / f"{target}.json")
    if local and isinstance(local.get("items"), list):
        return _normalize_digest(local, index)

    base = fallback_base()
    if base:
        remote = _fetch_json(f"{base}/{target}.json")
        if remote and isinstance(remote.get("items"), list):
            return _normalize_digest(remote, index)

    return None


def _normalize_digest(payload: dict, index: dict) -> dict:
    items = []
    for raw in payload.get("items") or []:
        if not isinstance(raw, dict):
            continue
        full_name = (raw.get("full_name") or "").strip()
        if not full_name:
            continue
        items.append({
            "full_name": full_name,
            "description": raw.get("description") or "",
            "language": raw.get("language") or "",
            "stars": int(raw.get("stars") or 0),
            "url": raw.get("url") or f"https://github.com/{full_name}",
            "reason": raw.get("reason") or "",
        })
    return {
        "date": payload.get("date"),
        "generated_at": payload.get("generated_at"),
        "timezone": payload.get("timezone") or "Asia/Shanghai",
        "sources": payload.get("sources") or [],
        "count": len(items),
        "items": items,
        "dates": index.get("dates") or [],
        "latest": index.get("latest"),
    }
