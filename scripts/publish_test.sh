#!/bin/bash
# 发布到 TestPyPI（测试环境）
# 使用方法: bash scripts/publish_test.sh [package-name]

set -e

PACKAGE_NAME=$1

if [ -z "$PACKAGE_NAME" ]; then
    echo "错误: 请指定要发布的包名"
    echo "使用方法: bash scripts/publish_test.sh [package-name]"
    exit 1
fi

# 检查工具
python -c "import build" 2>/dev/null || pip install build
python -c "import twine" 2>/dev/null || pip install twine

PKG_PATH="packages/hotboard/$PACKAGE_NAME"

# core 包在 src 目录
if [ "$PACKAGE_NAME" = "core" ]; then
    PKG_PATH="src"
fi

if [ ! -d "$PKG_PATH" ]; then
    echo "错误: 包 $PACKAGE_NAME 不存在"
    exit 1
fi

echo "发布 $PACKAGE_NAME 到 TestPyPI..."

# 清理
rm -rf $PKG_PATH/dist $PKG_PATH/build $PKG_PATH/*.egg-info

# 构建
python -m build $PKG_PATH

# 检查
twine check $PKG_PATH/dist/*

# 上传到 TestPyPI
twine upload --repository testpypi $PKG_PATH/dist/*

echo "✓ 发布到 TestPyPI 成功"
echo ""
echo "测试安装:"
echo "pip install --index-url https://test.pypi.org/simple/ hotboard-$PACKAGE_NAME"
