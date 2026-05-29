from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import asyncio
import random
import logging
from typing import List, Optional

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


def get_recommended_users(token: str, limit: int = 50) -> List[str]:
    """获取推荐的 GitHub 用户列表（过滤掉自己和已关注的人）"""
    try:
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        user_response = requests.get(f"{GITHUB_API}/user", headers=headers, timeout=10)
        if user_response.status_code != 200:
            return []
        current_login = user_response.json().get("login")

        following_response = requests.get(
            f"{GITHUB_API}/user/following?per_page=100", headers=headers, timeout=10
        )
        if following_response.status_code != 200:
            return []
        following_logins = {user["login"] for user in following_response.json()}

        recommended_users: List[str] = []
        search_queries = [
            "created:>2023-01-01 followers:>10",
            "created:>2022-01-01 followers:>50",
            "created:>2021-01-01 followers:>100",
            "language:python followers:>20",
            "language:javascript followers:>20",
            "language:java followers:>20",
        ]

        for query in search_queries:
            if len(recommended_users) >= limit:
                break
            search_response = requests.get(
                f"{GITHUB_API}/search/users?q={query}&sort=followers&order=desc&per_page=30",
                headers=headers,
                timeout=10,
            )
            if search_response.status_code == 200:
                for user in search_response.json().get("items", []):
                    username = user["login"]
                    if (username not in following_logins
                            and username != current_login
                            and username not in recommended_users):
                        recommended_users.append(username)
                        if len(recommended_users) >= limit:
                            break

        famous_users = [
            "torvalds", "gaearon", "sindresorhus", "addyosmani", "paulirish",
            "jashkenas", "defunkt", "mojombo", "pjhyett", "wycats",
            "dhh", "jeresig", "substack", "creationix", "ry",
            "tj", "visionmedia", "isaacs", "mikeal", "feross",
            "rauchg", "yyx990803", "kentcdodds", "getify", "bradfitz",
        ]
        for user in famous_users:
            if (user not in following_logins
                    and user != current_login
                    and user not in recommended_users):
                recommended_users.append(user)
                if len(recommended_users) >= limit:
                    break

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
