# 开发指南

本文档描述 Hotboard 平台实现的统一规范和最佳实践。

## 1. 文件结构

每个平台模块应遵循以下结构：

```python
# import 顺序：标准库 -> 第三方库 -> 本地库
import asyncio
import typer
from typing import TypedDict
from enum import StrEnum

from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import http_get, http_post, get_time, format_items_json
from hotboard.core.logger import logger

# 常量定义
PLATFORM_NAME = "平台名称"

# 枚举定义（可选，用于多榜单类型）
class RankType(StrEnum):
    """榜单类型枚举"""
    DEFAULT = "default"
    POPULAR = "popular"

# 配置定义（可选，用于榜单配置映射）
class RankConfig(TypedDict):
    """榜单配置类型"""
    name: str
    endpoint: str

RANK_CONFIGS: dict[str, RankConfig] = {
    RankType.DEFAULT: {"name": "默认榜", "endpoint": "/api/default"},
    RankType.POPULAR: {"name": "热门榜", "endpoint": "/api/popular"},
}

# 核心函数
async def fetch(rank_type: str = "default") -> list[HotItem]:
    """获取热榜数据"""
    ...

def format_output(items: list[HotItem], type_name: str, format: OutputFormat) -> str:
    """格式化输出"""
    ...

def main(...):
    """CLI 主函数"""
    ...

def run():
    """CLI 入口点"""
    typer.run(main)
```

## 2. 常量定义

- `PLATFORM_NAME`：平台名称，用于日志和输出标题
- `RankType`：榜单类型枚举（可选，仅当平台有多个榜单时定义）
- `RANK_CONFIGS`：榜单配置字典（可选，用于映射榜单类型到具体配置）

## 3. fetch 函数

`fetch` 函数负责从数据源获取热榜数据并转换为标准格式：

```python
async def fetch(rank_type: str = "default") -> list[HotItem]:
    """获取热榜数据
    
    Args:
        rank_type: 榜单类型标识
        
    Returns:
        标准化的 HotItem 列表
    """
    # 1. 构建请求参数
    url: str = "https://api.example.com/hotlist"
    headers: dict[str, str] = {"User-Agent": "..."}
    
    # 2. 发送 HTTP 请求
    result: dict[str, any] = await http_get(url, headers)
    
    # 3. 解析响应数据
    raw_items: list[dict[str, any]] = result.get("data", [])
    
    # 4. 转换为标准 HotItem 格式
    items: list[HotItem] = []
    for raw in raw_items:
        items.append(HotItem(
            id=raw.get("id"),
            title=raw.get("title"),
            url=raw.get("url"),
            mobile_url=raw.get("mobile_url"),
            hot=raw.get("hot_score"),
            time=get_time(raw.get("publish_time")),
            cover=raw.get("image"),
            author=raw.get("author"),
            desc=raw.get("description"),
        ))
    return items
```

**实现要点：**
- 完整的类型注解
- 使用 `dict.get()` 安全访问字段，避免 KeyError
- 时间字段统一使用 `get_time()` 转换
- 字段映射：将数据源字段映射到 HotItem 标准字段
- 避免冗余代码：直接返回字段值，不要写 `value if value else None`

## 4. format_output 函数

`format_output` 函数负责将 HotItem 列表格式化为指定输出格式：

```python
def format_output(items: list[HotItem], type_name: str, format: OutputFormat) -> str:
    """格式化输出
    
    Args:
        items: HotItem 列表
        type_name: 榜单类型名称
        format: 输出格式（JSON 或 Markdown）
        
    Returns:
        格式化后的字符串
    """
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, type_name)
    
    # Markdown 格式
    lines: list[str] = [
        f"# {PLATFORM_NAME} - {type_name}\n",
        f"**总数**: {len(items)} 条\n",
    ]
    for item in items:
        lines.append(f"## {item.title}\n")
        if item.hot:
            lines.append(f"- **热度**: {item.hot}")
        if item.author:
            lines.append(f"- **作者**: {item.author}")
        if item.time:
            lines.append(f"- **时间**: {item.time}")
        lines.append(f"- **链接**: {item.url}\n")
    return "\n".join(lines)
```

