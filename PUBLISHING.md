# 发布到 PyPI 指南

## 前置准备

### 1. 注册 PyPI 账号

- 生产环境: https://pypi.org/account/register/
- 测试环境: https://test.pypi.org/account/register/

### 2. 创建 API Token

生产环境 (PyPI):
1. 访问 https://pypi.org/manage/account/token/
2. 创建 API token，scope 选择 "Entire account" 或指定项目
3. 保存 token（只显示一次）

测试环境 (TestPyPI):
1. 访问 https://test.pypi.org/manage/account/token/
2. 同样创建 token

### 3. 配置 PyPI 凭证

创建 `~/.pypirc` 文件：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...  # 你的 PyPI token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...  # 你的 TestPyPI token
```

设置文件权限：
```bash
chmod 600 ~/.pypirc
```

### 4. 安装发布工具

```bash
pip install build twine
```

## 发布流程

### 方式 1: 使用脚本（推荐）

#### 测试发布（TestPyPI）

先在测试环境验证：

```bash
# 发布单个包到 TestPyPI
bash scripts/publish_test.sh core
bash scripts/publish_test.sh github

# 测试安装
pip install --index-url https://test.pypi.org/simple/ hotboard-core
pip install --index-url https://test.pypi.org/simple/ hotboard-github
```

#### 正式发布（PyPI）

```bash
# 发布核心包（必须先发布，其他包依赖它）
bash scripts/publish_to_pypi.sh core

# 发布单个平台包
bash scripts/publish_to_pypi.sh github
bash scripts/publish_to_pypi.sh baidu

# 发布所有包（慎用）
bash scripts/publish_to_pypi.sh all
```

### 方式 2: 手动发布

```bash
# 1. 进入包目录
cd packages/hotboard/core

# 2. 清理旧文件
rm -rf dist build *.egg-info

# 3. 构建包
python -m build

# 4. 检查包
twine check dist/*

# 5. 上传到 TestPyPI（测试）
twine upload --repository testpypi dist/*

# 6. 测试安装
pip install --index-url https://test.pypi.org/simple/ hotboard-core

# 7. 上传到 PyPI（正式）
twine upload dist/*
```

## 发布顺序

**重要**: 必须按以下顺序发布，因为存在依赖关系：

1. **hotboard-core** (核心包，所有平台依赖)
2. 各平台包（任意顺序）

```bash
# 正确的发布顺序
bash scripts/publish_to_pypi.sh core
bash scripts/publish_to_pypi.sh github
bash scripts/publish_to_pypi.sh baidu
# ... 其他平台
```

## 版本管理

### 更新版本号

修改 `pyproject.toml` 中的 `version` 字段：

```toml
[project]
name = "hotboard-core"
version = "0.1.1"  # 更新这里
```

### 版本号规范

遵循 [语义化版本](https://semver.org/lang/zh-CN/)：

- `0.1.0` → `0.1.1`: 修复 bug
- `0.1.0` → `0.2.0`: 新增功能（向下兼容）
- `0.1.0` → `1.0.0`: 重大变更（不兼容）

### 批量更新版本号

```bash
# 更新所有包到 0.1.1
find packages/hotboard -name "pyproject.toml" -exec sed -i '' 's/version = "0.1.0"/version = "0.1.1"/g' {} \;
```

## 验证发布

### 检查包是否可用

```bash
# 搜索包
pip search hotboard-core  # 注意: PyPI 已禁用搜索

# 查看包信息
pip show hotboard-core

# 访问 PyPI 页面
open https://pypi.org/project/hotboard-core/
```

### 测试安装

```bash
# 创建新的虚拟环境测试
python -m venv test_env
source test_env/bin/activate

# 安装并测试
pip install hotboard-core
pip install hotboard-github
hotboard-github --help
```

## 常见问题

### 1. 包名已存在

错误: `The name 'hotboard-xxx' is already taken`

解决: 包名在 PyPI 上是全局唯一的，需要更换名称或联系原作者。

### 2. 版本号已存在

错误: `File already exists`

解决: PyPI 不允许覆盖已发布的版本，必须更新版本号。

### 3. 依赖包找不到

错误: `Could not find a version that satisfies the requirement hotboard-core`

解决: 确保先发布 `hotboard-core` 包。

### 4. Token 认证失败

错误: `Invalid or non-existent authentication information`

解决:
- 检查 `~/.pypirc` 配置
- 确认 token 正确且未过期
- Token 必须以 `pypi-` 开头

### 5. 构建失败

错误: `No module named 'build'`

解决:
```bash
pip install --upgrade build twine setuptools wheel
```

## 撤回发布

PyPI 不支持删除已发布的版本（防止破坏依赖），只能：

1. 发布新版本修复问题
2. 联系 PyPI 管理员（仅限严重安全问题）

## CI/CD 自动发布

### GitHub Actions 配置

创建 `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install build twine
      
      - name: Build and publish
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: |
          bash scripts/publish_to_pypi.sh all
```

在 GitHub 仓库设置中添加 Secret:
- Name: `PYPI_API_TOKEN`
- Value: 你的 PyPI API token

## 参考资料

- [PyPI 官方文档](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine 文档](https://twine.readthedocs.io/)
- [语义化版本](https://semver.org/lang/zh-CN/)
