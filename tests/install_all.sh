#!/bin/bash
# 安装所有 hotboard 包

set -e

echo "开始安装所有 hotboard 包..."

# 安装所有平台包
for dir in packages/hotboard/*/; do
    if [ -f "$dir/pyproject.toml" ]; then
        echo "安装 $dir..."
        pip install -e "$dir"
    fi
done

echo "所有包安装完成！"
