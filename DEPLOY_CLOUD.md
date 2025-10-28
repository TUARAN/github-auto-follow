# 🌐 Cloudflare部署指南

## 🚀 Cloudflare Pages部署（推荐）

**优点**: 免费额度大，全球CDN，自动HTTPS，DDoS防护
**缺点**: 主要适合静态页面，动态功能有限

**部署步骤**:
1. 访问 [Cloudflare Pages](https://pages.cloudflare.com/)
2. 使用GitHub登录
3. 点击 "Create a project"
4. 选择 `TUARAN/github-auto-follow` 仓库
5. 配置构建设置：
   - Build command: `docker build -f Dockerfile.cloudflare -t github-follow-tool .`
   - Build output directory: `/app/frontend`
6. 点击 "Save and Deploy"
7. 获得公网地址

## ⚡ Cloudflare Workers部署

**优点**: 边缘计算，全球分布，高性能
**缺点**: 需要重构为Workers格式

**部署步骤**:
1. 安装 [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/install-and-update/)
2. 运行 `wrangler login`
3. 运行 `wrangler deploy`
4. 获得公网地址

## 🔧 部署前准备

### 1. 确保GitHub Actions配置
- 在GitHub仓库设置中添加Docker Hub secrets
- 确保自动构建正常工作

### 2. Cloudflare账户准备
- 注册 [Cloudflare账户](https://dash.cloudflare.com/sign-up)
- 验证邮箱地址

## 📋 部署后配置

### 1. 更新README
部署成功后，更新README中的在线演示地址

### 2. 配置自定义域名（可选）
- 在Cloudflare添加域名
- 配置DNS记录
- 启用HTTPS

### 3. 监控和维护
- 查看Cloudflare Analytics
- 监控性能指标
- 定期更新依赖

## 🎯 预期结果

部署成功后，你将获得：
- ✅ 公网可访问的GitHub自动关注工具
- ✅ 自动HTTPS证书
- ✅ 全球CDN加速
- ✅ DDoS防护
- ✅ 完整的监控和分析
