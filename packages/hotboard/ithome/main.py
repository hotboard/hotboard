import asyncio
import re
import typer
from enum import StrEnum

from bs4 import BeautifulSoup

from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import http_get_text, format_items_json
from hotboard.core.logger import logger

PLATFORM_NAME = "IT 之家"


class RankType(StrEnum):
    """榜单类型"""

    HOT = "hot"
    XIJIAYI = "xijiayi"


RANK_CONFIGS: dict[str, str] = {
    RankType.HOT: "热榜",
    RankType.XIJIAYI: "喜加一",
}


def replace_link_hot(url: str, get_id: bool = False) -> str:
    """处理热榜链接"""
    match = re.search(r"[html|live]/(\d+)\.htm", url)
    if match:
        article_id: str = match.group(1)
        if get_id:
            return article_id
        return f"https://www.ithome.com/0/{article_id[:3]}/{article_id[3:]}.htm"
    return url


def replace_link_xijiayi(url: str, get_id: bool = False) -> str:
    """处理喜加一链接"""
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
        href: str | None = item.select_one("a")["href"] if item.select_one("a") else None
        title: str = (
            item.select_one(".plc-title").get_text(strip=True)
            if item.select_one(".plc-title")
            else ""
        )
        cover_tag = item.select_one("img")
        cover: str | None = cover_tag.get("data-original") if cover_tag else None
        time_tag = item.select_one("span.post-time")
        time_text: str = time_tag.get_text(strip=True) if time_tag else ""
        review_tag = item.select_one(".review-num")
        review_text: str = review_tag.get_text(strip=True) if review_tag else None

        article_id: str = replace_link_hot(href, True) if href else None
        url_pc: str = replace_link_hot(href) if href else None

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
        href: str | None = item.select_one("a")["href"] if item.select_one("a") else None
        title: str = (
            item.select_one(".newsbody h2").get_text(strip=True)
            if item.select_one(".newsbody h2")
            else ""
        )
        desc: str | None = (
            item.select_one(".newsbody p").get_text(strip=True)
            if item.select_one(".newsbody p")
            else None
        )
        cover_tag = item.select_one("img")
        cover: str | None = cover_tag.get("data-original") if cover_tag else None
        time_tag = item.select_one("span.time")
        if time_tag:
            script_content = str(time_tag)  # 转成字符串
            match = re.search(r"'([^']+)'", script_content)
            time_str = match.group(1) if match else ""

        comment_tag = item.select_one(".comment")
        comment_text: str = comment_tag.get_text(strip=True) if comment_tag else ""

        article_id: str = replace_link_xijiayi(href, True) if href else None
        url_mobile: str = replace_link_xijiayi(href) if href else None

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
    """IT 之家榜单"""
    if type == RankType.XIJIAYI:
        items: list[HotItem] = asyncio.run(fetch_xijiayi())
    else:
        items: list[HotItem] = asyncio.run(fetch_hot())
    type_name = RANK_CONFIGS[type]
    print(format_output(items, type_name, format))
    logger.info(f"获取 [{PLATFORM_NAME} - {type_name}] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
