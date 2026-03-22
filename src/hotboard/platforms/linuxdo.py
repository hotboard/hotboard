import asyncio

import feedparser
import typer
from bs4 import BeautifulSoup

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, get_time, http_get_text

PLATFORM_NAME = "Linux.do"


async def fetch() -> list[HotItem]:
    """获取 Linux.do 热门文章"""
    url: str = "https://linux.do/top.rss?period=weekly"
    headers: dict[str, str] = {
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    }
    content: str = await http_get_text(url, headers)
    feed = feedparser.parse(content)
    items: list[HotItem] = []
    for entry in feed.entries:
        link = entry.get("link")
        link_str: str = str(link) if link else ""

        summary_detail = entry.get("summary_detail")
        desc_value = (
            summary_detail.get("value")
            if summary_detail and isinstance(summary_detail, dict)
            else None
        )
        summary = entry.get("summary")
        desc: str | None = str(desc_value) if desc_value else (str(summary) if summary else None)

        if desc:
            soup = BeautifulSoup(desc, "html.parser")
            desc = soup.get_text(separator=" ", strip=True)

        hot_item: HotItem = HotItem(
            id=str(entry.get("id", link_str)),
            title=str(entry.get("title")),
            desc=desc,
            author=str(entry.get("author")),
            time=get_time(str(entry.get("published"))),
            url=link_str,
            mobile_url=link_str,
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
            if item.desc:
                lines.append(f"- **简介**: {item.desc}")
            if item.author:
                lines.append(f"- **作者**: {item.author}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """Linux.do 热门文章"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 热门文章] 成功，共 {len(items)} 条")
