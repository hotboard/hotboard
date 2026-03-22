import asyncio
from typing import Any

import typer

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, get_time, http_get

PLATFORM_NAME = "数字尾巴"


async def fetch() -> list[HotItem]:
    """获取数字尾巴热门文章"""
    url: str = "https://opser.api.dgtle.com/v2/news/index"

    result: dict[str, Any] = await http_get(url)

    items: list[HotItem] = []
    for item in result.get("items", []):
        hot_item: HotItem = HotItem(
            id=item.get("id"),
            title=item.get("title"),
            desc=item.get("content"),
            cover=item.get("cover"),
            author=item.get("from"),
            time=get_time(item.get("created_at")),
            hot=item.get("membernum"),
            url=f"https://www.dgtle.com/news-{item.get('id')}-{item.get('type')}.html",
            mobile_url=f"https://m.dgtle.com/news-details/{item.get('id')}",
        )
        items.append(hot_item)

    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "热门文章")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 热门文章\n",
            f"**总数**: {len(items)} 条\n",
        ]

        for item in items:
            lines.append(f"## {item.title}\n")
            if item.hot:
                lines.append(f"- **热度**: {item.hot}")
            if item.author:
                lines.append(f"- **来源**: {item.author}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            if item.desc:
                desc_preview: str = item.desc[:100] + "..." if len(item.desc) > 100 else item.desc
                lines.append(f"- **简介**: {desc_preview}")
            lines.append(f"- **链接**: {item.url}\n")

        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """数字尾巴热门文章"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 热门文章] 成功，共 {len(items)} 条")
