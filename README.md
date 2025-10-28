# 🚀 GitHub 自动关注工具

👉 在线地址（Render）：[https://github-auto-follow.onrender.com](https://github-auto-follow.onrender.com)

一个现代化的网页工具，让用户可以批量关注GitHub用户，提升社交网络影响力。

## 📍 项目地址

- **GitHub仓库**: [https://github.com/TUARAN/github-auto-follow](https://github.com/TUARAN/github-auto-follow)
- **Docker Hub镜像**: [https://hub.docker.com/r/tuaran1453/github-follow-tool](https://hub.docker.com/r/tuaran1453/github-follow-tool)
- **在线演示**: 使用Docker镜像一键部署

## 🔗 相关链接

| 类型 | 地址 | 说明 |
|------|------|------|
| **GitHub仓库** | [https://github.com/TUARAN/github-auto-follow](https://github.com/TUARAN/github-auto-follow) | 源代码仓库 |
| **Docker Hub** | [https://hub.docker.com/r/tuaran1453/github-follow-tool](https://hub.docker.com/r/tuaran1453/github-follow-tool) | Docker镜像仓库 |
| **GitHub Actions** | [https://github.com/TUARAN/github-auto-follow/actions](https://github.com/TUARAN/github-auto-follow/actions) | 自动构建状态 |
| **Issues** | [https://github.com/TUARAN/github-auto-follow/issues](https://github.com/TUARAN/github-auto-follow/issues) | 问题反馈 |

## ✨ 功能特性

- 🎯 **批量关注**: 支持一次性关注多个GitHub用户
- 🔐 **安全认证**: 使用GitHub Personal Access Token进行安全认证
- 📊 **实时进度**: 显示关注进度和结果状态
- 🎨 **现代UI**: 基于Vue.js和Tailwind CSS的美观界面
- ⚡ **高性能**: FastAPI后端，支持异步处理
- 🐳 **容器化**: Docker支持，一键部署
- 📈 **统计信息**: 显示成功/失败数量和详细结果
- 💾 **结果导出**: 支持CSV格式导出关注结果

## 🛠️ 技术栈

| 模块 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue.js 3 + Tailwind CSS | 现代化响应式界面 |
| 后端 | FastAPI + Python 3.11 | 高性能异步API服务 |
| API | GitHub REST API v3 | 官方GitHub API集成 |
| 部署 | Docker + Docker Compose | 容器化部署方案 |
| 代理 | Nginx | 反向代理和负载均衡 |

## 🚀 快速开始

### 🌐 在线体验（推荐）

**一键部署到公网，无需本地安装：**

**Render部署（推荐）：**
1. 访问 [Render](https://render.com)
2. 使用GitHub登录
3. 选择仓库 `TUARAN/github-auto-follow`
4. Render自动检测配置并部署
5. 获得公网地址（完全免费）

### 📦 本地部署

**使用Docker Hub镜像：**

```bash
# 直接运行Docker镜像
docker run -d -p 8000:8000 -p 3000:3000 --name github-follow-tool tuaran1453/github-follow-tool:latest

# 访问应用
# 前端: http://localhost:3000
# API: http://localhost:8000
# 文档: http://localhost:8000/docs
```

### 🔧 从源码部署

**1. 克隆GitHub仓库**
```bash
git clone https://github.com/TUARAN/github-auto-follow.git
cd github-auto-follow
```

**2. 使用Docker Compose**
```bash
# 下载docker-compose配置
curl -O https://raw.githubusercontent.com/TUARAN/github-auto-follow/main/docker-compose-hub.yml

# 启动服务
docker-compose -f docker-compose-hub.yml up -d
```

### 方法二：本地Docker构建

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd github-follow
   ```

2. **启动服务**
   ```bash
   # 基础部署
   docker-compose up -d
   
   # 生产环境（包含Nginx）
   docker-compose --profile production up -d
   ```

3. **访问应用**
   - 前端界面: http://localhost:3000
   - API文档: http://localhost:8000/docs
   - 生产环境: http://localhost

### 🐳 Docker部署地址

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/

### 📦 Docker Hub镜像

- **镜像地址**: `tuaran1453/github-follow-tool:latest`
- **Docker Hub**: [https://hub.docker.com/r/tuaran1453/github-follow-tool](https://hub.docker.com/r/tuaran1453/github-follow-tool)
- **拉取命令**: `docker pull tuaran1453/github-follow-tool:latest`
- **自动构建**: 支持GitHub Actions自动构建和推送

### 方法二：本地开发

1. **安装依赖**
   ```bash
   # 后端依赖
   cd backend
   pip install -r requirements.txt
   
   # 前端依赖（可选，使用CDN）
   # 无需安装，直接使用CDN资源
   ```

2. **启动后端服务**
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **启动前端服务**
   ```bash
   cd frontend
   python -m http.server 3000
   ```

4. **访问应用**
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
GET /
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DEBUG` | `false` | 调试模式 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `HOST` | `0.0.0.0` | 服务监听地址 |
| `PORT` | `8000` | 服务端口 |

### 速率限制

- GitHub API限制：5000次请求/小时（认证用户）
- 默认请求间隔：0.5秒
- 建议单次操作不超过100个用户

## 🛡️ 安全考虑

1. **Token安全**
   - Token仅在前端临时使用，不会永久存储
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
# Docker日志
docker-compose logs -f github-follow-tool

# 本地开发日志
# 后端日志会在控制台显示
```

## 🌐 公网部署指南

### 🚀 Cloudflare Pages部署

**Cloudflare Pages部署（推荐）：**
1. 访问 [Cloudflare Pages](https://pages.cloudflare.com/)
2. 使用GitHub登录
3. 选择仓库 `TUARAN/github-auto-follow`
4. 使用 `Dockerfile.cloudflare` 构建
5. 获得公网地址

**Cloudflare Workers部署：**
```bash
# 安装Wrangler CLI
npm install -g wrangler

# 登录Cloudflare
wrangler login

# 部署到Workers
wrangler deploy
```

### 📋 Cloudflare优势

| 特性 | 说明 |
|------|------|
| **免费额度** | 无限静态页面，100,000次请求/天 |
| **全球CDN** | 200+ 数据中心，全球加速 |
| **自动HTTPS** | 免费SSL证书，自动续期 |
| **DDoS防护** | 企业级安全防护 |
| **部署简单** | 连接GitHub，自动部署 |

## 🐳 Docker Hub部署指南

### 发布到Docker Hub

1. **准备Docker Hub账户**
   ```bash
   # 登录Docker Hub
   docker login
   ```

2. **构建和推送镜像**
   ```bash
   # 使用部署脚本（推荐）
   ./deploy.sh
   
   # 或手动执行
   docker build -t tuaran1453/github-follow-tool:latest .
   docker push tuaran1453/github-follow-tool:latest
   ```

3. **配置自动构建**
   - 在Docker Hub创建仓库 `tuaran1453/github-follow-tool`
   - 在GitHub仓库设置中添加Docker Hub secrets:
     - `DOCKER_USERNAME`: tuaran1453
     - `DOCKER_PASSWORD`: 你的Docker Hub密码或访问令牌
   - GitHub Actions会自动在推送代码时构建和推送镜像

### 使用Docker Hub镜像

1. **直接运行**
   ```bash
   docker run -d -p 8000:8000 -p 3000:3000 --name github-follow-tool tuaran1453/github-follow-tool:latest
   ```

2. **使用docker-compose**
   ```bash
   # 修改docker-compose-hub.yml中的镜像名
   # 然后运行
   docker-compose -f docker-compose-hub.yml up -d
   ```

3. **生产环境部署**
   ```bash
   # 使用Nginx反向代理
   docker-compose -f docker-compose-hub.yml --profile production up -d
   ```

### 镜像标签策略

- `latest` - 最新稳定版本
- `v1.0.0` - 语义化版本标签
- `dev` - 开发版本

### 🔄 GitHub Actions自动构建

项目已配置GitHub Actions工作流，支持自动构建和推送Docker镜像：

**触发条件：**
- 推送到 `main` 或 `master` 分支
- 创建版本标签（如 `v1.0.0`）
- 创建Pull Request

**配置步骤：**
1. 在GitHub仓库 `https://github.com/TUARAN/github-auto-follow` 中
2. 进入 Settings → Secrets and variables → Actions
3. 添加以下secrets：
   - `DOCKER_USERNAME`: `tuaran1453`
   - `DOCKER_PASSWORD`: 你的Docker Hub密码或访问令牌

**自动构建特性：**
- 多架构支持（linux/amd64, linux/arm64）
- 构建缓存优化
- 自动标签管理
- 构建证明和签名

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
