# Hotboard Core

Hotboard 核心库，提供统一的数据类型和工具函数。

## 安装

```bash
pip install hotboard-core
```

## 功能

- 统一的 `HotItem` 数据类型
- HTTP 请求工具（基于 aiohttp）
- 时间处理工具
- 日志记录

## 使用

```python
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import http_get, get_time
from hotboard.core.logger import logger

# 发送 HTTP 请求
data = await http_get("https://api.example.com")

# 创建热榜项
item = HotItem(
    id="1",
    title="标题",
    url="https://example.com",
    hot="1000"
)
```

## 许可证

Apache-2.0
