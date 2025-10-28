# GitHub Actions 配置说明

## 🔧 设置步骤

### 1. 在Docker Hub创建仓库
- 访问 https://hub.docker.com/
- 登录你的账户 `tuaran1453`
- 创建新仓库 `github-follow-tool`
- 设置为公开仓库

### 2. 在GitHub仓库设置Secrets
- 访问 https://github.com/TUARAN/github-auto-follow/settings/secrets/actions
- 点击 "New repository secret"
- 添加以下secrets：

| Secret名称 | 值 | 说明 |
|-----------|-----|------|
| `DOCKER_USERNAME` | `tuaran1453` | Docker Hub用户名 |
| `DOCKER_PASSWORD` | `你的Docker Hub密码` | Docker Hub密码或访问令牌 |

### 3. 验证配置
- 推送代码到main分支
- 查看Actions页面：https://github.com/TUARAN/github-auto-follow/actions
- 确认构建成功

## 🚀 自动构建特性

- **多架构支持**: linux/amd64, linux/arm64
- **智能缓存**: 使用GitHub Actions缓存加速构建
- **自动标签**: 根据分支和标签自动生成镜像标签
- **构建证明**: 生成构建证明和签名
- **安全扫描**: 自动安全漏洞扫描

## 📋 支持的标签

- `latest` - main分支推送时自动生成
- `v1.0.0` - 创建版本标签时生成
- `main` - main分支推送时生成
- `dev` - dev分支推送时生成

## 🔍 故障排除

如果构建失败，请检查：
1. Docker Hub用户名和密码是否正确
2. Docker Hub仓库是否存在
3. GitHub Actions权限是否足够
4. 网络连接是否正常
