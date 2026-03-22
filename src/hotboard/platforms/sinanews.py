import asyncio
import json
from datetime import datetime
from enum import StrEnum
from typing import Any, TypedDict

import typer

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, get_time, http_get_text

PLATFORM_NAME = "新浪新闻"


class RankType(StrEnum):
    """榜单类型"""

    ALL = "1"
    VIDEO = "2"
    IMAGE = "3"
    CHINA = "4"
    WORLD = "5"
    SOCIETY = "6"
    SPORTS = "7"
    FINANCE = "8"
    ENT = "9"
    TECH = "10"
    MIL = "11"


class RankConfig(TypedDict):
    """榜单配置"""

    name: str
    www: str
    params: str


RANK_CONFIGS: dict[str, RankConfig] = {
    RankType.ALL: {"name": "总排行", "www": "news", "params": "www_www_all_suda_suda"},
    RankType.VIDEO: {"name": "视频排行", "www": "news", "params": "video_news_all_by_vv"},
    RankType.IMAGE: {"name": "图片排行", "www": "news", "params": "total_slide_suda"},
    RankType.CHINA: {"name": "国内新闻", "www": "news", "params": "news_china_suda"},
    RankType.WORLD: {"name": "国际新闻", "www": "news", "params": "news_world_suda"},
    RankType.SOCIETY: {"name": "社会新闻", "www": "news", "params": "news_society_suda"},
    RankType.SPORTS: {"name": "体育新闻", "www": "sports", "params": "sports_suda"},
    RankType.FINANCE: {"name": "财经新闻", "www": "finance", "params": "finance_0_suda"},
    RankType.ENT: {"name": "娱乐新闻", "www": "ent", "params": "ent_suda"},
    RankType.TECH: {"name": "科技新闻", "www": "tech", "params": "tech_news_suda"},
    RankType.MIL: {"name": "军事新闻", "www": "news", "params": "news_mil_suda"},
}


def parse_jsonp(data: str) -> dict[str, Any]:
    """解析 JSONP 数据"""
    prefix: str = "var data = "
    json_str: str = data[len(prefix) :].strip().rstrip(";")
    return json.loads(json_str)


async def fetch(rank_type: str = "1") -> list[HotItem]:
    """获取新浪新闻"""
    config: RankConfig = RANK_CONFIGS[rank_type]
    date_str: str = datetime.now().strftime("%Y%m%d")
    url: str = (
        f"https://top.{config['www']}.sina.com.cn/ws/GetTopDataList.php?top_type=day&top_cat={config['params']}&top_time={date_str}&top_show_num=50"
    )
    text: str = await http_get_text(url)
    data: dict[str, Any] = parse_jsonp(text)
    item_list: list[dict[str, Any]] = data.get("data", [])
    items: list[HotItem] = []
    for item in item_list:
        item_url: str = item.get("url", "")
        hot_item: HotItem = HotItem(
            id=item.get("id"),
            title=item.get("title"),
            author=item.get("media"),
            hot=item.get("top_num"),
            time=get_time(item.get("time")),
            url=item_url,
            mobile_url=item_url,
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], rank_name: str, format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, rank_name)
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - {rank_name}\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.author:
                lines.append(f"- **来源**: {item.author}")
            if item.hot:
                lines.append(f"- **热度**: {item.hot}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(
    type: RankType = typer.Option(
        RankType.ALL,
        help="榜单类型：" + ", ".join([f"{k}={v['name']}" for k, v in RANK_CONFIGS.items()]),
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """新浪新闻"""
    items: list[HotItem] = asyncio.run(fetch(type))
    rank_name = RANK_CONFIGS[type]["name"]
    print(format_output(items, rank_name, format))
    logger.info(f"获取 {PLATFORM_NAME} {rank_name}成功，共 {len(items)} 条")
