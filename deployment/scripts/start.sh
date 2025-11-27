#!/bin/bash

# CozyCognee 启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$DEPLOYMENT_DIR"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件，正在从 env.example 创建..."
    cp env.example .env
    echo "✅ 已创建 .env 文件，请编辑配置后再运行此脚本"
    exit 1
fi

# 检查必需的环境变量
if ! grep -q "LLM_API_KEY=" .env || grep -q "LLM_API_KEY=your-llm-api-key-here" .env; then
    echo "⚠️  请先配置 LLM_API_KEY 环境变量"
    exit 1
fi

echo "🚀 启动 CozyCognee 服务..."

# 启动核心服务
echo "📦 启动 Cognee 后端服务..."
docker-compose up -d cognee

# 等待服务就绪
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
if docker-compose ps | grep -q "cognee.*Up"; then
    echo "✅ Cognee 后端服务已启动"
    echo "📍 API 地址: http://localhost:8000"
    echo "📍 API 文档: http://localhost:8000/docs"
else
    echo "❌ Cognee 后端服务启动失败"
    docker-compose logs cognee
    exit 1
fi

# 询问是否启动其他服务
read -p "是否启动前端服务? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 启动前端服务..."
    docker-compose --profile ui up -d frontend
    echo "📍 前端地址: http://localhost:3000"
fi

read -p "是否启动数据库服务? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 启动数据库服务..."
    docker-compose --profile postgres up -d postgres
    docker-compose --profile neo4j up -d neo4j
    docker-compose --profile chromadb up -d chromadb
    echo "✅ 数据库服务已启动"
fi

echo ""
echo "🎉 服务启动完成！"
echo ""
echo "查看服务状态: docker-compose ps"
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"

