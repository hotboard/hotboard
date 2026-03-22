import asyncio
import re

import typer
from bs4 import BeautifulSoup

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, http_get_text

PLATFORM_NAME = "简书"


def get_id(url: str) -> str:
    """从 URL 中提取 ID"""
    if not url:
        return "undefined"
    match = re.search(r"([^/]+)$", url)
    return match.group(1) if match else "undefined"


async def fetch() -> list[HotItem]:
    """获取简书热门推荐"""
    url: str = "https://www.jianshu.com/"
    headers: dict[str, str] = {"Referer": "https://www.jianshu.com"}
    html: str = await http_get_text(url, headers)
    soup = BeautifulSoup(html, "lxml")
    list_dom = soup.select("ul.note-list li")

    items: list[HotItem] = []
    for item in list_dom:
        a_tag = item.select_one("a")
        href_attr = a_tag.get("href") if a_tag else None
        href: str = str(href_attr) if href_attr and isinstance(href_attr, str) else ""

        a_title = item.select_one("a.title")
        title: str | None = a_title.get_text(strip=True) if a_title else None

        cover_tag = item.select_one("img")
        cover_attr = cover_tag.get("src") if cover_tag else None
        cover: str | None = str(cover_attr) if cover_attr and isinstance(cover_attr, str) else None

        desc_tag = item.select_one("p.abstract")
        desc: str | None = desc_tag.get_text(strip=True) if desc_tag else None

        author_tag = item.select_one("a.nickname")
        author: str | None = author_tag.get_text(strip=True) if author_tag else None

        article_id: str = get_id(href)

        hot_item: HotItem = HotItem(
            id=article_id,
            title=title,
            desc=desc,
            cover=cover,
            author=author,
            url=f"https://www.jianshu.com{href}",
            mobile_url=f"https://www.jianshu.com{href}",
        )
        items.append(hot_item)

    return items


def format_output(items: list[HotItem], type_name: str, format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "热门推荐")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 热门推荐\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.author:
                lines.append(f"- **作者**: {item.author}")
            if item.desc:
                lines.append(f"- **描述**: {item.desc}")
            if item.cover:
                lines.append(f"- **封面**: {item.cover}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """简书热门推荐"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, "热门推荐", format))
    logger.info(f"获取 [{PLATFORM_NAME} - 热门推荐] 成功，共 {len(items)} 条")
