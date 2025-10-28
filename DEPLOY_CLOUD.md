# 🌐 公网部署指南

## 🚀 推荐部署方案

### 方案1：Railway（推荐）
**优点**: 免费额度大，部署简单，自动HTTPS
**缺点**: 免费版有休眠机制

**部署步骤**:
1. 访问 [Railway](https://railway.app/)
2. 使用GitHub登录
3. 点击 "New Project" → "Deploy from GitHub repo"
4. 选择 `TUARAN/github-auto-follow` 仓库
5. 使用 `Dockerfile.cloud` 作为构建文件
6. 部署完成后获得公网地址

### 方案2：Render
**优点**: 免费，稳定，自动HTTPS
**缺点**: 免费版有休眠机制

**部署步骤**:
1. 访问 [Render](https://render.com/)
2. 使用GitHub登录
3. 点击 "New" → "Web Service"
4. 连接GitHub仓库 `TUARAN/github-auto-follow`
5. 使用 `render.yaml` 配置
6. 部署完成后获得公网地址

### 方案3：Fly.io
**优点**: 免费额度大，全球CDN
**缺点**: 需要命令行操作

**部署步骤**:
1. 安装 [Fly CLI](https://fly.io/docs/hands-on/install-flyctl/)
2. 运行 `fly auth login`
3. 运行 `fly launch` 使用 `fly.toml` 配置
4. 运行 `fly deploy`
5. 获得公网地址

## 🔧 部署前准备

### 1. 确保GitHub Actions配置
- 在GitHub仓库设置中添加Docker Hub secrets
- 确保自动构建正常工作

### 2. 选择部署平台
- **新手推荐**: Railway
- **稳定性优先**: Render  
- **性能优先**: Fly.io

## 📋 部署后配置

### 1. 更新README
部署成功后，更新README中的在线演示地址

### 2. 配置自定义域名（可选）
- 购买域名
- 在部署平台配置DNS
- 启用HTTPS

### 3. 监控和维护
- 设置健康检查
- 配置日志监控
- 定期更新依赖

## 🎯 预期结果

部署成功后，你将获得：
- 公网可访问的GitHub自动关注工具
- 自动HTTPS证书
- 全球CDN加速
- 自动扩缩容
- 完整的监控和日志
