import asyncio
import json
import time
from enum import StrEnum
from typing import Any, TypedDict

import typer

from hotboard.core.logger import logger
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import format_items_json, get_time, http_post

PLATFORM_NAME = "36 氪"


class RankType(StrEnum):
    """榜单类型"""

    HOT = "hot"
    VIDEO = "video"
    COMMENT = "comment"
    COLLECT = "collect"


class RankConfig(TypedDict):
    """榜单类型配置"""

    name: str  # 榜单中文名称
    list_key: str  # API 响应中的列表字段名


RANK_CONFIGS: dict[str, RankConfig] = {
    RankType.HOT: {"name": "人气榜", "list_key": "hotRankList"},
    RankType.VIDEO: {"name": "视频榜", "list_key": "videoList"},
    RankType.COMMENT: {"name": "热议榜", "list_key": "remarkList"},
    RankType.COLLECT: {"name": "收藏榜", "list_key": "collectList"},
}


async def fetch(rank_type: str = "hot") -> list[HotItem]:
    """获取 36 氪榜单"""
    url: str = f"https://gateway.36kr.com/api/mis/nav/home/nav/rank/{rank_type}"
    headers: dict[str, str] = {
        "Content-Type": "application/json; charset=utf-8",
        "Referer": "https://m.36kr.com/",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    }
    body: dict[str, Any] = {
        "partner_id": "wap",
        "param": {
            "siteId": 1,
            "platformId": 2,
        },
        "timestamp": int(time.time() * 1000),
    }
    result: dict[str, Any] = await http_post(url, headers, json.dumps(body))
    result_list_key = RANK_CONFIGS[rank_type]["list_key"]
    item_list: list[dict[str, Any]] = result.get("data", {}).get(result_list_key, [])
    items: list[HotItem] = []
    for item in item_list:
        material: dict[str, Any] = item.get("templateMaterial", {})
        item_id: str = item.get("itemId", "")
        hot_item: HotItem = HotItem(
            id=item_id,
            title=material.get("widgetTitle"),
            author=material.get("authorName"),
            cover=material.get("widgetImage"),
            time=get_time(item.get("publishTime")),
            hot=material.get("statRead"),
            url=f"https://www.36kr.com/p/{item_id}",
            mobile_url=f"https://m.36kr.com/p/{item_id}",
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
            if item.hot:
                lines.append(f"- **热度**: {item.hot}")
            if item.author:
                lines.append(f"- **作者**: {item.author}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(
    type: RankType = typer.Option(
        RankType.HOT,
        help="榜单类型：" + ", ".join([f"{k}={v['name']}" for k, v in RANK_CONFIGS.items()]),
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """36 氪榜单"""
    items: list[HotItem] = asyncio.run(fetch(type))
    type_name = RANK_CONFIGS[type]["name"]
    print(format_output(items, type_name, format))
    logger.info(f"获取 [{PLATFORM_NAME} - {type_name}] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
