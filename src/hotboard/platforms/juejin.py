import asyncio
from typing import Any

import typer

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, http_get

PLATFORM_NAME = "稀土掘金"


async def get_categories() -> dict[str, str]:
    """获取分类列表"""
    url: str = "https://api.juejin.cn/tag_api/v1/query_category_briefs"
    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    }
    result: dict[str, Any] = await http_get(url, headers)
    data_list: list[dict[str, Any]] = result.get("data", [])
    categories: dict[str, str] = {"1": "综合"}
    for item in data_list:
        category_id: str | None = item.get("category_id")
        category_name: str | None = item.get("category_name")
        if category_id and category_name:
            categories[category_id] = category_name
    return categories


async def fetch(category_id: str = "1") -> list[HotItem]:
    """获取稀土掘金文章榜"""
    url: str = (
        f"https://api.juejin.cn/content_api/v1/content/article_rank?category_id={category_id}&type=hot"
    )
    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    }
    result: dict[str, Any] = await http_get(url, headers)
    data_list: list[dict[str, Any]] = result.get("data", [])
    items: list[HotItem] = []
    for item in data_list:
        content: dict[str, Any] = item.get("content", {})
        author: dict[str, Any] = item.get("author", {})
        content_counter: dict[str, Any] = item.get("content_counter", {})
        content_id: str | None = content.get("content_id")
        hot_item: HotItem = HotItem(
            id=content_id,
            title=content.get("title"),
            author=author.get("name"),
            hot=content_counter.get("hot_rank"),
            url=f"https://juejin.cn/post/{content_id}",
            mobile_url=f"https://juejin.cn/post/{content_id}",
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], type_name: str, format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, type_name)
    else:
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
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(
    category: str = typer.Option(
        "1", help="分类 ID（默认 1 = 综合），运行 hotboard-juejin --list-categories 查看所有分类"
    ),
    list_categories: bool = typer.Option(False, "--list-categories", help="列出所有可用分类"),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """稀土掘金文章榜"""
    categories: dict[str, str] = asyncio.run(get_categories())

    if list_categories:
        print("可用分类：")
        for cat_id, cat_name in categories.items():
            print(f"  {cat_id} = {cat_name}")
        return

    items: list[HotItem] = asyncio.run(fetch(category))
    category_name = categories.get(category, category)
    print(format_output(items, category_name, format))
    logger.info(f"获取 [{PLATFORM_NAME} - {category_name}] 成功，共 {len(items)} 条")
