# 🎉 项目部署完成！

## 📍 仓库地址

- **GitHub仓库**: https://github.com/TUARAN/github-auto-follow
- **Docker Hub镜像**: https://hub.docker.com/r/tuaran1453/github-follow-tool

## 🚀 使用方法

### 最简单的方式（推荐）
```bash
docker run -d -p 8000:8000 -p 3000:3000 --name github-follow-tool tuaran1453/github-follow-tool:latest
```

### 从源码部署
```bash
git clone https://github.com/TUARAN/github-auto-follow.git
cd github-auto-follow
docker-compose up -d
```

## 🌐 访问地址

- **前端界面**: http://localhost:3000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/

## 🔧 下一步

1. **配置GitHub Actions**:
   - 访问: https://github.com/TUARAN/github-auto-follow/settings/secrets/actions
   - 添加 `DOCKER_USERNAME`: `tuaran1453`
   - 添加 `DOCKER_PASSWORD`: 你的Docker Hub密码

2. **在Docker Hub创建仓库**:
   - 访问: https://hub.docker.com/
   - 创建仓库: `tuaran1453/github-follow-tool`

3. **验证自动构建**:
   - 查看: https://github.com/TUARAN/github-auto-follow/actions

## ✨ 功能特性

- 🤖 自动获取推荐用户
- ⏰ 定时自动关注（每5分钟关注10个人）
- 🎯 批量手动关注
- 📊 实时进度显示
- 🔐 GitHub Token安全认证
- 🐳 Docker一键部署
- 🔄 GitHub Actions自动构建
