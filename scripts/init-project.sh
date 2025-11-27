#!/bin/bash

# CozyCognee 项目初始化脚本
# 用于初始化 project/cognee 目录（Cognee 官方项目副本）

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$PROJECT_ROOT/project/cognee"
COGNEE_REPO="https://github.com/topoteretes/cognee.git"

echo "🚀 初始化 CozyCognee 项目..."

# 检查 project 目录是否存在
if [ ! -d "$PROJECT_ROOT/project" ]; then
    echo "📁 创建 project 目录..."
    mkdir -p "$PROJECT_ROOT/project"
fi

# 检查 project/cognee 目录
if [ -d "$PROJECT_DIR" ]; then
    if [ -d "$PROJECT_DIR/.git" ]; then
        echo "✅ project/cognee 目录已存在且是一个 Git 仓库"
        echo "📍 当前分支: $(cd "$PROJECT_DIR" && git branch --show-current)"
        echo ""
        read -p "是否要更新到最新版本? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🔄 更新 Cognee 代码..."
            cd "$PROJECT_DIR"
            
            # 检查是否有 upstream 远程仓库
            if ! git remote | grep -q upstream; then
                echo "➕ 添加 upstream 远程仓库..."
                git remote add upstream "$COGNEE_REPO" 2>/dev/null || true
            fi
            
            # 获取最新代码
            echo "📥 获取最新代码..."
            git fetch upstream
            
            # 合并最新代码
            CURRENT_BRANCH=$(git branch --show-current)
            echo "🔄 合并 upstream/main 到 $CURRENT_BRANCH..."
            git merge upstream/main || {
                echo "⚠️  合并冲突，请手动解决后继续"
                exit 1
            }
            
            echo "✅ 更新完成"
        fi
    else
        echo "⚠️  project/cognee 目录已存在但不是 Git 仓库"
        read -p "是否要删除并重新克隆? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$PROJECT_DIR"
        else
            echo "❌ 取消初始化"
            exit 1
        fi
    fi
fi

# 如果目录不存在，克隆仓库
if [ ! -d "$PROJECT_DIR" ]; then
    echo "📥 克隆 Cognee 官方仓库..."
    echo "   仓库地址: $COGNEE_REPO"
    echo "   目标目录: $PROJECT_DIR"
    echo ""
    
    git clone "$COGNEE_REPO" "$PROJECT_DIR"
    
    cd "$PROJECT_DIR"
    
    # 添加 upstream 远程仓库（如果还没有）
    if ! git remote | grep -q upstream; then
        echo "➕ 添加 upstream 远程仓库..."
        git remote add upstream "$COGNEE_REPO" 2>/dev/null || true
    fi
    
    echo "✅ 克隆完成"
fi

# 显示当前状态
echo ""
echo "📊 项目状态:"
cd "$PROJECT_DIR"
echo "   当前分支: $(git branch --show-current)"
echo "   最新提交: $(git log -1 --oneline)"
echo "   远程仓库:"
git remote -v | sed 's/^/     /'

echo ""
echo "🎉 项目初始化完成！"
echo ""
echo "💡 提示:"
echo "   - 使用 'cd project/cognee && git fetch upstream && git merge upstream/main' 同步最新代码"
echo "   - 查看开发文档: docs/development/README.md"
echo "   - 开始部署: cd deployment && ./scripts/start.sh"

