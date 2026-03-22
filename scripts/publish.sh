#!/bin/bash
set -e

echo "发布 hotboard 到 PyPI..."

# 代码检查和格式化
echo "代码格式化..."
black .
isort .

echo "代码检查..."
ruff check .

echo "类型检查..."
pyright

# 运行测试
echo "运行测试..."
pytest tests/

# 清理旧文件
rm -rf dist build *.egg-info

# 构建
echo "构建包..."
python -m build

# 检查
echo "检查包..."
twine check dist/*

# 上传
echo "上传到 PyPI..."
twine upload dist/*

echo "发布完成！"
