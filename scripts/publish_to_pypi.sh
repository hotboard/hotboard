#!/bin/bash
# 发布 Hotboard 包到 PyPI
# 使用方法: bash scripts/publish_to_pypi.sh [package-name]
# 示例: bash scripts/publish_to_pypi.sh github

set -e

PACKAGE_NAME=$1

if [ -z "$PACKAGE_NAME" ]; then
    echo "错误: 请指定要发布的包名"
    echo "使用方法: bash scripts/publish_to_pypi.sh [package-name]"
    echo "示例: bash scripts/publish_to_pypi.sh github"
    echo ""
    echo "可用的包:"
    echo "  - core (核心包，其他包依赖)"
    echo "  - github, baidu, zhihu, ... (各平台包)"
    echo "  - all (发布所有包)"
    exit 1
fi

# 检查是否安装了 build 和 twine
python -c "import build" 2>/dev/null || pip install build
python -c "import twine" 2>/dev/null || pip install twine

# 发布单个包
publish_package() {
    local pkg_path=$1
    local pkg_name=$(basename $pkg_path)
    
    echo "=========================================="
    echo "发布包: $pkg_name"
    echo "路径: $pkg_path"
    echo "=========================================="
    
    # 清理旧的构建文件
    rm -rf $pkg_path/dist $pkg_path/build $pkg_path/*.egg-info
    
    # 构建包
    echo "构建包..."
    python -m build $pkg_path
    
    # 检查包
    echo "检查包..."
    twine check $pkg_path/dist/*
    
    # 上传到 PyPI
    echo "上传到 PyPI..."
    twine upload $pkg_path/dist/*
    
    echo "✓ $pkg_name 发布成功"
    echo ""
}

# 发布所有包
if [ "$PACKAGE_NAME" = "all" ]; then
    echo "发布所有包到 PyPI..."
    echo ""
    
    # 先发布 core 包（其他包依赖它）
    publish_package "src"
    
    # 发布其他包
    for pkg_dir in packages/hotboard/*/; do
        if [ -f "$pkg_dir/pyproject.toml" ]; then
            publish_package "$pkg_dir"
        fi
    done
    
    echo "=========================================="
    echo "所有包发布完成！"
    echo "=========================================="
else
    # 发布指定包
    PKG_PATH="packages/hotboard/$PACKAGE_NAME"
    
    # core 包在 src 目录
    if [ "$PACKAGE_NAME" = "core" ]; then
        PKG_PATH="src"
    fi
    
    if [ ! -d "$PKG_PATH" ]; then
        echo "错误: 包 $PACKAGE_NAME 不存在"
        echo "路径: $PKG_PATH"
        exit 1
    fi
    
    if [ ! -f "$PKG_PATH/pyproject.toml" ]; then
        echo "错误: $PKG_PATH 中没有 pyproject.toml"
        exit 1
    fi
    
    publish_package "$PKG_PATH"
fi
