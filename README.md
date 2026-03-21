# Hotboard

[![Test](https://github.com/hotboard/hotboard/actions/workflows/test.yml/badge.svg)](https://github.com/hotboard/hotboard/actions/workflows/test.yml)
[![Lint](https://github.com/hotboard/hotboard/actions/workflows/lint.yml/badge.svg)](https://github.com/hotboard/hotboard/actions/workflows/lint.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

Hotboard 是一个统一的热榜数据获取工具，支持 47+ 个平台的热榜数据抓取。

## ✨ 特性

- 🎯 统一接口：所有平台使用相同的 CLI 命令格式
- 📦 模块化设计：每个平台独立打包，按需安装
- 🔄 多种输出格式：支持 JSON 和 Markdown 格式
- 🚀 异步高效：基于 aiohttp 的异步请求
- 🛠️ 类型安全：完整的类型注解支持
- 🔌 OpenClaw 集成：可作为 OpenClaw skill 使用（[https://github.com/hotboard/hotboard-skills](https://github.com/hotboard/hotboard-skills)）

## 📋 支持的平台

### 综合资讯
百度热搜、微博热搜、知乎热榜、腾讯新闻、新浪、新浪新闻、澎湃新闻、网易新闻

### 视频娱乐
B 站、抖音、快手、AcFun

### 科技媒体
36kr、虎嗅、极客公园、爱范儿、少数派、IT 之家、数字尾巴

### 开发者社区
GitHub Trending、Hacker News、掘金、CSDN、V2EX、Linux.do、NodeSeek、HelloGitHub、51CTO、HostLoc

### 游戏社区
NGA、LOL、米游社、游研社

### 体育社区
虎扑

### 社交阅读
豆瓣、贴吧、简书、果壳、新水木、微信读书

### 国际平台
New York Times

### 实用工具
地震速报、天气预警、历史上的今天

### 其他
吾爱破解

## 🚀 快速开始

### 安装

从 PyPI 安装（推荐）：

```bash
# 安装特定平台（会自动安装 core 依赖）
pip install hotboard-github
pip install hotboard-baidu
pip install hotboard-zhihu
```

从源码安装（开发者）：

```bash
# 克隆仓库
git clone https://github.com/hotboard/hotboard.git
cd hotboard

# 安装核心包
pip install -e packages/hotboard/core

# 安装特定平台
pip install -e packages/hotboard/github

# 或安装所有平台
bash tests/install_all.sh
```

### 使用

获取热榜数据（Markdown 格式）：
```bash
hotboard-github
hotboard-baidu
hotboard-zhihu
```

获取 JSON 格式：
```bash
hotboard-github --format json
```

查看帮助：
```bash
hotboard-github --help
```

## 🤖 OpenClaw 集成

Hotboard 支持作为 OpenClaw skill 使用，实现自然语言交互。

Skills 位于独立仓库：[hotboard/hotboard-skills](https://github.com/hotboard/hotboard-skills)

### 安装方式

从 ClawHub 安装（推荐）：
```bash
clawhub install hotboard-github
clawhub install hotboard-baidu
```

从 GitHub 安装：
```bash
cd ~/.openclaw/skills/
git clone https://github.com/hotboard/hotboard-skills
```

### 使用示例
- "帮我看看 GitHub 上有什么热门项目"
- "查看知乎热榜"
- "推荐一些适合程序员的热榜平台"

## 📦 项目结构

```
hotboard/
├── packages/hotboard/          # 所有平台包（发布到 PyPI）
│   ├── core/                   # 核心库
│   ├── github/                 # GitHub 平台
│   ├── baidu/                  # 百度平台
│   └── ...                     # 其他 46 个平台
├── tests/                      # 测试和安装脚本
├── scripts/                    # 发布脚本
├── DEVELOPMENT.md              # 开发规范
├── CONTRIBUTING.md             # 贡献指南
└── README.md                   # 本文件
```

## 🔧 开发

查看 [DEVELOPMENT.md](DEVELOPMENT.md) 了解开发规范。

安装开发依赖：
```bash
bash tests/install_dev.sh
```

运行测试：
```bash
pytest tests/
```

代码检查：
```bash
black .
ruff check .
pyright packages/hotboard/core
```

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与项目。

### 添加新平台

1. 在 `packages/hotboard/` 下创建新平台目录
2. 遵循 [DEVELOPMENT.md](DEVELOPMENT.md) 中的规范
3. 添加测试用例
4. 提交 Pull Request

## 📄 许可证

本项目采用 [Apache-2.0](LICENSE) 许可证。

## ⚠️ 免责声明

- 本项目仅供学习交流使用
- 使用时请遵守各平台的服务条款和 robots.txt
- 请合理控制请求频率，避免对目标平台造成压力
- 数据来源于各平台公开接口，不保证实时性和完整性

## 🔗 相关链接

- [PyPI 主页](https://pypi.org/search/?q=hotboard)
- [Skills 仓库](https://github.com/hotboard/hotboard-skills)
- [问题反馈](https://github.com/hotboard/hotboard/issues)
- [更新日志](CHANGELOG.md)
- [安全政策](SECURITY.md)
- [发布指南](PUBLISHING.md)
