#!/bin/bash

# CozyCognee 单个镜像构建脚本
# 用法: ./build-image.sh <service> [version]
# 服务: cognee, cognee-frontend, cognee-mcp

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$DEPLOYMENT_DIR")"

# 参数
SERVICE=$1
VERSION=${2:-latest}

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查参数
if [ -z "$SERVICE" ]; then
    echo -e "${RED}❌ 错误: 请指定服务名称${NC}"
    echo "用法: $0 <service> [version]"
    echo "服务: cognee, cognee-frontend, cognee-mcp"
    exit 1
fi

# 服务配置
case $SERVICE in
    cognee)
        DOCKERFILE="docker/cognee/Dockerfile"
        IMAGE_NAME="cognee"
        ;;
    cognee-frontend|frontend)
        DOCKERFILE="docker/cognee-frontend/Dockerfile"
        IMAGE_NAME="cognee-frontend"
        ;;
    cognee-mcp|mcp)
        DOCKERFILE="docker/cognee-mcp/Dockerfile"
        IMAGE_NAME="cognee-mcp"
        ;;
    *)
        echo -e "${RED}❌ 错误: 未知的服务名称 '$SERVICE'${NC}"
        echo "支持的服务: cognee, cognee-frontend, cognee-mcp"
        exit 1
        ;;
esac

echo -e "${GREEN}🚀 构建 $IMAGE_NAME 镜像${NC}"
echo "版本: $VERSION"
echo "Dockerfile: $DOCKERFILE"
echo ""

# 检查 project 目录
if [ ! -d "$PROJECT_ROOT/project/cognee" ]; then
    echo -e "${RED}❌ 错误: project/cognee 目录不存在${NC}"
    echo "请先运行: ./scripts/init-project.sh"
    exit 1
fi

cd "$DEPLOYMENT_DIR"

# 构建镜像
echo -e "${YELLOW}📦 开始构建...${NC}"
docker build \
    -f "$DOCKERFILE" \
    -t "$IMAGE_NAME:$VERSION" \
    -t "$IMAGE_NAME:latest" \
    --label "org.opencontainers.image.created=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --label "org.opencontainers.image.version=$VERSION" \
    --label "org.opencontainers.image.revision=$(git rev-parse HEAD 2>/dev/null || echo 'unknown')" \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 镜像构建成功${NC}"
    echo ""
    echo "镜像信息:"
    docker images | grep "$IMAGE_NAME" | grep -E "$VERSION|latest" || true
else
    echo -e "${RED}❌ 镜像构建失败${NC}"
    exit 1
fi

