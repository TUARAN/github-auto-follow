#!/usr/bin/env python3
"""每日热门/趋势仓库采集脚本（供 GitHub Actions cron 或本地调用）。

仅依赖 requests，不引入后端的 FastAPI 依赖。
从 GitHub Trending 页面和 GitHub Search API 收集公开热门仓库，
写入 data/trending/YYYY-MM-DD.json，并维护 index.json。

本脚本只做只读采集：不会调用 GitHub Star API（/user/starred），
也不会关注任何用户。

环境变量：
  DIGEST_TOKEN / GITHUB_TOKEN / GH_TOKEN
                    选填，用于提高 Search API 速率限制（只读即可）
  DIGEST_LIMIT      选填，清单条数，默认 30，限制在 20–50
  DIGEST_RETENTION_DAYS
                    选填，保留最近几天的清单，默认 14
  DIGEST_DATA_DIR   选填，输出目录，默认仓库下 data/trending
  DIGEST_DATE       选填，清单日期 YYYY-MM-DD（默认 Asia/Shanghai 当天）
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Optional
from zoneinfo import ZoneInfo

import requests

GITHUB_API = "https://api.github.com"
TRENDING_URL = "https://github.com/trending"
TIMEOUT = 20
TZ = ZoneInfo("Asia/Shanghai")
MIN_LIMIT = 20
MAX_LIMIT = 50
DEFAULT_LIMIT = 30
DEFAULT_RETENTION_DAYS = 14
REPO_ROOT = Path(__file__).resolve().parent.parent

ARTICLE_RE = re.compile(r'<article class="Box-row"[^>]*>(.*?)</article>', re.S)
HREF_RE = re.compile(r'<h2[^>]*>\s*<a[^>]*href="(/[^/]+/[^"/]+)"', re.S)
DESC_RE = re.compile(r'<p class="[^"]*color-fg-muted[^"]*">\s*(.*?)\s*</p>', re.S)
LANG_RE = re.compile(r'<span itemprop="programmingLanguage">\s*([^<]+)\s*</span>')
STARS_RE = re.compile(r'href="[^"]+/stargazers"[^>]*>\s*([0-9,]+)\s*<')
PERIOD_RE = re.compile(r'([0-9,]+)\s+stars\s+(today|this week|this month)', re.I)
TAG_RE = re.compile(r"<[^>]+>")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def today_in_shanghai(now: Optional[datetime] = None) -> str:
    current = now or datetime.now(TZ)
    if current.tzinfo is None:
        current = current.replace(tzinfo=TZ)
    return current.astimezone(TZ).date().isoformat()


def clamp_limit(value: int) -> int:
    return max(MIN_LIMIT, min(MAX_LIMIT, int(value)))


def parse_int(text: str, default: int = 0) -> int:
    digits = re.sub(r"[^0-9]", "", text or "")
    return int(digits) if digits else default


def clean_text(text: str) -> str:
    return html_lib.unescape(TAG_RE.sub("", text or "")).strip()


def parse_trending_html(page_html: str, period_label: str) -> List[dict]:
    """从 GitHub Trending 页面 HTML 解析仓库列表。忽略登录/Star 按钮链接。"""
    repos: List[dict] = []
    seen = set()
    for article in ARTICLE_RE.findall(page_html or ""):
        href_match = HREF_RE.search(article)
        if not href_match:
            continue
        path = href_match.group(1).strip("/")
        parts = path.split("/")
        if len(parts) != 2 or path.startswith("login"):
            continue
        full_name = f"{parts[0]}/{parts[1]}"
        if full_name in seen:
            continue
        seen.add(full_name)

        desc_match = DESC_RE.search(article)
        lang_match = LANG_RE.search(article)
        stars_match = STARS_RE.search(article)
        period_match = PERIOD_RE.search(article)
        period_stars = parse_int(period_match.group(1)) if period_match else 0
        reason = period_label
        if period_stars:
            if "今日" in period_label:
                reason = f"{period_label}，当天新增 {period_stars} star"
            elif "本周" in period_label:
                reason = f"{period_label}，本周新增 {period_stars} star"
            elif "本月" in period_label:
                reason = f"{period_label}，本月新增 {period_stars} star"

        repos.append({
            "full_name": full_name,
            "description": clean_text(desc_match.group(1)) if desc_match else "",
            "language": clean_text(lang_match.group(1)) if lang_match else "",
            "stars": parse_int(stars_match.group(1)) if stars_match else 0,
            "url": f"https://github.com/{full_name}",
            "reason": reason,
        })
    return repos


def build_session(token: Optional[str] = None) -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "github-auto-follow-digest",
    })
    if token:
        session.headers["Authorization"] = f"token {token}"
    return session


def resolve_token() -> Optional[str]:
    for key in ("DIGEST_TOKEN", "GITHUB_TOKEN", "GH_TOKEN"):
        value = os.getenv(key, "").strip()
        if value:
            return value
    return None


def fetch_trending(session: requests.Session, since: str, reason: str) -> List[dict]:
    try:
        response = session.get(
            TRENDING_URL,
            params={"since": since},
            headers={"Accept": "text/html,application/xhtml+xml"},
            timeout=TIMEOUT,
        )
        if response.status_code != 200:
            print(f"::warning::获取 GitHub Trending（{since}）失败：HTTP {response.status_code}")
            return []
        return parse_trending_html(response.text, reason)
    except requests.RequestException as exc:
        print(f"::warning::获取 GitHub Trending（{since}）出错：{exc}")
        return []


def search_new_popular(session: requests.Session, today: str, days: int, per_page: int) -> List[dict]:
    start = (datetime.fromisoformat(today) - timedelta(days=days)).date().isoformat()
    query = f"created:>{start} stars:>20 archived:false fork:false"
    try:
        response = session.get(
            f"{GITHUB_API}/search/repositories",
            params={
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": min(per_page, 50),
            },
            timeout=TIMEOUT,
        )
        if response.status_code != 200:
            print(f"::warning::Search API 失败：HTTP {response.status_code}")
            return []
        items = []
        for repo in response.json().get("items", []):
            full_name = repo.get("full_name") or ""
            if not full_name or repo.get("private"):
                continue
            items.append({
                "full_name": full_name,
                "description": (repo.get("description") or "").strip(),
                "language": repo.get("language") or "",
                "stars": int(repo.get("stargazers_count") or 0),
                "url": repo.get("html_url") or f"https://github.com/{full_name}",
                "reason": f"近 {days} 日新建仓库，星标较多",
            })
        return items
    except requests.RequestException as exc:
        print(f"::warning::Search API 出错：{exc}")
        return []


def enrich_repo(session: requests.Session, item: dict) -> dict:
    """用仓库 API 补全语言、简介和 star 数；失败时保留已有字段。"""
    full_name = item.get("full_name") or ""
    if not full_name:
        return item
    try:
        response = session.get(f"{GITHUB_API}/repos/{full_name}", timeout=TIMEOUT)
        if response.status_code != 200:
            return item
        data = response.json()
        if data.get("private"):
            return item
        item["description"] = (data.get("description") or item.get("description") or "").strip()
        item["language"] = data.get("language") or item.get("language") or ""
        item["stars"] = int(data.get("stargazers_count") or item.get("stars") or 0)
        item["url"] = data.get("html_url") or item.get("url") or f"https://github.com/{full_name}"
    except requests.RequestException:
        return item
    return item


def merge_repos(groups: Iterable[List[dict]], limit: int) -> List[dict]:
    merged: List[dict] = []
    seen = set()
    for group in groups:
        for item in group:
            name = (item.get("full_name") or "").strip()
            if not name or name in seen:
                continue
            seen.add(name)
            merged.append(item)
            if len(merged) >= limit:
                return merged
    return merged


def collect_digest(session: requests.Session, today: str, limit: int) -> List[dict]:
    daily = fetch_trending(session, "daily", "GitHub 今日趋势")
    weekly = fetch_trending(session, "weekly", "GitHub 本周趋势")
    search = search_new_popular(session, today, days=14, per_page=limit)
    items = merge_repos((daily, weekly, search), limit)
    enriched = [enrich_repo(session, item) for item in items]
    return enriched


def digest_path(data_dir: Path, date: str) -> Path:
    return data_dir / f"{date}.json"


def list_existing_dates(data_dir: Path) -> List[str]:
    if not data_dir.exists():
        return []
    dates = [p.stem for p in data_dir.glob("*.json") if DATE_RE.match(p.stem)]
    dates.sort(reverse=True)
    return dates


def write_index(data_dir: Path, dates: List[str]) -> Path:
    payload = {
        "latest": dates[0] if dates else None,
        "dates": dates,
    }
    path = data_dir / "index.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def prune_old_digests(data_dir: Path, today: str, retention_days: int) -> List[str]:
    cutoff = (datetime.fromisoformat(today) - timedelta(days=retention_days)).date().isoformat()
    kept: List[str] = []
    for date in list_existing_dates(data_dir):
        if date < cutoff:
            digest_path(data_dir, date).unlink(missing_ok=True)
            print(f"已删除过期清单 {date}.json")
        else:
            kept.append(date)
    return kept


def write_digest(data_dir: Path, date: str, items: List[dict], sources: List[str]) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "date": date,
        "generated_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "timezone": "Asia/Shanghai",
        "sources": sources,
        "count": len(items),
        "items": [
            {
                "full_name": item.get("full_name") or "",
                "description": item.get("description") or "",
                "language": item.get("language") or "",
                "stars": int(item.get("stars") or 0),
                "url": item.get("url") or "",
                "reason": item.get("reason") or "",
            }
            for item in items
        ],
    }
    path = digest_path(data_dir, date)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def build_digest(data_dir: Path, date: str, limit: int, retention_days: int, token: Optional[str]) -> dict:
    session = build_session(token)
    items = collect_digest(session, date, limit)
    sources = ["github-trending-daily", "github-trending-weekly", "github-search-new"]
    path = write_digest(data_dir, date, items, sources)
    dates = prune_old_digests(data_dir, date, retention_days)
    if date not in dates:
        dates = [date] + dates
        dates.sort(reverse=True)
    write_index(data_dir, dates)
    print(f"已写入 {path}（{len(items)} 条）")
    if len(items) < MIN_LIMIT:
        print(f"::warning::清单只有 {len(items)} 条，低于建议下限 {MIN_LIMIT}")
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="采集每日热门/趋势 GitHub 仓库清单（只读，不会点 star）")
    parser.add_argument("--limit", type=int, default=None, help="清单条数，默认 30，范围 20–50")
    parser.add_argument("--data-dir", default=None, help="输出目录，默认 data/trending")
    parser.add_argument("--date", default=None, help="清单日期 YYYY-MM-DD，默认北京时间当天")
    parser.add_argument("--retention-days", type=int, default=None, help="保留天数，默认 14")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    date = args.date or os.getenv("DIGEST_DATE") or today_in_shanghai()
    if not DATE_RE.match(date):
        print(f"::error::无效日期：{date}")
        return 1
    limit = clamp_limit(args.limit if args.limit is not None else int(os.getenv("DIGEST_LIMIT", str(DEFAULT_LIMIT))))
    retention = args.retention_days if args.retention_days is not None else int(
        os.getenv("DIGEST_RETENTION_DAYS", str(DEFAULT_RETENTION_DAYS))
    )
    data_dir = Path(args.data_dir or os.getenv("DIGEST_DATA_DIR") or (REPO_ROOT / "data" / "trending"))
    if not data_dir.is_absolute():
        data_dir = (Path.cwd() / data_dir).resolve()

    token = resolve_token()
    if token:
        print("已使用 token 访问 GitHub API（只读采集，提高速率限制）。")
    else:
        print("未提供 token，将以未认证方式访问 GitHub API（速率限制更低）。")

    digest = build_digest(data_dir, date, limit, retention, token)
    print(f"日期 {digest['date']}，共 {digest['count']} 个仓库。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
