from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import time
import asyncio
from typing import List, Dict, Optional
import logging
import random
import threading
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GitHub Follow Tool", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GITHUB_API = "https://api.github.com"

# 自动关注相关全局变量
auto_follow_status = {
    "is_running": False,
    "start_time": None,
    "next_run_time": None,
    "total_followed": 0,
    "last_batch_results": None,
    "token": None,
    "interval_minutes": 5,
    "users_per_batch": 10,
    "timer": None
}

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

class AutoFollowRequest(BaseModel):
    token: str
    interval_minutes: Optional[int] = 5  # 间隔分钟数
    users_per_batch: Optional[int] = 10  # 每批关注用户数

class AutoFollowStatus(BaseModel):
    is_running: bool
    start_time: Optional[str]
    next_run_time: Optional[str]
    total_followed: int
    last_batch_results: Optional[List[FollowResult]]

def validate_github_token(token: str) -> bool:
    """验证GitHub token是否有效"""
    try:
        headers = {"Authorization": f"token {token}"}
        response = requests.get(f"{GITHUB_API}/user", headers=headers, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return False

def get_recommended_users(token: str, limit: int = 50) -> List[str]:
    """获取推荐的GitHub用户列表"""
    try:
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # 获取当前用户信息
        user_response = requests.get(f"{GITHUB_API}/user", headers=headers, timeout=10)
        if user_response.status_code != 200:
            return []
        
        current_user = user_response.json()
        current_login = current_user.get("login")
        
        # 获取用户正在关注的人
        following_response = requests.get(
            f"{GITHUB_API}/user/following?per_page=100",
            headers=headers,
            timeout=10
        )
        
        if following_response.status_code != 200:
            return []
        
        following_users = following_response.json()
        following_logins = {user["login"] for user in following_users}
        
        # 获取推荐用户（通过搜索活跃用户）
        recommended_users = []
        
        # 搜索最近活跃的用户
        search_queries = [
            "created:>2023-01-01 followers:>10",
            "created:>2022-01-01 followers:>50",
            "created:>2021-01-01 followers:>100",
            "language:python followers:>20",
            "language:javascript followers:>20",
            "language:java followers:>20"
        ]
        
        for query in search_queries:
            if len(recommended_users) >= limit:
                break
                
            search_response = requests.get(
                f"{GITHUB_API}/search/users?q={query}&sort=followers&order=desc&per_page=30",
                headers=headers,
                timeout=10
            )
            
            if search_response.status_code == 200:
                search_results = search_response.json()
                for user in search_results.get("items", []):
                    username = user["login"]
                    if (username not in following_logins and 
                        username != current_login and 
                        username not in recommended_users):
                        recommended_users.append(username)
                        if len(recommended_users) >= limit:
                            break
        
        # 如果推荐用户不够，添加一些知名用户
        famous_users = [
            "torvalds", "gaearon", "sindresorhus", "addyosmani", "paulirish",
            "jashkenas", "defunkt", "mojombo", "pjhyett", "wycats",
            "dhh", "jeresig", "substack", "creationix", "ry",
            "tj", "visionmedia", "isaacs", "mikeal", "feross",
            "rauchg", "rauchg", "rauchg", "rauchg", "rauchg"
        ]
        
        for user in famous_users:
            if (user not in following_logins and 
                user != current_login and 
                user not in recommended_users):
                recommended_users.append(user)
                if len(recommended_users) >= limit:
                    break
        
        # 随机打乱顺序
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
            "Accept": "application/vnd.github.v3+json"
        }
        
        # 检查用户是否存在
        user_response = requests.get(f"{GITHUB_API}/users/{username}", headers=headers, timeout=10)
        if user_response.status_code == 404:
            return FollowResult(
                username=username,
                status="error",
                message="用户不存在",
                success=False
            )
        
        # 执行关注操作
        follow_response = requests.put(
            f"{GITHUB_API}/user/following/{username}",
            headers=headers,
            timeout=10
        )
        
        if follow_response.status_code == 204:
            return FollowResult(
                username=username,
                status="success",
                message="关注成功",
                success=True
            )
        elif follow_response.status_code == 401:
            return FollowResult(
                username=username,
                status="error",
                message="Token无效或权限不足",
                success=False
            )
        elif follow_response.status_code == 403:
            return FollowResult(
                username=username,
                status="error",
                message="API速率限制或权限不足",
                success=False
            )
        else:
            return FollowResult(
                username=username,
                status="error",
                message=f"关注失败 (HTTP {follow_response.status_code})",
                success=False
            )
            
    except requests.exceptions.Timeout:
        return FollowResult(
            username=username,
            status="error",
            message="请求超时",
            success=False
        )
    except Exception as e:
        logger.error(f"Error following {username}: {e}")
        return FollowResult(
            username=username,
            status="error",
            message=f"未知错误: {str(e)}",
            success=False
        )

