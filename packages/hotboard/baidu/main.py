import asyncio
import re
import json

import typer
from enum import StrEnum

from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import http_get_text, format_items_json
from hotboard.core.logger import logger

PLATFORM_NAME = "百度"


class SearchType(StrEnum):
    """热搜类别"""

    REALTIME = "realtime"
    NOVEL = "novel"
    MOVIE = "movie"
    TELEPLAY = "teleplay"
    CAR = "car"
    GAME = "game"


SEARCH_CONFIGS: dict[str, str] = {
    SearchType.REALTIME: "热搜",
    SearchType.NOVEL: "小说",
    SearchType.MOVIE: "电影",
    SearchType.TELEPLAY: "电视剧",
    SearchType.CAR: "汽车",
    SearchType.GAME: "游戏",
}


async def fetch(search_type: str = "realtime") -> list[HotItem]:
    """获取百度热搜"""
    url: str = f"https://top.baidu.com/board?tab={search_type}"

    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    }

    html_content: str = await http_get_text(url, headers)

    # 正则提取 s-data
    pattern: re.Pattern = re.compile(r"<!--s-data:(.*?)-->", re.DOTALL)
    match: re.Match | None = pattern.search(html_content)

    if not match:
        logger.warning("未找到热搜数据")
        return []

    s_data: dict[str, any] = json.loads(match.group(1))
    logger.debug(f"hotboard-baidu s_data: {json.dumps(s_data, ensure_ascii=False)}")
    # 提取 cards 内容
    cards: list[dict[str, any]] = s_data.get("data", {}).get("cards", [])
    if not cards:
        return []

    card_content: list[any] = cards[0].get("content", [])

    items: list[HotItem] = []
    for item in card_content:
        title: str = item.get("word")
        hot_score: str = item.get("hotScore")

        hot_item: HotItem = HotItem(
            title=title,
            desc=item.get("desc"),
            cover=item.get("img"),
            hot=hot_score,
            url=item.get("url"),  # f"https://www.baidu.com/s?wd={quote(item.get("query"))}"
            mobile_url=item.get("appUrl"),
        )
        items.append(hot_item)

    return items


def format_output(items: list[HotItem], search_type: str, format: OutputFormat) -> str:
    """格式化输出"""
    type_name: str = SEARCH_CONFIGS[search_type]
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, type_name)
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - {type_name}\n",
            f"**总数**: {len(items)} 条\n",
        ]

        for item in items:
            lines.append(f"## {item.title}\n")
            if item.hot:
                lines.append(f"- **热度**: {item.hot}")
            if item.author:
                lines.append(f"- **来源**: {item.author}")
            if item.desc:
                desc_preview: str = item.desc[:100] + "..." if len(item.desc) > 100 else item.desc
                lines.append(f"- **简介**: {desc_preview}")
            lines.append(f"- **链接**: {item.url}\n")

        return "\n".join(lines)


def main(
    type: SearchType = typer.Option(
        SearchType.REALTIME,
        help="热搜类别：" + ", ".join([f"{k}={v}" for k, v in SEARCH_CONFIGS.items()]),
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """百度热搜"""
    items: list[HotItem] = asyncio.run(fetch(type))
    type_name = SEARCH_CONFIGS[type]
    print(format_output(items, type, format))
    logger.info(f"获取 [{PLATFORM_NAME} - {type_name}] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
