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
| `FIXED_TOKEN` | 无（必填） | 自动执行（tuaran账号）使用的固定GitHub Token |
| `AUTO_START_DATE` | `2025-10-28` | 自动模式开始日期 |
| `DAILY_FOLLOW_LIMIT` | `10` | 自动模式每天关注人数 |
| `DATA_FILE` | `auto_follow_data.json` | 自动模式数据文件名 |

### 速率限制

- GitHub API限制：5000次请求/小时（认证用户）
- 默认请求间隔：0.5秒
- 建议单次操作不超过100个用户

## 🛡️ 安全考虑

1. **Token安全**
   - 固定 `FIXED_TOKEN` 仅在后端通过环境变量提供，不在仓库或前端暴露
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
