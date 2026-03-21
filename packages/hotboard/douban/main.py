import asyncio
import re
from enum import StrEnum

import typer
from bs4 import BeautifulSoup

from hotboard.core.logger import logger
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import format_items_json, get_time, http_get_text

PLATFORM_NAME = "豆瓣"


class ListType(StrEnum):
    """榜单类型"""

    GROUP = "group"
    MOVIE = "movie"


LIST_CONFIGS: dict[str, str] = {
    ListType.GROUP: "豆瓣讨论 - 讨论精选",
    ListType.MOVIE: "豆瓣电影 - 新片榜",
}


def get_numbers(text: str | None) -> int:
    """从文本中提取数字"""
    if not text:
        return 0
    match = re.search(r"\d+", text)
    return int(match.group()) if match else 0


async def fetch_group() -> list[HotItem]:
    """获取豆瓣讨论精选"""
    url: str = "https://www.douban.com/group/explore"

    html: str = await http_get_text(url)
    soup = BeautifulSoup(html, "lxml")

    items: list[HotItem] = []
    for item in soup.select(".article .channel-item"):
        link_elem = item.select_one("h3 a")
        url_href: str | None = link_elem.get_text("href") if link_elem else None

        title: str | None = link_elem.get_text(strip=True) if link_elem else None

        desc_elem = item.select_one(".block p")
        desc: str | None = desc_elem.get_text(strip=True) if desc_elem else None

        time_elem = item.select_one("span.pubtime")
        time_text: str | None = time_elem.get_text(strip=True) if time_elem else None

        hot_elem = item.select_one(".likes")
        hot_text: str | None = hot_elem.get_text(strip=True) if hot_elem else None

        cover_elem = item.select_one(".pic-wrap img")
        cover: str | None = cover_elem.get_text("src") if cover_elem else None

        topic_id: int = get_numbers(url_href)
        hot_item: HotItem = HotItem(
            id=topic_id,
            title=title,
            desc=desc,
            time=get_time(time_text),
            hot=get_numbers(hot_text),
            cover=cover,
            url=url_href,  # f"https://www.douban.com/group/topic/{topic_id}"
            mobile_url=f"https://m.douban.com/group/topic/{topic_id}",
        )
        items.append(hot_item)

    return items


async def fetch_movie() -> list[HotItem]:
    """获取豆瓣电影新片榜"""
    url: str = "https://movie.douban.com/chart/"

    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    }

    html: str = await http_get_text(url, headers)
    soup = BeautifulSoup(html, "lxml")

    items: list[HotItem] = []
    for item in soup.select(".article tr.item"):
        link_elem = item.select_one("a")
        url_href: str | None = link_elem.get_text("href") if link_elem else None
        movie_title: str | None = link_elem.get_text("title") if link_elem else None

        score_elem = item.select_one(".rating_nums")
        score_text: str | None = score_elem.get_text(strip=True) if score_elem else None

        score = f"[豆瓣评分 {score_text}]" if score_text else "[暂无评分]"

        title: str = f"{movie_title} {score}" if movie_title else ""

        cover_elem = item.select_one("img")
        cover: str | None = cover_elem.get_text("src") if cover_elem else None

        desc_elem = item.select_one("p.pl")
        desc: str | None = desc_elem.get_text(strip=True) if desc_elem else None

        hot_elem = item.select_one("span.pl")
        hot_text: str | None = hot_elem.get_text(strip=True) if hot_elem else None
        hot: int = get_numbers(hot_text)

        movie_id: int = get_numbers(url_href)

        hot_item: HotItem = HotItem(
            id=movie_id,
            title=title,
            desc=desc,
            cover=cover,
            hot=hot,
            url=url_href,  # f"https://movie.douban.com/subject/{movie_id}/"
            mobile_url=f"https://m.douban.com/movie/subject/{movie_id}/",
        )
        items.append(hot_item)

    return items


def format_output(items: list[HotItem], list_type: str, format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, list_type)
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - {list_type}\n",
            f"**总数**: {len(items)} 条\n",
        ]

        for item in items:
            lines.append(f"## {item.title}\n")
            if item.hot:
                lines.append(f"- **热度**: {item.hot}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            if item.desc:
                desc_preview: str = item.desc[:100] + "..." if len(item.desc) > 100 else item.desc
                lines.append(f"- **简介**: {desc_preview}")
            lines.append(f"- **链接**: {item.url}\n")

        return "\n".join(lines)


def main(
    type: ListType = typer.Option(
        ListType.GROUP, help="榜单类型：" + ", ".join([f"{k}={v}" for k, v in LIST_CONFIGS.items()])
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """豆瓣热榜"""
    if type == ListType.MOVIE:
        items: list[HotItem] = asyncio.run(fetch_movie())
    else:
        items: list[HotItem] = asyncio.run(fetch_group())
    list_type: str = LIST_CONFIGS[type]
    print(format_output(items, list_type, format))
    logger.info(f"获取 [{PLATFORM_NAME} - {list_type}] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
