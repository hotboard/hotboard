#!/bin/bash
# 安装开发环境

set -e

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "安装开发环境..."

# 安装核心包
echo "安装核心包..."
pip install -e "$PROJECT_ROOT/src"

# 安装所有平台包
echo "安装所有平台包..."
for dir in "$PROJECT_ROOT/packages/hotboard/"*/; do
    if [ -f "${dir}pyproject.toml" ]; then
        echo "安装 ${dir}..."
        pip install -e "${dir}"
    fi
done

# 安装开发工具
echo "安装开发工具..."
pip install black ruff isort pyright pytest pytest-cov

echo "开发环境安装完成！"
echo ""
echo "可用命令:"
echo "  black .          # 格式化代码"
echo "  ruff check .     # 代码检查"
echo "  isort .          # 格式化 import"
echo "  pyright          # 类型检查"
echo "  pytest           # 运行测试"
