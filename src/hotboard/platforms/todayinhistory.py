import asyncio
import json
from datetime import datetime
from typing import Any

import typer
from bs4 import BeautifulSoup

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, http_get_text

PLATFORM_NAME = "历史上的今天"


async def fetch(month: int, day: int) -> list[HotItem]:
    """获取历史上的今天"""
    month_str: str = str(month).zfill(2)
    day_str: str = str(day).zfill(2)
    url: str = f"https://baike.baidu.com/cms/home/eventsOnHistory/{month_str}.json?_={int(datetime.now().timestamp() * 1000)}"
    text: str = await http_get_text(url)
    result: dict[str, Any] = json.loads(text)
    month_data: dict[str, list[dict[str, Any]]] = result.get(month_str, {})
    data_list: list[dict[str, Any]] = month_data.get(month_str + day_str, [])
    items: list[HotItem] = []
    for item in data_list:
        title_html = item.get("title")
        title: str = (
            BeautifulSoup(title_html, "html.parser").get_text().strip() if title_html else ""
        )
        desc_html = item.get("desc")
        desc: str = BeautifulSoup(desc_html, "html.parser").get_text().strip() if desc_html else ""
        hot_item: HotItem = HotItem(
            title=title,
            desc=desc,
            cover=item.get("pic_share") if item.get("cover") else None,
            author=item.get("year"),
            url=item.get("link"),
            mobile_url=item.get("link"),
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], month: int, day: int, format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, f"{month}-{day}")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - {month}-{day}\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.author:
                lines.append(f"- **年份**: {item.author}")
            if item.desc:
                lines.append(f"- **描述**: {item.desc}")
            if item.cover:
                lines.append(f"- **图片**: {item.cover}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(
    month: int = typer.Option(datetime.now().month, help="月份（默认当前月份）"),
    day: int = typer.Option(datetime.now().day, help="日期（默认当前日期）"),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """历史上的今天"""
    items: list[HotItem] = asyncio.run(fetch(month, day))
    print(format_output(items, month, day, format))
    logger.info(f"获取 [{PLATFORM_NAME}] 成功，共 {len(items)} 条")
