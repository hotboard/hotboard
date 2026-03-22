import asyncio
import re
from enum import StrEnum

import typer
from bs4 import BeautifulSoup

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, http_get_text

PLATFORM_NAME = "IT 之家"


class RankType(StrEnum):
    """榜单类型"""

    HOT = "hot"
    XIJIAYI = "xijiayi"


RANK_CONFIGS: dict[str, str] = {
    RankType.HOT: "热榜",
    RankType.XIJIAYI: "喜加一",
}


def replace_link_hot(url: str | None, get_id: bool = False) -> str | None:
    """处理热榜链接"""
    if not url:
        return None
    match = re.search(r"[html|live]/(\d+)\.htm", url)
    if match:
        article_id: str = match.group(1)
        if get_id:
            return article_id
        return f"https://www.ithome.com/0/{article_id[:3]}/{article_id[3:]}.htm"
    return url


def replace_link_xijiayi(url: str | None, get_id: bool = False) -> str | None:
    """处理喜加一链接"""
    if not url:
        return None
    match = re.search(r"https://www\.ithome\.com/0/(\d+)/(\d+)\.htm", url)
    if match:
        part1: str = match.group(1)
        part2: str = match.group(2)
        if get_id:
            return part1 + part2
        return f"https://m.ithome.com/html/{part1}{part2}.htm"
    return url


async def fetch_hot() -> list[HotItem]:
    """获取 IT 之家热榜"""
    url: str = "https://m.ithome.com/rankm/"
    html: str = await http_get_text(url)
    soup = BeautifulSoup(html, "lxml")
    list_dom = soup.select(".rank-box .placeholder")

    items: list[HotItem] = []
    for item in list_dom:
        a_tag = item.select_one("a")
        href_attr = a_tag.get("href") if a_tag else None
        href: str | None = str(href_attr) if href_attr and isinstance(href_attr, str) else None

        title_tag = item.select_one(".plc-title")
        title: str | None = title_tag.get_text(strip=True) if title_tag else None

        cover_tag = item.select_one("img")
        cover_attr = cover_tag.get("data-original") if cover_tag else None
        cover: str | None = str(cover_attr) if cover_attr and isinstance(cover_attr, str) else None

        time_tag = item.select_one("span.post-time")
        time_text: str | None = time_tag.get_text(strip=True) if time_tag else None

        review_tag = item.select_one(".review-num")
        review_text: str | None = review_tag.get_text(strip=True) if review_tag else None

        article_id: str | None = replace_link_hot(href, True)
        url_pc: str | None = replace_link_hot(href)

        hot_item: HotItem = HotItem(
            id=article_id,
            title=title,
            cover=cover,
            time=time_text,
            hot=review_text,
            url=url_pc,
            mobile_url=url_pc,
        )
        items.append(hot_item)

    return items


async def fetch_xijiayi() -> list[HotItem]:
    """获取 IT 之家喜加一"""
    url: str = "https://www.ithome.com/zt/xijiayi"
    html: str = await http_get_text(url)
    soup = BeautifulSoup(html, "lxml")
    list_dom = soup.select(".newslist li")

    items: list[HotItem] = []
    for item in list_dom:
        a_tag = item.select_one("a")
        href_attr = a_tag.get("href") if a_tag else None
        href: str | None = str(href_attr) if href_attr and isinstance(href_attr, str) else None

        title_tag = item.select_one(".newsbody h2")
        title: str | None = title_tag.get_text(strip=True) if title_tag else None

        desc_tag = item.select_one(".newsbody p")
        desc: str | None = desc_tag.get_text(strip=True) if desc_tag else None

        cover_tag = item.select_one("img")
        cover_attr = cover_tag.get("data-original") if cover_tag else None
        cover: str | None = str(cover_attr) if cover_attr and isinstance(cover_attr, str) else None

        time_str: str | None = None
        time_tag = item.select_one("span.time")
        if time_tag:
            script_content = str(time_tag)
            match = re.search(r"'([^']+)'", script_content)
            time_str = match.group(1) if match else None

        comment_tag = item.select_one(".comment")
        comment_text: str | None = comment_tag.get_text(strip=True) if comment_tag else None

        article_id: str | None = replace_link_xijiayi(href, True)
        url_mobile: str | None = replace_link_xijiayi(href)

        hot_item: HotItem = HotItem(
            id=article_id,
            title=title,
            desc=desc,
            cover=cover,
            time=time_str,
            hot=comment_text,
            url=href,
            mobile_url=url_mobile,
        )
        items.append(hot_item)

    return items


def format_output(items: list[HotItem], type_name: str, format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, type_name)
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - {type_name}\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            if item.hot:
                lines.append(f"- **评论**: {item.hot}")
            if item.desc:
                lines.append(f"- **描述**: {item.desc}")
            if item.cover:
                lines.append(f"- **封面**: {item.cover}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(
    type: RankType = typer.Option(
        RankType.HOT, help="榜单类型：" + ", ".join([f"{k}={v}" for k, v in RANK_CONFIGS.items()])
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """IT 之家榜单和喜加一最新动态"""
    if type == RankType.XIJIAYI:
        items: list[HotItem] = asyncio.run(fetch_xijiayi())
    else:
        items: list[HotItem] = asyncio.run(fetch_hot())
    type_name = RANK_CONFIGS[type]
    print(format_output(items, type_name, format))
    logger.info(f"获取 [{PLATFORM_NAME} - {type_name}] 成功，共 {len(items)} 条")
