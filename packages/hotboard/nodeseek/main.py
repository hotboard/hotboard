import asyncio

import feedparser
import typer

from hotboard.core.logger import logger
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import format_items_json, get_time, http_get_text

PLATFORM_NAME = "NodeSeek"


async def fetch() -> list[HotItem]:
    """获取 NodeSeek 最新"""
    url: str = "https://rss.nodeseek.com/"
    text: str = await http_get_text(url)
    feed: feedparser.util.FeedParserDict = feedparser.parse(text)
    items: list[HotItem] = []
    for entry in feed.get("entries") or []:
        link: str = str(entry.get("link"))
        hot_item: HotItem = HotItem(
            id=str(entry.get("id")),
            title=str(entry.get("title")),
            desc=str(entry.get("summary")),
            author=str(entry.get("author")),
            time=get_time(str(entry.get("published"))),
            url=link,
            mobile_url=link,
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "最新")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 最新\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.desc:
                lines.append(f"- **描述**: {item.desc[:100]}...")
            if item.author:
                lines.append(f"- **作者**: {item.author}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """NodeSeek 最新"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 最新] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
