import asyncio
from enum import StrEnum
from typing import Any

import typer

from hotboard.core.logger import logger
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import format_items_json, get_time, http_get

PLATFORM_NAME = "V2EX"


class TopicType(StrEnum):
    """主题类型"""

    HOT = "hot"
    LATEST = "latest"


TOPIC_NAMES: dict[str, str] = {
    TopicType.HOT: "最热主题",
    TopicType.LATEST: "最新主题",
}


async def fetch(topic_type: str = "hot") -> list[HotItem]:
    """获取 V2EX 主题榜"""
    url: str = f"https://www.v2ex.com/api/topics/{topic_type}.json"
    data: list[dict[str, Any]] = await http_get(url)
    items: list[HotItem] = []
    for item in data:
        hot_item: HotItem = HotItem(
            id=item.get("id"),
            title=item.get("title"),
            desc=item.get("content"),
            author=item.get("member", {}).get("username"),
            time=get_time(item.get("created", "")),
            hot=item.get("replies"),
            url=item.get("url"),
            mobile_url=item.get("url"),
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], topic_name: str, format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, topic_name)
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - {topic_name}\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.desc:
                desc_preview: str = item.desc[:100] + "..." if len(item.desc) > 100 else item.desc
                lines.append(f"- **描述**: {desc_preview}")
            if item.author:
                lines.append(f"- **作者**: {item.author}")
            if item.hot:
                lines.append(f"- **回复数**: {item.hot}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(
    type: TopicType = typer.Option(
        TopicType.HOT, help="主题类型：" + ", ".join([f"{k}={v}" for k, v in TOPIC_NAMES.items()])
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """V2EX 主题榜"""
    items: list[HotItem] = asyncio.run(fetch(type))
    topic_name = TOPIC_NAMES[type]
    print(format_output(items, topic_name, format))
    logger.info(f"获取 [{PLATFORM_NAME} - {topic_name}] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
