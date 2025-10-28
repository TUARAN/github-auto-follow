# 🚀 快速部署指南

## 📦 当前项目状态

✅ **已完成配置：**
- Docker镜像构建配置
- GitHub Actions自动构建工作流
- Docker Hub部署脚本
- 完整的README文档

## 🔧 部署步骤

### 1. 登录Docker Hub
```bash
docker login
# 输入用户名: tuaran1453
# 输入密码
```

### 2. 推送代码到GitHub
```bash
git add .
git commit -m "Add GitHub Actions and Docker Hub support"
git push origin main
```

### 3. 配置GitHub Actions Secrets
- 访问: https://github.com/TUARAN/github-auto-follow/settings/secrets/actions
- 添加secrets:
  - `DOCKER_USERNAME`: `tuaran1453`
  - `DOCKER_PASSWORD`: 你的Docker Hub密码

### 4. 在Docker Hub创建仓库
- 访问: https://hub.docker.com/
- 创建仓库: `tuaran1453/github-follow-tool`

### 5. 验证自动构建
- 查看Actions: https://github.com/TUARAN/github-auto-follow/actions
- 确认构建成功

## 📋 文件说明

| 文件 | 用途 |
|------|------|
| `deploy.sh` | 手动部署脚本 |
| `start.sh` | 本地启动脚本 |
| `docker-compose-hub.yml` | Docker Hub部署配置 |
| `docker-compose-simple.yml` | 本地Docker部署 |
| `.github/workflows/docker.yml` | GitHub Actions工作流 |
| `GITHUB_ACTIONS.md` | GitHub Actions配置说明 |

## 🎯 最终结果

部署完成后，任何人都可以使用：
```bash
docker run -d -p 8000:8000 -p 3000:3000 --name github-follow-tool tuaran1453/github-follow-tool:latest
```

访问地址：
- 前端: http://localhost:3000
- API: http://localhost:8000
- 文档: http://localhost:8000/docs
