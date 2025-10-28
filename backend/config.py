# 配置文件
import os

# GitHub API配置
GITHUB_API_BASE = "https://api.github.com"
GITHUB_API_VERSION = "v3"

# 应用配置
APP_NAME = "GitHub Follow Tool"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# 服务器配置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# API限制配置
DEFAULT_REQUEST_DELAY = 0.5  # 默认请求间隔（秒）
MAX_USERS_PER_REQUEST = 100  # 单次请求最大用户数
REQUEST_TIMEOUT = 10  # 请求超时时间（秒）

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 固定自动执行配置（tuaran账号）
# 在部署环境中以环境变量方式提供，避免硬编码泄露
# 示例：FIXED_TOKEN=ghp_xxx AUTO_START_DATE=2025-10-28 DAILY_FOLLOW_LIMIT=10
FIXED_TOKEN = os.getenv("FIXED_TOKEN", "")
AUTO_START_DATE = os.getenv("AUTO_START_DATE", "2025-10-28")
DAILY_FOLLOW_LIMIT = int(os.getenv("DAILY_FOLLOW_LIMIT", 10))
DATA_FILE = os.getenv("DATA_FILE", "auto_follow_data.json")
