import asyncio
from typing import Any

import typer

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, get_time, http_get

PLATFORM_NAME = "今日头条"


async def fetch() -> list[HotItem]:
    """获取今日头条热榜"""
    url: str = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
    result: dict[str, Any] = await http_get(url)
    data: list[dict[str, Any]] = result.get("data", [])
    return [
        HotItem(
            id=item["ClusterIdStr"],
            title=item["Title"],
            cover=item["Image"]["url"],
            hot=int(item["HotValue"]),
            url=f"https://www.toutiao.com/trending/{item['ClusterIdStr']}/",
            mobile_url=f"https://api.toutiaoapi.com/feoffline/amos_land/new/html/main/index.html?topic_id={item['ClusterIdStr']}",
        )
        for item in data
    ]


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items)
    lines: list[str] = [
        f"# {PLATFORM_NAME}\n",
        f"**总数**: {len(items)} 条\n",
    ]
    for item in items:
        lines.append(f"## {item.title}\n")
        if item.hot:
            lines.append(f"- **热度**: {item.hot}")
        lines.append(f"- **链接**: {item.url}\n")
    return "\n".join(lines)


def main(
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """今日头条热榜"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME}] 成功,共 {len(items)} 条")
