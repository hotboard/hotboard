import asyncio

import typer
from bs4 import BeautifulSoup

from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import http_get_text, get_time, format_items_json
from hotboard.core.logger import logger

PLATFORM_NAME = "GameRes 游资网"


async def fetch() -> list[HotItem]:
    """获取 GameRes 游资网最新资讯"""
    url: str = "https://www.gameres.com"

    html: str = await http_get_text(url)

    soup = BeautifulSoup(html, "lxml")

    container = soup.find("div", {"data-news-pane-id": "100000"})

    items: list[HotItem] = []
    for article in container.find_all("article", class_="feed-item"):
        title_el = article.find("a", class_="feed-item-title-a")

        title: str = title_el.get_text(strip=True)
        href: str = title_el.get("href")
        item_url: str = href if href.startswith("http") else f"https://www.gameres.com{href}"

        cover_el = article.find("div", class_="thumb")
        cover: str | None = cover_el.get("data-original") if cover_el else None

        desc_el = article.select_one(".feed-item-right > p")
        desc: str | None = desc_el.get_text(strip=True) if desc_el else None

        mark_info = article.find("div", class_="mark-info")
        date_time: str | None = None
        if mark_info:
            text_node = next(mark_info.stripped_strings, None)
            if text_node:
                date_time = text_node

        hot_item: HotItem = HotItem(
            id=item_url,
            title=title,
            desc=desc,
            time=get_time(date_time),
            url=item_url,
            mobile_url=item_url,
            cover=cover,
        )
        items.append(hot_item)

    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "最新资讯")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 最新资讯\n",
            f"**总数**: {len(items)} 条\n",
        ]

        for item in items:
            lines.append(f"## {item.title}\n")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            if item.desc:
                lines.append(f"- **描述**: {item.desc}")
            lines.append(f"- **链接**: {item.url}\n")

        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """GameRes 游资网最新资讯"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 最新资讯] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
