import asyncio

import typer

from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import http_get, get_time, format_items_json
from hotboard.core.logger import logger

PLATFORM_NAME = "极客公园"


async def fetch() -> list[HotItem]:
    """获取极客公园热门文章"""
    url: str = "https://mainssl.geekpark.net/api/v2"

    result: dict[str, any] = await http_get(url)

    items: list[HotItem] = []
    for item in result["homepage_posts"]:
        post: dict[str, any] = item.get("post", {})

        post_id: str = post.get("id")
        title: str = post.get("title")
        abstract: str = post.get("abstract")
        cover_url: str = post.get("cover_url")
        views: int = post.get("views")
        published_timestamp: int = post.get("published_timestamp")

        authors: list[dict[str, any]] | None = post.get("authors")
        author: str | None = None
        if authors and len(authors) > 0:
            author = authors[0].get("nickname")

        hot_item: HotItem = HotItem(
            id=post_id,
            title=title,
            desc=abstract,
            time=get_time(published_timestamp),
            hot=views,
            url=f"https://www.geekpark.net/news/{post_id}",
            mobile_url=f"https://www.geekpark.net/news/{post_id}",
            cover=cover_url,
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
            if item.hot:
                lines.append(f"- **浏览**: {item.hot}")
            if item.desc:
                lines.append(f"- **描述**: {item.desc}")
            lines.append(f"- **链接**: {item.url}\n")

        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """极客公园热门文章"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 热门文章] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
