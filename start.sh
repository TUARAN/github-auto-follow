#!/bin/bash

# GitHub Follow Tool 启动脚本

echo "🚀 GitHub 自动关注工具启动脚本"
echo "=================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

echo "✅ Docker 环境检查通过"

# 选择部署模式
echo ""
echo "请选择部署模式："
echo "1) 开发模式 (仅后端和前端)"
echo "2) 生产模式 (包含Nginx反向代理)"
echo "3) 本地开发模式"
echo ""
read -p "请输入选择 (1-3): " choice

case $choice in
    1)
        echo "🔧 启动开发模式..."
        docker-compose up -d
        echo ""
        echo "✅ 服务启动完成！"
        echo "📱 前端界面: http://localhost:3000"
        echo "🔧 API文档: http://localhost:8000/docs"
        ;;
    2)
        echo "🏭 启动生产模式..."
        docker-compose --profile production up -d
        echo ""
        echo "✅ 服务启动完成！"
        echo "🌐 访问地址: http://localhost"
        echo "🔧 API文档: http://localhost/docs"
        ;;
    3)
        echo "💻 启动本地开发模式..."
        echo ""
        echo "请手动执行以下命令："
        echo ""
        echo "1. 启动后端服务："
        echo "   cd backend"
        echo "   pip install -r requirements.txt"
        echo "   uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
        echo ""
        echo "2. 启动前端服务（新终端）："
        echo "   cd frontend"
        echo "   python -m http.server 3000"
        echo ""
        echo "3. 访问应用："
        echo "   前端界面: http://localhost:3000"
        echo "   API文档: http://localhost:8000/docs"
        ;;
    *)
        echo "❌ 无效选择，请重新运行脚本"
        exit 1
        ;;
esac

echo ""
echo "📖 使用说明："
echo "1. 获取GitHub Personal Access Token (需要 user:follow 权限)"
echo "2. 访问前端界面"
echo "3. 输入Token和要关注的用户名"
echo "4. 点击开始关注"
echo ""
echo "🔗 GitHub Token: https://github.com/settings/tokens"
echo ""
echo "🛑 停止服务: docker-compose down"
echo "📊 查看日志: docker-compose logs -f"