**实现要点：**
- JSON 格式统一使用 `format_items_json()` 工具函数
- Markdown 格式可根据平台特点自定义显示字段
- 条件显示：仅当字段有值时才输出

## 5. main 函数

`main` 函数是 CLI 的入口，负责参数解析和流程控制：

```python
def main(
    type: RankType = typer.Option(RankType.DEFAULT, help="榜单类型"),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")
):
    """获取热榜数据"""
    items: list[HotItem] = asyncio.run(fetch(type))
    type_name = RANK_CONFIGS[type]["name"]
    print(format_output(items, type_name, format))
    logger.info(f"获取 [{PLATFORM_NAME} - {type_name}] 成功，共 {len(items)} 条")
```

**实现要点：**
- 使用 typer 进行参数解析
- 参数类型使用枚举提供类型安全和自动补全
- 使用 `asyncio.run()` 调用异步函数
- 日志记录使用 `logger.info()`

## 6. 类型注解规范

- 所有函数参数和返回值必须有完整的类型注解
- 局部变量建议添加类型注解以提高代码可读性
- 使用 Python 3.9+ 原生类型：`list[str]` 而不是 `typing.List[str]`
- 使用 `dict[str, any]` 表示 JSON 对象或动态字典
- 使用 `StrEnum` 定义字符串枚举类型

## 7. 命名规范

- 常量：`UPPER_CASE`（如 `PLATFORM_NAME`）
- 类名：`PascalCase`（如 `RankType`、`HotItem`）
- 函数和变量：`snake_case`（如 `fetch`、`format_output`）
- 枚举成员：`UPPER_CASE`（如 `RankType.DEFAULT`）
- 私有函数：`_snake_case`（如 `_parse_data`）

## 8. 中英文排版规范

- 中英文之间必须添加空格（如：`获取 GitHub 热榜`）
- 中文使用全角标点：`，。：；！？`
- 英文使用半角标点：`, . : ; ! ?`
- 数字与单位之间添加空格（如：`100 条`）

## 9. 代码质量要求

- 禁止使用 try-except 捕获异常（让异常自然抛出，由调用方处理）
- 禁止在函数内部 import（所有 import 应在文件顶部）
- 禁止冗余代码：`value if value else None` 应简化为 `value`
- 及时清理未使用的变量、import 语句和注释
- 减少中间变量：对于只使用一次的变量，考虑内联

## 10. 依赖配置

每个平台模块的 `pyproject.toml` 应包含以下依赖：

```toml
[project]
name = "hotboard-platform"
version = "1.0.0"
dependencies = [
    "hotboard-core",
    "typer",
]

[project.scripts]
hotboard-platform = "hotboard.platform.main:run"
```

## 11. HTTP 请求工具

核心库提供了统一的 HTTP 请求工具：

- `http_get(url, headers=None, params=None)`：GET 请求
- `http_post(url, headers=None, data=None, json=None)`：POST 请求

这些工具函数已处理常见错误和超时，直接使用即可。

## 12. 时间处理

使用 `get_time()` 工具函数统一处理时间字段：

```python
from hotboard.core.utils import get_time

# 自动识别时间戳或时间字符串
time_str = get_time(raw_data.get("publish_time"))
```

## 13. 日志记录

使用统一的 logger 进行日志记录：

```python
from hotboard.core.logger import logger

logger.info("操作成功")
logger.warning("警告信息")
logger.error("错误信息")
```

## 14. 测试建议

- 每个平台模块应可独立运行和测试
- 使用 `python -m hotboard.platform.main` 测试 CLI
- 验证输出格式（JSON 和 Markdown）是否正确
- 检查字段映射是否完整（id、title、url 等）
