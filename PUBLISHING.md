# 发布指南

## 准备

1. 注册 PyPI 账号：[https://pypi.org/account/register/](https://pypi.org/account/register/)
2. 注册 TestPyPI 账号：[https://test.pypi.org/account/register/](https://test.pypi.org/account/register/)
3. 创建 API Token：
   - PyPI: [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
   - TestPyPI: [https://test.pypi.org/manage/account/token/](https://test.pypi.org/manage/account/token/)
4. 配置 `~/.pypirc`：

    ```ini
    [distutils]
    index-servers =
        pypi
        testpypi

    [pypi]
    username = __token__
    password = pypi-AgEIcHlwaS5vcmcC...

    [testpypi]
    repository = https://test.pypi.org/legacy/
    username = __token__
    password = pypi-AgEIcHlwaS5vcmcC...
    ```

5. 安装工具：

```bash
pip install build twine
```

## 测试发布（TestPyPI）

```bash
# 更新版本号
# 编辑 pyproject.toml 中的 version

# 构建
python -m build

# 检查
twine check dist/*

# 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ hotboard

# 测试运行
hotboard list
hotboard github
```

## 正式发布（PyPI）

```bash
# 确认版本号正确
# 编辑 pyproject.toml 中的 version

# 构建
python -m build

# 检查
twine check dist/*

# 上传到 PyPI
twine upload dist/*

# 验证
pip install hotboard
hotboard list
```

## 版本号规范

遵循语义化版本：

- `0.0.1` → `0.0.2`: 修复 bug
- `0.0.1` → `0.1.0`: 新增功能（向下兼容）
- `0.0.1` → `1.0.0`: 重大变更（不兼容）
