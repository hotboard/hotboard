import asyncio
import re

import typer
from bs4 import BeautifulSoup

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, http_get_text

PLATFORM_NAME = "Hacker News"


async def fetch() -> list[HotItem]:
    """获取 Hacker News Popular"""
    base_url: str = "https://news.ycombinator.com"

    headers: dict[str, str] = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    }

    html: str = await http_get_text(base_url, headers)

    soup = BeautifulSoup(html, "lxml")

    items: list[HotItem] = []
    for story in soup.find_all("tr", class_="athing"):
        story_id_attr = story.get("id")
        if not story_id_attr or not isinstance(story_id_attr, str):
            continue
        story_id: str = story_id_attr

        title_el = story.select_one(".titleline a")
        if not title_el:
            continue

        title: str = title_el.get_text(strip=True)
        href = title_el.get("href")
        if not href or not isinstance(href, str):
            continue
        story_url: str = href if href.startswith("http") else f"{base_url}/item?id={story_id}"

        score_el = soup.find("span", id=f"score_{story_id}")
        hot: str | None = None
        if score_el:
            score_text = score_el.get_text(strip=True)
            match = re.search(r"\d+", score_text)
            if match:
                hot = match.group()

        hot_item: HotItem = HotItem(
            id=story_id,
            title=title,
            hot=hot,
            url=story_url,
            mobile_url=story_url,
        )
        items.append(hot_item)

    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "Popular")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - Popular\n",
            f"**总数**: {len(items)} 条\n",
        ]

        for item in items:
            lines.append(f"## {item.title}\n")
            if item.hot:
                lines.append(f"- **分数**: {item.hot}")
            lines.append(f"- **链接**: {item.url}\n")

        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """Hacker News Popular"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - Popular] 成功，共 {len(items)} 条")
