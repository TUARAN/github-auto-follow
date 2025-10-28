#!/bin/bash

# TUARAN GitHub 自动关注工具 - 快速部署脚本

echo "🚀 开始部署 GitHub 自动关注工具..."

# 检查Git状态
echo "📋 检查Git状态..."
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ 有未提交的更改，请先提交代码"
    git status
    exit 1
fi

# 推送到远程仓库
echo "📤 推送代码到远程仓库..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ 代码推送成功！"
else
    echo "❌ 代码推送失败"
    exit 1
fi

# 显示部署信息
echo ""
echo "🎉 部署准备完成！"
echo ""
echo "📝 下一步操作："
echo "1. 访问 https://dashboard.render.com"
echo "2. 创建新的 Web Service"
echo "3. 连接你的GitHub仓库"
echo "4. 使用以下配置："
echo ""
echo "   Name: github-follow-tool"
echo "   Environment: Python"
echo "   Plan: Free"
echo "   Build Command: pip install -r backend/requirements.txt"
echo "   Start Command: python3 -m uvicorn backend.main:app --host 0.0.0.0 --port \$PORT"
echo "   Health Check Path: /"
echo ""
echo "   Environment Variables:"
echo "   - PORT: 10000"
echo "   - PYTHON_VERSION: 3.9.18"
echo ""
echo "   Static Publish Path: frontend/"
echo "   Routes: /* -> /index.html"
echo ""
echo "🔗 部署完成后访问你的服务URL即可使用！"
echo ""
echo "✨ 功能特性："
echo "- 从2025年10月28日开始自动运行"
echo "- 每天关注10个GitHub用户（TUARAN账号）"
echo "- 实时状态监控和统计"
echo "- 完整的Web界面"
echo ""
