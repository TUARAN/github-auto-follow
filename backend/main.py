from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import asyncio
import random
import logging
from datetime import datetime, timedelta
from typing import List, Optional

try:
    from backend.trending import is_valid_date, load_digest, load_index
except ImportError:
    from trending import is_valid_date, load_digest, load_index

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GitHub Follow Tool", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # 与 allow_origins=["*"] 互斥，浏览器会拒绝 True 组合
    allow_methods=["*"],
    allow_headers=["*"],
)

GITHUB_API = "https://api.github.com"

RANDOM_USER_QUERIES = [
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


def extract_token(authorization: Optional[str]) -> str:
    """从 Authorization header 解析 token，避免 token 出现在 URL/日志中"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() in ("token", "bearer"):
        return parts[1]
    return authorization.strip()


class FollowRequest(BaseModel):
    token: str
    usernames: List[str]
    delay: Optional[float] = 0.5  # 请求间隔，避免触发速率限制


class FollowResult(BaseModel):
    username: str
    status: str
    message: str
    success: bool


class FollowResponse(BaseModel):
    results: List[FollowResult]
    total: int
    successful: int
    failed: int


def validate_github_token(token: str) -> bool:
    try:
        headers = {"Authorization": f"token {token}"}
        response = requests.get(f"{GITHUB_API}/user", headers=headers, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return False


def is_allowed_candidate(username: str, current_login: str, following_logins: set, picked: List[str]) -> bool:
    return (
        bool(username)
        and not username.endswith("[bot]")
        and username not in following_logins
        and username != current_login
        and username not in picked
    )


def collect_current_following(headers: dict) -> set:
    """拉取当前已关注的人（最多 500 个，用于推荐去重）。"""
    following_logins = set()
    for page in range(1, 6):
        response = requests.get(
            f"{GITHUB_API}/user/following",
            params={"per_page": 100, "page": page},
            headers=headers,
            timeout=10,
        )
        if response.status_code != 200:
            break
        batch = response.json()
        following_logins.update(user["login"] for user in batch)
        if len(batch) < 100:
            break
    return following_logins


def add_random_search_users(headers: dict, current_login: str, following_logins: set,
                            recommended_users: List[str], target_count: int) -> None:
    queries = RANDOM_USER_QUERIES[:]
    random.shuffle(queries)
    for query in queries:
        if len(recommended_users) >= target_count:
            return
        response = requests.get(
            f"{GITHUB_API}/search/users",
            params={"q": query, "per_page": 30, "page": random.randint(1, 10)},
            headers=headers,
            timeout=10,
        )
        if response.status_code != 200:
            continue
        users = response.json().get("items", [])
        random.shuffle(users)
        for user in users:
            username = user.get("login")
            if user.get("type") == "User" and is_allowed_candidate(
                username, current_login, following_logins, recommended_users
            ):
                recommended_users.append(username)
                if len(recommended_users) >= target_count:
                    return


def add_repository_contributors(headers: dict, current_login: str, following_logins: set,
                                recommended_users: List[str], target_count: int) -> None:
    recent_cutoff = (datetime.utcnow() - timedelta(days=365)).strftime("%Y-%m-%d")
    queries = [f"{query} pushed:>{recent_cutoff}" for query in REPOSITORY_QUERIES]
    random.shuffle(queries)

    for query in queries:
        if len(recommended_users) >= target_count:
            return
        repo_response = requests.get(
            f"{GITHUB_API}/search/repositories",
            params={
                "q": query,
                "sort": random.choice(["updated", "forks", "help-wanted-issues"]),
                "order": "desc",
                "per_page": 10,
                "page": random.randint(1, 5),
            },
            headers=headers,
            timeout=10,
        )
        if repo_response.status_code != 200:
            continue

        repositories = repo_response.json().get("items", [])
        random.shuffle(repositories)
        for repo in repositories:
            if len(recommended_users) >= target_count:
                return
            contributors_url = repo.get("contributors_url")
            if not contributors_url:
                continue
            contributors_response = requests.get(
                contributors_url,
                params={"per_page": 30, "anon": "false"},
                headers=headers,
                timeout=10,
            )
            if contributors_response.status_code != 200:
                continue
            contributors = contributors_response.json()
            random.shuffle(contributors)
            for contributor in contributors:
                username = contributor.get("login")
                if contributor.get("type") == "User" and is_allowed_candidate(
                    username, current_login, following_logins, recommended_users
                ):
                    recommended_users.append(username)
                    if len(recommended_users) >= target_count:
                        return


def get_recommended_users(token: str, limit: int = 50) -> List[str]:
    """获取推荐的 GitHub 用户列表（随机搜索 + 活跃项目参与者，过滤自己和已关注的人）。"""
    try:
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        user_response = requests.get(f"{GITHUB_API}/user", headers=headers, timeout=10)
        if user_response.status_code != 200:
            return []
        current_login = user_response.json().get("login")

        following_logins = collect_current_following(headers)
        recommended_users: List[str] = []

        add_random_search_users(headers, current_login, following_logins, recommended_users, limit)
        add_repository_contributors(headers, current_login, following_logins, recommended_users, limit)

        random.shuffle(recommended_users)
        return recommended_users[:limit]

    except Exception as e:
        logger.error(f"Error getting recommended users: {e}")
        return []


def follow_user(token: str, username: str) -> FollowResult:
    """关注单个用户"""
    try:
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        user_response = requests.get(f"{GITHUB_API}/users/{username}", headers=headers, timeout=10)
        if user_response.status_code == 404:
            return FollowResult(username=username, status="error", message="用户不存在", success=False)

        follow_response = requests.put(
            f"{GITHUB_API}/user/following/{username}", headers=headers, timeout=10
        )

        if follow_response.status_code == 204:
            return FollowResult(username=username, status="success", message="关注成功", success=True)
        elif follow_response.status_code == 401:
            return FollowResult(username=username, status="error", message="Token无效或权限不足", success=False)
        elif follow_response.status_code == 403:
            return FollowResult(username=username, status="error", message="API速率限制或权限不足", success=False)
        else:
            return FollowResult(
                username=username, status="error",
                message=f"关注失败 (HTTP {follow_response.status_code})", success=False,
            )

    except requests.exceptions.Timeout:
        return FollowResult(username=username, status="error", message="请求超时", success=False)
    except Exception as e:
        logger.error(f"Error following {username}: {e}")
        return FollowResult(username=username, status="error", message=f"未知错误: {str(e)}", success=False)


@app.get("/healthz")
async def healthz():
    """健康检查端点（用于 Render health check）"""
    return {"message": "GitHub Follow Tool API", "status": "running"}


@app.get("/")
async def index_page():
    """返回前端页面"""
    return FileResponse("frontend/index.html")


@app.post("/follow", response_model=FollowResponse)
async def follow_users(request: FollowRequest):
    """批量关注用户"""
    try:
        if not validate_github_token(request.token):
            raise HTTPException(status_code=401, detail="Invalid GitHub token")

        unique_usernames = [u.strip() for u in dict.fromkeys(request.usernames) if u.strip()]

        results = []
        successful = 0
        failed = 0
        logger.info(f"Starting to follow {len(unique_usernames)} users")

        for i, username in enumerate(unique_usernames):
            result = follow_user(request.token, username)
            results.append(result)
            if result.success:
                successful += 1
            else:
                failed += 1
            if i < len(unique_usernames) - 1:
                await asyncio.sleep(request.delay)

        logger.info(f"Follow operation completed. Success: {successful}, Failed: {failed}")
        return FollowResponse(results=results, total=len(results), successful=successful, failed=failed)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in follow_users: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/user/info")
async def get_user_info(authorization: Optional[str] = Header(None)):
    """获取当前用户信息"""
    token = extract_token(authorization)
    try:
        headers = {"Authorization": f"token {token}"}
        response = requests.get(f"{GITHUB_API}/user", headers=headers, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            return {
                "username": user_data.get("login"),
                "name": user_data.get("name"),
                "avatar_url": user_data.get("avatar_url"),
                "followers": user_data.get("followers", 0),
                "following": user_data.get("following", 0),
            }
        raise HTTPException(status_code=401, detail="Invalid token")
    except HTTPException:
        raise
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=408, detail="Request timeout")
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/users/recommended")
async def get_recommended_users_endpoint(limit: int = 50, authorization: Optional[str] = Header(None)):
    """获取推荐的用户列表"""
    token = extract_token(authorization)
    try:
        if not validate_github_token(token):
            raise HTTPException(status_code=401, detail="Invalid GitHub token")
        recommended_users = get_recommended_users(token, limit)
        return {"users": recommended_users, "total": len(recommended_users)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommended users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



@app.get("/trending/dates")
async def trending_dates():
    """列出可查看的每日热门清单日期（只读，无需 Token）。"""
    return load_index()


@app.get("/trending")
async def trending_latest():
    """返回最新一份每日热门仓库清单（只读，无需 Token）。"""
    digest = load_digest()
    if not digest:
        return {"date": None, "generated_at": None, "count": 0, "items": [], "dates": [], "latest": None}
    return digest


@app.get("/trending/{digest_date}")
async def trending_by_date(digest_date: str):
    """返回指定日期的每日热门仓库清单（只读，无需 Token）。"""
    if not is_valid_date(digest_date):
        raise HTTPException(status_code=400, detail="Invalid date, expected YYYY-MM-DD")
    digest = load_digest(digest_date)
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found for this date")
    return digest


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
