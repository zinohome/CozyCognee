#!/bin/bash

# CozyCognee 重启脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$DEPLOYMENT_DIR"

echo "🔄 重启 CozyCognee 服务..."

docker-compose restart

echo "✅ 服务已重启"

