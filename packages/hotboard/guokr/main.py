import asyncio
from typing import Any

import typer

from hotboard.core.logger import logger
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import format_items_json, get_time, http_get

PLATFORM_NAME = "果壳"


async def fetch() -> list[HotItem]:
    """获取果壳热门文章"""
    url: str = "https://www.guokr.com/beta/proxy/science_api/articles?limit=30"

    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    }

    result: list[dict[str, Any]] = await http_get(url, headers)

    items: list[HotItem] = []
    for item in result:
        article_id: str | None = item.get("id")
        title: str | None = item.get("title")
        summary: str | None = item.get("summary")
        small_image: str | None = item.get("small_image")
        date_modified: str | None = item.get("date_modified")

        author_data: dict[str, Any] | None = item.get("author")
        author: str | None = None
        if author_data:
            author = author_data.get("nickname")

        hot_item: HotItem = HotItem(
            id=article_id,
            title=title,
            desc=summary,
            time=get_time(date_modified),
            url=f"https://www.guokr.com/article/{article_id}",
            mobile_url=f"https://m.guokr.com/article/{article_id}",
            cover=small_image,
            author=author,
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
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            if item.author:
                lines.append(f"- **作者**: {item.author}")
            if item.desc:
                lines.append(f"- **描述**: {item.desc}")
            lines.append(f"- **链接**: {item.url}\n")

        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """果壳热门文章"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 热门文章] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
