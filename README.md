# 🚀 GitHub 自动关注工具

👉 在线地址（Render）：[https://github-auto-follow.onrender.com](https://github-auto-follow.onrender.com)
👉 后端 API 域名：`https://gaf.onrender.com`

一个现代化的网页工具，让用户可以批量关注GitHub用户，提升社交网络影响力。

## 📍 项目地址

- **GitHub仓库**: [https://github.com/TUARAN/github-auto-follow](https://github.com/TUARAN/github-auto-follow)
- **在线演示**: [https://github-auto-follow.onrender.com](https://github-auto-follow.onrender.com)

## 🔗 相关链接

| 类型 | 地址 | 说明 |
|------|------|------|
| **GitHub仓库** | [https://github.com/TUARAN/github-auto-follow](https://github.com/TUARAN/github-auto-follow) | 源代码仓库 |
| **在线演示** | [https://github-auto-follow.onrender.com](https://github-auto-follow.onrender.com) | 在线体验 |
| **后端 API** | `https://gaf.onrender.com` | 生产后端地址 |
| **Issues** | [https://github.com/TUARAN/github-auto-follow/issues](https://github.com/TUARAN/github-auto-follow/issues) | 问题反馈 |

## ✨ 功能特性

- 🎯 **批量关注**: 支持一次性关注多个GitHub用户
- 🔐 **安全认证**: 使用GitHub Personal Access Token进行安全认证
- 📊 **实时进度**: 显示关注进度和结果状态
- 🎨 **现代UI**: 基于Vue.js和Tailwind CSS的美观界面
- ⚡ **高性能**: FastAPI后端，支持异步处理
- ☁️ **云部署**: Render云平台，一键部署
- 📈 **统计信息**: 显示成功/失败数量和详细结果
- 💾 **结果导出**: 支持CSV格式导出关注结果
- 🔀 **非名人推荐**: 从随机搜索用户和活跃项目参与者中生成关注候选，不按粉丝数排名
- 📰 **每日热门清单**: 每天采集 GitHub 趋势和近期热门公开仓库，在页面里浏览今日和近期历史（只读，不会自动点 star）

## 🛠️ 技术栈

| 模块 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue.js 3 + Tailwind CSS | 现代化响应式界面 |
| 后端 | FastAPI + Python 3.11 | 高性能异步API服务 |
| API | GitHub REST API v3 | 官方GitHub API集成 |
| 部署 | Render | 云平台部署方案 |

## 🚀 快速开始

### 🌐 在线体验（推荐）

**一键部署到公网，无需本地安装：**

**Render部署（推荐）：**
1. 访问 [Render](https://render.com)
2. 使用GitHub登录
3. 选择仓库 `TUARAN/github-auto-follow`
4. Render自动检测配置并部署
5. 获得公网地址（完全免费）

### 🔧 本地开发

**1. 克隆GitHub仓库**
```bash
git clone https://github.com/TUARAN/github-auto-follow.git
cd github-auto-follow
```

**2. 安装依赖**
```bash
# 后端依赖
cd backend
pip install -r requirements.txt
```

**3. 启动后端服务**
```bash
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**4. 启动前端服务**
```bash
cd frontend
python3 -m http.server 3000
```

**5. 访问应用**
- 前端界面: http://localhost:3000
- API文档: http://localhost:8000/docs


## 🔑 获取GitHub Token

1. 访问 [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token (classic)"
3. 选择以下权限：
   - `user:follow` - 关注/取消关注用户
   - `read:user` - 读取用户信息（可选）
4. 复制生成的token

## 📖 使用说明

### 1. 输入Token
- 在Token输入框中粘贴你的GitHub Personal Access Token
- 系统会自动验证Token的有效性
- 验证成功后显示你的GitHub用户信息

### 2. 输入用户名
- 在文本框中输入要关注的GitHub用户名
- 每行输入一个用户名
- 支持批量输入，最多100个用户
- 系统会自动去重

### 3. 配置选项
- **请求间隔**: 设置API请求间隔，避免触发速率限制（默认0.5秒）
- **最大用户数**: 限制单次操作的用户数量（默认50个）

### 4. 执行关注
- 点击"开始关注"按钮
- 系统会显示实时进度
- 完成后显示详细结果

### 5. 查看结果
- 成功/失败统计
- 每个用户的详细状态
- 支持导出CSV格式结果

### 6. 浏览每日热门仓库
- 打开页面后切换到「每日热门」标签（或访问 `#trending`）
- 可查看当天清单，并切换近期日期回看历史
- 每条包含仓库全名、简介、语言、star 数和入选原因；点击仓库名会打开 GitHub 页面
- 清单是只读的，页面不会自动点 star，也没有批量点 star 的操作

## 🔧 API接口

### 关注用户
```http
POST /follow
Content-Type: application/json

{
  "token": "your_github_token",
  "usernames": ["user1", "user2", "user3"],
  "delay": 0.5
}
```

### 获取用户信息
```http
GET /user/info?token=your_github_token
```

### 健康检查
```http
GET /healthz
```

### 每日热门清单（无需 Token）
```http
GET /trending
GET /trending/dates
GET /trending/2026-11-17
```

`GET /trending` 返回最新一份清单，响应中同时包含可回看的日期列表。每条仓库包含 `full_name`、`description`、`language`、`stars`、`url` 和可选的 `reason`；配置了 `DEEPSEEK_API_KEY` 时还会有中文简介 `description_zh`。

### 每日热门定时采集与简介翻译

- 定时任务：`.github/workflows/daily-trending.yml`，北京时间每天 08:30 跑一次 `scripts/daily_trending.py`，并把 `data/trending/` 提交回 `main` 分支；也可以在 Actions 页面手动触发（workflow_dispatch）
- 简介翻译：配置 Secrets `DEEPSEEK_API_KEY` 后，清单生成时自动把英文简介译成简体中文，写入 `description_zh`；翻译结果缓存在 `data/trending/translations.json`（按仓库名和简介哈希做键，同一仓库不重复翻译，90 天过期）
- 翻译失败或未配置 key 时 `description_zh` 留空，不影响采集和展示；展示端优先中文简介、回退英文原文

## ⚙️ 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DEBUG` | `false` | 调试模式 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `HOST` | `0.0.0.0` | 服务监听地址 |
| `PORT` | `8000` | 服务端口 |
| `FOLLOW_TOKEN` | 无（必填） | 自动关注脚本使用的 GitHub Token，需要 `user:follow` 权限 |
| `FOLLOW_MIN` | `10` | 自动关注脚本单次关注人数下限 |
| `FOLLOW_MAX` | `10` | 自动关注脚本单次关注人数上限 |
| `RATE_LIMIT_FLOOR` | `200` | GitHub API 剩余配额低于该值时提前停止 |
| `DIGEST_TOKEN` / `GITHUB_TOKEN` | 无（选填） | 采集热门清单时用于提高 GitHub Search API 速率限制，只读即可。GitHub Actions 会自动使用 `GITHUB_TOKEN`，一般不必另配 Secret |
| `DEEPSEEK_API_KEY` | 无（选填） | 配置后把仓库简介翻译成中文，写入清单的 `description_zh` 字段；未配置或 key 无效时跳过翻译，采集照常完成。在 GitHub Actions 中通过 Secrets 配置 |
| `DIGEST_TRANSLATE_MODEL` | `deepseek-chat` | 简介翻译使用的 DeepSeek 模型 |
| `DIGEST_LIMIT` | `30` | 每日热门清单条数，限制在 20–50 |
| `DIGEST_RETENTION_DAYS` | `14` | 清单保留天数，更早的文件会被删除 |
| `TRENDING_DATA_DIR` | `data/trending` | 后端读取清单的本地目录 |
| `TRENDING_FALLBACK_URL` | 本仓库 `main` 分支的 raw 地址 | 本地没有清单文件时，后端可回源到 GitHub 上已提交的数据 |

### 速率限制

- GitHub API限制：5000次请求/小时（认证用户）
- 默认请求间隔：0.5秒
- 建议单次操作不超过100个用户

### 自动关注脚本

```bash
FOLLOW_TOKEN=your_github_token python3 scripts/daily_follow.py
```

自动脚本会随机决定本次关注人数，并从两类来源挑选候选：

- 随机 GitHub 用户搜索结果
- 近期活跃项目的 contributors

脚本会过滤自己、已关注用户和 bot 账号；不会使用粉丝数排序，也不会追加固定明星名单。

GitHub Actions 默认在北京时间 08:00–17:00 每小时触发一次，每批随机延迟最多
20 分钟后关注 10 人，目标每天约 100 人。若遇到 GitHub API 限流、任务延迟或
没有足够的新候选，脚本会提前停止，因此实际人数可能低于 100。

### 每日热门清单脚本

```bash
# 本地生成当天清单（可选提供 token 以提高 API 速率限制）
python3 scripts/daily_trending.py

DIGEST_TOKEN=your_github_token DIGEST_LIMIT=30 python3 scripts/daily_trending.py
```

脚本会：

- 读取 GitHub Trending（今日 + 本周）页面，收集正在上升的公开仓库
- 再用 GitHub Search API 补充近 14 日新建、星标较多的公开仓库
- 去重后默认保存约 30 条（可配置，范围 20–50）到 `data/trending/YYYY-MM-DD.json`，并更新 `data/trending/index.json`
- 只做只读采集，不会调用 Star API，也不会关注任何人

工作流模板在 `docs/github-actions/daily-trending.yml`，默认在北京时间 08:00 运行，并把清单提交回仓库，供后端 API 和前端读取。启用方式：

1. 把 `docs/github-actions/daily-trending.yml` 复制为 `.github/workflows/daily-trending.yml` 并提交到默认分支 `main`（新建工作流文件需要 GitHub token 具备 `workflow` 权限；也可以在 GitHub 网页上新建该文件）
2. 确保仓库已打开 GitHub Actions（Settings → Actions → Allow all actions）
3. 合并到 `main` 后，定时任务会自动生效；也可在 Actions 标签页打开 **Daily Trending Digest**，点击 **Run workflow** 立即生成一份
4. 无需额外配置 Secret：工作流使用内置的 `GITHUB_TOKEN` 访问只读 API 并提交数据文件

查看清单：

- 打开应用后切换到「每日热门」标签，或直接访问 `/#trending`
- 本地先生成清单，再启动后端：`cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload`，然后访问 http://localhost:8000/#trending
- 也可直接请求 `GET /trending` 和 `GET /trending/{日期}`

## 🛡️ 安全考虑

1. **Token安全**
   - 自动脚本使用的 `FOLLOW_TOKEN` 仅通过环境变量提供，不在仓库或前端暴露
   - 用户Token仅在前端临时使用，不会永久存储
   - 建议定期更换Token
   - 不要在不信任的环境中使用

2. **API限制**
   - 内置请求间隔，避免触发速率限制
   - 支持自定义延迟时间
   - 自动处理API错误和重试

3. **输入验证**
   - 用户名格式验证
   - 数量限制保护
   - 自动去重处理

## 🐛 故障排除

### 常见问题

1. **Token验证失败**
   - 检查Token是否正确
   - 确认Token具有`user:follow`权限
   - 检查Token是否过期

2. **关注失败**
   - 检查用户名是否存在
   - 确认目标用户未被屏蔽
   - 检查API速率限制

3. **网络连接问题**
   - 检查网络连接
   - 确认GitHub API可访问
   - 检查防火墙设置

### 日志查看

```bash
# 本地开发日志
# 后端日志会在控制台显示
```

 


## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## ⚠️ 免责声明

本工具仅供学习和个人使用。请遵守GitHub的服务条款，不要滥用API。使用本工具产生的任何后果由用户自行承担。

## 📞 支持

如果你遇到问题或有建议，请：

1. 查看[故障排除](#故障排除)部分
2. 搜索现有的[Issues](../../issues)
3. 创建新的Issue描述问题

---

⭐ 如果这个项目对你有帮助，请给它一个星标！
