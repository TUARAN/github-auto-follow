# GitHub 自动关注工具 - 自动运行功能

## 功能概述

这个工具现在支持自动运行功能，从2024年10月28日开始，每天自动关注10个GitHub用户。

## 主要特性

### 1. 自动运行系统
- **开始日期**: 2024年10月28日
- **运行频率**: 每天一次
- **每次关注**: 10个用户
- **固定Token**: 使用预配置的GitHub Personal Access Token

### 2. 状态监控
- **运行天数**: 显示从开始日期到现在的运行天数
- **总关注数**: 累计关注的用户总数
- **每日统计**: 显示每天的关注数量
- **实时状态**: 显示当前是否正在运行

### 3. 数据持久化
- 所有状态和统计数据都会保存到 `auto_follow_data.json` 文件
- 服务重启后会自动恢复之前的状态
- 支持历史数据查看

## 使用方法

### 启动服务
```bash
cd backend
python3 main.py
```

### 访问前端
打开 `frontend/index.html` 文件，页面会自动显示：
- 运行状态概览
- 已运行天数
- 总关注数
- 每日关注统计
- 最近一批关注结果

### API端点

#### 获取状态
```bash
curl http://localhost:8000/auto-follow/status
```

#### 检查自动启动
```bash
curl -X POST http://localhost:8000/auto-follow/auto-start
```

#### 手动启动
```bash
curl -X POST http://localhost:8000/auto-follow/start
```

#### 停止运行
```bash
curl -X POST http://localhost:8000/auto-follow/stop
```

## 配置说明

### 固定配置
- **Token**: `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`
- **开始日期**: 2024-10-28
- **每日关注数**: 10人
- **运行间隔**: 24小时

### 数据文件
- 状态数据保存在 `backend/auto_follow_data.json`
- 包含运行状态、统计数据、历史记录等

## 监控和统计

### 前端显示
1. **运行状态概览**: 显示开始日期、运行天数、总关注数等
2. **每日统计图表**: 显示每天的关注数量
3. **最近结果**: 显示最近一批关注的用户和结果
4. **实时状态**: 显示当前是否正在运行

### 后端日志
- 所有操作都会记录在日志中
- 包括关注成功/失败、错误信息等

## 注意事项

1. **Token权限**: 确保GitHub token具有 `user:follow` 权限
2. **API限制**: 遵守GitHub API的速率限制
3. **数据备份**: 定期备份 `auto_follow_data.json` 文件
4. **服务监控**: 建议使用进程管理工具确保服务持续运行

## 故障排除

### 常见问题
1. **服务无法启动**: 检查端口8000是否被占用
2. **Token无效**: 验证GitHub token是否有效且有正确权限
3. **数据丢失**: 检查 `auto_follow_data.json` 文件是否存在且可读
4. **关注失败**: 检查网络连接和GitHub API状态

### 日志查看
```bash
tail -f backend/server.log
```

## 更新历史

- **v1.0**: 基础手动关注功能
- **v2.0**: 添加自动运行功能，支持从10月28日开始每天关注10人