def auto_follow_batch():
    """执行一批自动关注"""
    global auto_follow_status
    
    if not auto_follow_status["is_running"] or not auto_follow_status["token"]:
        return
    
    try:
        logger.info("Starting auto follow batch")
        
        # 获取推荐用户
        recommended_users = get_recommended_users(
            auto_follow_status["token"], 
            auto_follow_status["users_per_batch"]
        )
        
        if not recommended_users:
            logger.warning("No recommended users found")
            return
        
        # 执行关注
        results = []
        successful = 0
        
        for username in recommended_users:
            result = follow_user(auto_follow_status["token"], username)
            results.append(result)
            
            if result.success:
                successful += 1
                auto_follow_status["total_followed"] += 1
            
            # 添加延迟避免触发速率限制
            time.sleep(0.5)
        
        # 更新状态
        auto_follow_status["last_batch_results"] = results
        
        logger.info(f"Auto follow batch completed. Success: {successful}, Total: {len(results)}")
        
        # 计算下次运行时间
        next_run = datetime.now() + timedelta(minutes=auto_follow_status["interval_minutes"])
        auto_follow_status["next_run_time"] = next_run.isoformat()
        
        # 设置下次定时任务
        if auto_follow_status["is_running"]:
            auto_follow_status["timer"] = threading.Timer(
                auto_follow_status["interval_minutes"] * 60,
                auto_follow_batch
            )
            auto_follow_status["timer"].start()
            
    except Exception as e:
        logger.error(f"Error in auto follow batch: {e}")

def start_auto_follow(token: str, interval_minutes: int = 5, users_per_batch: int = 10):
    """启动自动关注"""
    global auto_follow_status
    
    if auto_follow_status["is_running"]:
        raise HTTPException(status_code=400, detail="Auto follow is already running")
    
    if not validate_github_token(token):
        raise HTTPException(status_code=401, detail="Invalid GitHub token")
    
    # 更新状态
    auto_follow_status.update({
        "is_running": True,
        "start_time": datetime.now().isoformat(),
        "token": token,
        "interval_minutes": interval_minutes,
        "users_per_batch": users_per_batch,
        "total_followed": 0,
        "last_batch_results": None
    })
    
    # 立即执行第一批
    auto_follow_batch()
    
    logger.info(f"Auto follow started. Interval: {interval_minutes}min, Batch size: {users_per_batch}")

def stop_auto_follow():
    """停止自动关注"""
    global auto_follow_status
    
    if not auto_follow_status["is_running"]:
        raise HTTPException(status_code=400, detail="Auto follow is not running")
    
    # 停止定时器
    if auto_follow_status["timer"]:
        auto_follow_status["timer"].cancel()
        auto_follow_status["timer"] = None
    
    # 更新状态
    auto_follow_status.update({
        "is_running": False,
        "next_run_time": None
    })
    
    logger.info("Auto follow stopped")

@app.get("/")
async def root():
    """健康检查端点"""
    return {"message": "GitHub Follow Tool API", "status": "running"}

@app.post("/follow", response_model=FollowResponse)
async def follow_users(request: FollowRequest):
    """批量关注用户"""
    try:
        # 验证token
        if not validate_github_token(request.token):
            raise HTTPException(status_code=401, detail="Invalid GitHub token")
        
        # 去重用户名
        unique_usernames = list(set(request.usernames))
        
        results = []
        successful = 0
        failed = 0
        
        logger.info(f"Starting to follow {len(unique_usernames)} users")
        
        for i, username in enumerate(unique_usernames):
            if not username.strip():
                continue
                
            username = username.strip()
            logger.info(f"Following user {i+1}/{len(unique_usernames)}: {username}")
            
            result = follow_user(request.token, username)
            results.append(result)
            
            if result.success:
                successful += 1
            else:
                failed += 1
            
            # 添加延迟避免触发速率限制
            if i < len(unique_usernames) - 1:  # 不在最后一个请求后等待
                await asyncio.sleep(request.delay)
        
        logger.info(f"Follow operation completed. Success: {successful}, Failed: {failed}")
        
        return FollowResponse(
            results=results,
            total=len(results),
            successful=successful,
            failed=failed
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in follow_users: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/user/info")
async def get_user_info(token: str):
    """获取当前用户信息"""
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
                "following": user_data.get("following", 0)
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
            
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=408, detail="Request timeout")
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users/recommended")
async def get_recommended_users_endpoint(token: str, limit: int = 50):
    """获取推荐的用户列表"""
    try:
        if not validate_github_token(token):
            raise HTTPException(status_code=401, detail="Invalid GitHub token")
        
        recommended_users = get_recommended_users(token, limit)
        return {
            "users": recommended_users,
            "total": len(recommended_users)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommended users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/auto-follow/start")
async def start_auto_follow_endpoint(request: AutoFollowRequest):
    """启动自动关注"""
    try:
        start_auto_follow(
            request.token,
            request.interval_minutes,
            request.users_per_batch
        )
        return {"message": "Auto follow started successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting auto follow: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/auto-follow/stop")
async def stop_auto_follow_endpoint():
    """停止自动关注"""
    try:
        stop_auto_follow()
        return {"message": "Auto follow stopped successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping auto follow: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/auto-follow/status", response_model=AutoFollowStatus)
async def get_auto_follow_status():
    """获取自动关注状态"""
    return AutoFollowStatus(
        is_running=auto_follow_status["is_running"],
        start_time=auto_follow_status["start_time"],
        next_run_time=auto_follow_status["next_run_time"],
        total_followed=auto_follow_status["total_followed"],
        last_batch_results=auto_follow_status["last_batch_results"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
