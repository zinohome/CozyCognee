#!/bin/bash

# CozyCognee 镜像构建脚本
# 用于构建所有 Docker 镜像并管理版本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$DEPLOYMENT_DIR")"

# 默认版本
VERSION=${1:-latest}
BUILD_DATE=$(date +%Y%m%d)

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 CozyCognee 镜像构建脚本${NC}"
echo "版本: $VERSION"
echo "构建日期: $BUILD_DATE"
echo ""

# 检查 project 目录
if [ ! -d "$PROJECT_ROOT/project/cognee" ]; then
    echo -e "${RED}❌ 错误: project/cognee 目录不存在${NC}"
    echo "请先运行: ./scripts/init-project.sh"
    exit 1
fi

cd "$DEPLOYMENT_DIR"

# 构建函数
build_image() {
    local service=$1
    local dockerfile=$2
    local image_name=$3
    local version=$4
    
    echo -e "${YELLOW}📦 构建 $service 镜像...${NC}"
    echo "   镜像名称: $image_name:$version"
    echo "   Dockerfile: $dockerfile"
    
    docker build \
        -f "$dockerfile" \
        -t "$image_name:$version" \
        -t "$image_name:latest" \
        --label "org.opencontainers.image.created=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        --label "org.opencontainers.image.version=$version" \
        --label "org.opencontainers.image.revision=$(git rev-parse HEAD 2>/dev/null || echo 'unknown')" \
        .
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $service 镜像构建成功${NC}"
        echo ""
    else
        echo -e "${RED}❌ $service 镜像构建失败${NC}"
        exit 1
    fi
}

# 构建所有镜像
echo "开始构建镜像..."
echo ""

# 1. Cognee 后端
build_image "Cognee" \
    "docker/cognee/Dockerfile" \
    "cognee" \
    "$VERSION"

# 2. Cognee Frontend
build_image "Cognee Frontend" \
    "docker/cognee-frontend/Dockerfile" \
    "cognee-frontend" \
    "$VERSION"

# 3. Cognee MCP
build_image "Cognee MCP" \
    "docker/cognee-mcp/Dockerfile" \
    "cognee-mcp" \
    "$VERSION"

# 显示构建结果
echo -e "${GREEN}🎉 所有镜像构建完成！${NC}"
echo ""
echo "构建的镜像:"
docker images | grep -E "cognee|cognee-frontend|cognee-mcp" | grep -E "$VERSION|latest" || true
echo ""

# 询问是否推送到镜像仓库
read -p "是否要推送到镜像仓库? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "请输入镜像仓库地址 (例如: registry.example.com 或 docker.io/username): " REGISTRY
    
    if [ -n "$REGISTRY" ]; then
        echo "推送镜像到 $REGISTRY..."
        
        # 推送镜像
        for image in cognee cognee-frontend cognee-mcp; do
            echo "推送 $image:$VERSION..."
            docker tag "$image:$VERSION" "$REGISTRY/$image:$VERSION"
            docker tag "$image:latest" "$REGISTRY/$image:latest"
            docker push "$REGISTRY/$image:$VERSION"
            docker push "$REGISTRY/$image:latest"
        done
        
        echo -e "${GREEN}✅ 镜像推送完成${NC}"
    else
        echo "未提供镜像仓库地址，跳过推送"
    fi
fi

echo ""
echo "💡 提示:"
echo "   - 使用 'docker images | grep cognee' 查看构建的镜像"
echo "   - 使用 'docker-compose -f docker-compose.1panel.yml up -d' 启动服务"
echo "   - 版本信息: $VERSION"

