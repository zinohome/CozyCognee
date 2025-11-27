#!/bin/bash

# CozyCognee 停止脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$DEPLOYMENT_DIR"

echo "🛑 停止 CozyCognee 服务..."

docker-compose down

echo "✅ 所有服务已停止"

