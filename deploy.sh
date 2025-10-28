#!/bin/bash

# GitHub Follow Tool - 快速部署脚本 (tuaran1453)

echo "🚀 GitHub Follow Tool - 快速部署到Docker Hub"
echo "=============================================="
echo "Docker用户名: tuaran1453"
echo ""

# 检查Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行"
    exit 1
fi

# 构建镜像
echo "🔨 构建Docker镜像..."
docker build -t tuaran1453/github-follow-tool:latest .

if [ $? -ne 0 ]; then
    echo "❌ 构建失败"
    exit 1
fi

echo "✅ 构建成功"
echo ""

# 测试镜像
echo "🧪 测试镜像..."
docker run --rm -d -p 8001:8000 -p 3001:3000 --name test-github-follow tuaran1453/github-follow-tool:latest

sleep 5

if curl -f http://localhost:8001/ > /dev/null 2>&1; then
    echo "✅ 镜像测试通过"
    docker stop test-github-follow > /dev/null 2>&1
else
    echo "❌ 镜像测试失败"
    docker stop test-github-follow > /dev/null 2>&1
    exit 1
fi

echo ""
echo "📤 准备推送到Docker Hub..."
echo "请确保已登录Docker Hub: docker login"

read -p "是否继续推送? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker push tuaran1453/github-follow-tool:latest
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 部署成功！"
        echo ""
        echo "📋 使用方法："
        echo "docker run -d -p 8000:8000 -p 3000:3000 --name github-follow-tool tuaran1453/github-follow-tool:latest"
        echo ""
        echo "🌐 访问地址："
        echo "前端: http://localhost:3000"
        echo "API: http://localhost:8000"
        echo "文档: http://localhost:8000/docs"
        echo ""
        echo "🔗 Docker Hub: https://hub.docker.com/r/tuaran1453/github-follow-tool"
    else
        echo "❌ 推送失败"
        exit 1
    fi
else
    echo "⏸️ 跳过推送"
    echo ""
    echo "💡 本地镜像已构建完成，可以手动推送："
    echo "docker push tuaran1453/github-follow-tool:latest"
fi
