import asyncio
from typing import Any

import typer

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, get_time, http_get

PLATFORM_NAME = "百度贴吧"


async def fetch() -> list[HotItem]:
    """获取百度贴吧热议榜"""
    url: str = "https://tieba.baidu.com/hottopic/browse/topicList"
    data: dict[str, Any] = await http_get(url)
    topic_list: list[dict[str, Any]] = (
        data.get("data", {}).get("bang_topic", {}).get("topic_list", [])
    )
    items: list[HotItem] = []
    for item in topic_list:
        hot_item: HotItem = HotItem(
            id=item.get("topic_id"),
            title=item.get("topic_name"),
            desc=item.get("topic_desc"),
            cover=item.get("topic_pic"),
            hot=item.get("discuss_num"),
            time=get_time(item.get("create_time")),
            url=item.get("topic_url"),
            mobile_url=item.get("topic_url"),
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "热议榜")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 热议榜\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.desc:
                lines.append(f"- **描述**: {item.desc}")
            if item.hot:
                lines.append(f"- **讨论数**: {item.hot}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """百度贴吧热议榜"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 热议榜] 成功，共 {len(items)} 条")
