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

# 构建（临时取消代理）
echo "构建包..."
env -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy python -m build

# 检查
echo "检查包..."
twine check dist/*

# 上传
echo "上传到 PyPI..."
if [ -n "$HTTPS_PROXY" ] || [ -n "$https_proxy" ]; then
    twine upload dist/*
else
    echo "提示：如需使用代理，请设置 HTTPS_PROXY 环境变量"
    twine upload dist/*
fi

echo "发布完成！"
