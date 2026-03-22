#!/bin/bash
set -e

echo "安装开发环境..."
pip install -e .
pip install pytest ruff black isort pyright

echo ""
echo "开发环境安装完成！"
echo ""
echo "可用命令："
echo "  pytest tests/       # 运行测试"
echo "  ruff check .        # 代码检查"
echo "  black .             # 格式化代码"
echo "  isort .             # 排序 import"
echo "  pyright             # 类型检查"
echo "  hotboard list       # 测试 CLI"
