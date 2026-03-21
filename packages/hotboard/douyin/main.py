import asyncio
import json
from typing import Any

import typer

from hotboard.core.logger import logger
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import format_items_json, get_time, http_get_text

PLATFORM_NAME = "抖音"


async def fetch() -> list[HotItem]:
    """获取抖音热榜"""
    url: str = (
        "https://www.douyin.com/aweme/v1/web/hot/search/list/?device_platform=webapp&aid=6383&channel=channel_pc_web&detail_list=1"
    )

    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    text: str = await http_get_text(url, headers)

    result: dict[str, Any] = json.loads(text)
    items: list[HotItem] = []
    for item in result.get("data", {}).get("word_list", []):
        sentence_id: str = item.get("sentence_id")
        hot_item: HotItem = HotItem(
            id=sentence_id,
            title=item.get("word"),
            time=get_time(item.get("event_time")),
            hot=item.get("hot_value"),
            url=f"https://www.douyin.com/hot/{sentence_id}",
            mobile_url=f"https://www.douyin.com/hot/{sentence_id}",
        )
        items.append(hot_item)

    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "热榜")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 热榜\n",
            f"**总数**: {len(items)} 条\n",
        ]

        for idx, item in enumerate(items, 1):
            lines.append(f"## {idx}. {item.title}\n")
            if item.hot:
                lines.append(f"- **热度**: {item.hot}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")

        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """抖音热榜"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 热榜] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
