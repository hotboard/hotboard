import asyncio
import json
from typing import Any

import typer

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, get_time, http_get_text

PLATFORM_NAME = "网易新闻"


async def fetch() -> list[HotItem]:
    """获取网易新闻热点榜"""
    url: str = "https://m.163.com/fe/api/hot/news/flow"
    text: str = await http_get_text(url)
    data: dict[str, Any] = json.loads(text)
    item_list: list[dict[str, Any]] = data.get("data", {}).get("list", [])
    items: list[HotItem] = []
    for item in item_list:
        doc_id: str = item.get("docid", "")
        hot_item: HotItem = HotItem(
            id=doc_id,
            title=item.get("title"),
            cover=item.get("imgsrc"),
            author=item.get("source"),
            time=get_time(item.get("ptime")),
            url=f"https://www.163.com/dy/article/{doc_id}.html",
            mobile_url=f"https://m.163.com/dy/article/{doc_id}.html",
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "热点榜")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 热点榜\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.author:
                lines.append(f"- **来源**: {item.author}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            if item.cover:
                lines.append(f"- **封面**: {item.cover}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """网易新闻热点榜"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 热点榜] 成功，共 {len(items)} 条")
