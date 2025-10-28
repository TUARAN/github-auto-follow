# Render 部署配置

## 🚀 Render 一键部署 (完全免费)

Render 是最佳的全栈部署方案，**完全免费**且支持Python！

### 部署步骤

1. **访问 Render**
   - 打开 [render.com](https://render.com)
   - 使用 GitHub 账号登录

2. **创建新服务**
   - 点击 "New +"
   - 选择 "Web Service"
   - 连接你的 GitHub 仓库 `TUARAN/github-auto-follow`

3. **配置服务**
   - **Name**: `github-follow-tool`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `python3 -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`

4. **自动部署**
   - Render 会自动检测 `render.yaml` 配置
   - 自动安装依赖并启动服务
   - 提供公网访问地址

### 访问地址

部署完成后，你会得到类似这样的地址：
- `https://github-follow-tool.onrender.com`

### 配置说明

- **构建器**: Python 3.9
- **启动命令**: FastAPI 后端服务
- **静态文件**: 自动服务前端文件
- **健康检查**: 自动检测服务状态
- **免费额度**: 750小时/月 (完全够用)

### 环境变量

可以在 Render 控制台添加：
- `PORT`: Render 自动设置
- `GITHUB_TOKEN`: 你的 GitHub Personal Access Token (可选)

### 优势

✅ **完全免费**: 750小时/月免费额度  
✅ **一键部署**: 前后端一起部署  
✅ **自动构建**: 支持 Python 依赖  
✅ **自动重启**: 服务异常自动重启  
✅ **HTTPS**: 自动提供 HTTPS 证书  
✅ **全球CDN**: 快速访问  

### 注意事项

- 免费服务在15分钟无访问后会自动休眠
- 重新访问时会自动唤醒 (需要几秒钟)
- 对于个人项目完全够用

### 部署后测试

1. 访问你的 Render URL
2. 输入 GitHub Token
3. 测试关注功能
4. 享受免费的全栈服务！
