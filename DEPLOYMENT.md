# 部署说明 - GitHub 自动关注工具

## 部署到 Render

### 1. 准备工作
- 确保代码已推送到GitHub仓库
- 确保render.yaml配置文件正确

### 2. Render部署步骤

1. **登录Render控制台**
   - 访问 https://dashboard.render.com
   - 使用GitHub账号登录

2. **创建新服务**
   - 点击 "New +" 按钮
   - 选择 "Web Service"
   - 连接你的GitHub仓库

3. **配置服务**
   - **Name**: `github-follow-tool`
   - **Environment**: `Python`
   - **Plan**: `Free`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `python3 -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/`

4. **环境变量**
   - `PORT`: `10000`
   - `PYTHON_VERSION`: `3.9.18`

5. **静态文件**
   - **Static Publish Path**: `frontend/`
   - **Routes**: 添加重写规则 `/*` -> `/index.html`

### 3. 部署后验证

部署完成后，访问你的服务URL，应该能看到：

1. **API健康检查**
   ```bash
   curl https://your-app-name.onrender.com/
   ```
   应该返回: `{"message": "GitHub Follow Tool API", "status": "running"}`

2. **自动关注状态**
   ```bash
   curl https://your-app-name.onrender.com/auto-follow/status
   ```
   应该返回运行状态和统计信息

3. **前端页面**
   访问 `https://your-app-name.onrender.com/` 应该显示完整的Web界面

### 4. 重要注意事项

#### 数据持久化
- Render的免费计划不提供持久化存储
- 数据文件 `auto_follow_data.json` 会在服务重启后丢失
- 建议升级到付费计划或使用外部数据库

#### 自动启动
- 服务部署后会自动启动关注任务
- 从2024年10月28日开始计算运行天数
- 每天关注10个用户

#### 监控和日志
- 在Render控制台可以查看服务日志
- 监控服务运行状态和错误信息

### 5. 故障排除

#### 常见问题
1. **服务启动失败**
   - 检查Python版本是否为3.9.18
   - 确认requirements.txt中的依赖正确

2. **API无法访问**
   - 检查健康检查路径配置
   - 确认端口配置正确

3. **前端页面无法加载**
   - 检查静态文件路径配置
   - 确认路由重写规则正确

#### 日志查看
在Render控制台的 "Logs" 标签页可以查看实时日志。

### 6. 生产环境建议

1. **升级到付费计划**
   - 获得持久化存储
   - 更好的性能和稳定性

2. **使用外部数据库**
   - PostgreSQL或MongoDB
   - 替换JSON文件存储

3. **添加监控**
   - 设置健康检查
   - 配置告警通知

4. **安全配置**
   - 使用环境变量存储敏感信息
   - 配置HTTPS和CORS

## 部署完成后的功能

✅ **自动运行**: 从10月28日开始每天关注10个用户  
✅ **状态监控**: 实时显示运行状态和统计  
✅ **数据持久**: 保存关注历史和每日统计  
✅ **Web界面**: 完整的用户界面和监控面板  
✅ **API接口**: RESTful API支持外部集成  

部署完成后，你的GitHub自动关注工具将完全自动化运行！
