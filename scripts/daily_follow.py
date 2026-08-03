#!/usr/bin/env python3
"""每日定时关注脚本（供 GitHub Actions cron 调用）。

仅依赖 requests，自带「推荐 + 关注」逻辑，不引入后端的 FastAPI 依赖。
GitHub 本身就是「已关注谁」的唯一事实来源，因此脚本无状态：
每次运行都重新拉取关注列表并过滤，重复运行幂等、不会重复关注。

本次关注人数在 [FOLLOW_MIN, FOLLOW_MAX] 间随机；定时工作流默认每批 10 人。
接近 API 速率限制
（剩余配额低于 RATE_LIMIT_FLOOR）或遇到二级限流（403）时，提前停止。

环境变量：
  FOLLOW_TOKEN      必填，具有 user:follow 权限的 Personal Access Token
  FOLLOW_MIN        选填，单次关注人数下限（默认 10）
  FOLLOW_MAX        选填，单次关注人数上限（默认 10）
  RATE_LIMIT_FLOOR  选填，剩余配额低于此值即停止（默认 200）
"""
import os
import sys
import time
import random
import requests
from datetime import datetime, timedelta

GITHUB_API = "https://api.github.com"
TIMEOUT = 10

SEARCH_QUERIES = [
    "type:user repos:>0",
    "type:user language:python",
    "type:user language:javascript",
    "type:user language:go",
    "type:user language:rust",
    "type:user language:java",
    "type:user created:>2020-01-01",
    "type:user created:>2022-01-01",
]

REPOSITORY_QUERIES = [
    "archived:false mirror:false language:python",
    "archived:false mirror:false language:javascript",
    "archived:false mirror:false language:typescript",
    "archived:false mirror:false language:go",
    "archived:false mirror:false language:rust",
    "archived:false mirror:false topic:cli",
    "archived:false mirror:false topic:web",
    "archived:false mirror:false topic:ai",
]


def session(token: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    return s


def current_login(s: requests.Session) -> str:
    r = s.get(f"{GITHUB_API}/user", timeout=TIMEOUT)
    if r.status_code != 200:
        raise SystemExit(f"Token 无效或权限不足 (HTTP {r.status_code})")
    return r.json()["login"]


def following_set(s: requests.Session) -> set:
    """拉取当前已关注的人（最多翻 5 页 / 500 人，足够用于去重）。"""
    logins = set()
    for page in range(1, 6):
        r = s.get(f"{GITHUB_API}/user/following",
                  params={"per_page": 100, "page": page}, timeout=TIMEOUT)
        if r.status_code != 200:
            break
        batch = r.json()
        logins.update(u["login"] for u in batch)
        if len(batch) < 100:
            break
    return logins


def allowed_candidate(login: str, seen: set) -> bool:
    return bool(login) and not login.endswith("[bot]") and login not in seen


def add_random_search_users(s: requests.Session, seen: set, picked: list, target_count: int) -> None:
    queries = SEARCH_QUERIES[:]
    random.shuffle(queries)
    for q in queries:
        if len(picked) >= target_count:
            return
        r = s.get(f"{GITHUB_API}/search/users",
                  params={"q": q, "per_page": 30, "page": random.randint(1, 10)},
                  timeout=TIMEOUT)
        if r.status_code != 200:
            continue
        users = r.json().get("items", [])
        random.shuffle(users)
        for u in users:
            login = u.get("login")
            if u.get("type") == "User" and allowed_candidate(login, seen):
                seen.add(login)
                picked.append(login)
                if len(picked) >= target_count:
                    return


def add_repository_contributors(s: requests.Session, seen: set, picked: list, target_count: int) -> None:
    recent_cutoff = (datetime.utcnow() - timedelta(days=365)).strftime("%Y-%m-%d")
    queries = [f"{q} pushed:>{recent_cutoff}" for q in REPOSITORY_QUERIES]
    random.shuffle(queries)
    for q in queries:
        if len(picked) >= target_count:
            return
        r = s.get(f"{GITHUB_API}/search/repositories",
                  params={
                      "q": q,
                      "sort": random.choice(["updated", "forks", "help-wanted-issues"]),
                      "order": "desc",
                      "per_page": 10,
                      "page": random.randint(1, 5),
                  },
                  timeout=TIMEOUT)
        if r.status_code != 200:
            continue
        repos = r.json().get("items", [])
        random.shuffle(repos)
        for repo in repos:
            if len(picked) >= target_count:
                return
            contributors_url = repo.get("contributors_url")
            if not contributors_url:
                continue
            contributors_response = s.get(contributors_url,
                                          params={"per_page": 30, "anon": "false"},
                                          timeout=TIMEOUT)
            if contributors_response.status_code != 200:
                continue
            contributors = contributors_response.json()
            random.shuffle(contributors)
            for contributor in contributors:
                login = contributor.get("login")
                if contributor.get("type") == "User" and allowed_candidate(login, seen):
                    seen.add(login)
                    picked.append(login)
                    if len(picked) >= target_count:
                        return


def recommend(s: requests.Session, me: str, already: set, limit: int) -> list:
    picked = []
    seen = set(already) | {me}
    add_random_search_users(s, seen, picked, limit)
    add_repository_contributors(s, seen, picked, limit)
    random.shuffle(picked)
    return picked[:limit]


def follow(s: requests.Session, username: str) -> requests.Response:
    return s.put(f"{GITHUB_API}/user/following/{username}", timeout=TIMEOUT)


def remaining_quota(r: requests.Response):
    """从响应头读取剩余核心配额，读不到返回 None。"""
    value = r.headers.get("X-RateLimit-Remaining")
    return int(value) if value is not None and value.isdigit() else None


def main() -> int:
    token = os.getenv("FOLLOW_TOKEN", "").strip()
    if not token:
        print("::error::缺少 FOLLOW_TOKEN（在仓库 Settings → Secrets 中配置）")
        return 1

    low = int(os.getenv("FOLLOW_MIN", "10"))
    high = int(os.getenv("FOLLOW_MAX", "10"))
    floor = int(os.getenv("RATE_LIMIT_FLOOR", "200"))
    limit = random.randint(min(low, high), max(low, high))

    s = session(token)
    me = current_login(s)
    already = following_set(s)
    targets = recommend(s, me, already, limit)

    if not targets:
        print(f"@{me}: 没有可关注的新用户。")
        return 0

    print(f"@{me}: 本次计划关注 {len(targets)} 人。")
    ok = 0
    for name in targets:
        r = follow(s, name)
        remaining = remaining_quota(r)

        if r.status_code == 204:
            ok += 1
            print(f"  ✓ {name}")
        elif r.status_code == 403:
            # 二级速率限制 / 滥用检测：立即停止，避免账号被标记
            print(f"::warning::触发速率限制（403），提前停止。已关注 {ok} 人。")
            break
        else:
            print(f"  ✗ {name} (HTTP {r.status_code})")

        if remaining is not None and remaining < floor:
            print(f"::warning::剩余配额 {remaining} 低于阈值 {floor}，提前停止。已关注 {ok} 人。")
            break

        time.sleep(random.uniform(1.5, 4.0))  # 随机间隔，行为更接近真人

    print(f"@{me}: 本次成功关注 {ok}/{len(targets)} 人。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
