import asyncio
import feedparser
import typer
from bs4 import BeautifulSoup
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import http_get_text, format_items_json, get_time
from hotboard.core.logger import logger

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
        link: str = entry.get("link", "")
        desc: str = (
            entry.get("summary_detail", {}).get("value", "")
            if hasattr(entry, "summary_detail")
            else entry.get("summary", "")
        )
        if desc:
            soup = BeautifulSoup(desc, "html.parser")
            desc = soup.get_text(separator=" ", strip=True)
        pub_date: str = entry.get("published", "")
        hot_item: HotItem = HotItem(
            id=entry.get("id", link),
            title=entry.get("title"),
            desc=desc,
            author=entry.get("author"),
            time=get_time(pub_date) if pub_date else None,
            url=link,
            mobile_url=link,
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


def run():
    """CLI 入口点"""
    typer.run(main)
