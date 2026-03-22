import asyncio
from typing import Any

import typer

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, get_time, http_get

PLATFORM_NAME = "CSDN"


async def fetch() -> list[HotItem]:
    """获取 CSDN 排行榜"""
    url: str = "https://blog.csdn.net/phoenix/web/blog/hot-rank?page=0&pageSize=30"

    result: dict[str, Any] = await http_get(url)

    items: list[HotItem] = []
    for item in result.get("data", []):
        pic_list: list[str] = item.get("picList", [])
        url = item.get("articleDetailUrl")
        hot_item: HotItem = HotItem(
            id=item.get("productId"),
            title=item.get("articleTitle"),
            cover=pic_list[0] if pic_list else None,
            author=item.get("nickName"),
            time=get_time(item.get("period")),
            hot=item.get("hotRankScore"),
            url=url,
            mobile_url=url,
        )
        items.append(hot_item)

    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "排行榜")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 排行榜\n",
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


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """CSDN 排行榜"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 排行榜] 成功，共 {len(items)} 条")
