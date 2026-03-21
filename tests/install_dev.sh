#!/bin/bash
# 安装开发环境

set -e

echo "安装开发环境..."

# 安装核心包
echo "安装核心包..."
pip install -e packages/hotboard/core

# 安装开发工具
echo "安装开发工具..."
pip install black ruff pyright pytest pytest-cov

echo "开发环境安装完成！"
echo ""
echo "可用命令:"
echo "  black .          # 格式化代码"
echo "  ruff check .     # 代码检查"
echo "  pyright          # 类型检查"
echo "  pytest           # 运行测试"
