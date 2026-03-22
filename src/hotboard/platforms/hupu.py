import asyncio
from enum import StrEnum
from typing import Any

import typer

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, http_get

PLATFORM_NAME = "虎扑"


class TopicType(StrEnum):
    """话题类型"""

    MAIN = "1"
    LOVE = "6"
    CAMPUS = "11"
    HISTORY = "12"
    PHOTO = "612"


TOPIC_CONFIGS: dict[str, str] = {
    TopicType.MAIN: "主干道",
    TopicType.LOVE: "恋爱区",
    TopicType.CAMPUS: "校园区",
    TopicType.HISTORY: "历史区",
    TopicType.PHOTO: "摄影区",
}


async def fetch(type: str = "1") -> list[HotItem]:
    """获取虎扑步行街热帖"""
    url: str = f"https://m.hupu.com/api/v2/bbs/topicThreads?topicId={type}&page=1"

    result: dict[str, Any] = await http_get(url)

    items: list[HotItem] = []
    for item in result["data"]["topicThreads"]:
        tid: str = item.get("tid")
        title: str = item.get("title")
        username: str = item.get("username")
        replies: int = item.get("replies")

        hot_item: HotItem = HotItem(
            id=tid,
            title=title,
            author=username,
            hot=replies,
            url=f"https://bbs.hupu.com/{tid}.html",
            mobile_url=item.get("url"),
        )
        items.append(hot_item)

    return items


def format_output(items: list[HotItem], type: str, format: OutputFormat) -> str:
    """格式化输出"""
    type_name = TOPIC_CONFIGS[type]

    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, type_name)
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - {type_name}\n",
            f"**总数**: {len(items)} 条\n",
        ]

        for item in items:
            lines.append(f"## {item.title}\n")
            if item.author:
                lines.append(f"- **作者**: {item.author}")
            if item.hot:
                lines.append(f"- **回复**: {item.hot}")
            lines.append(f"- **链接**: {item.url}\n")

        return "\n".join(lines)


def main(
    type: TopicType = typer.Option(
        TopicType.MAIN,
        help="话题类型：" + ", ".join([f"{k}={v}" for k, v in TOPIC_CONFIGS.items()]),
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """虎扑步行街热帖"""
    items: list[HotItem] = asyncio.run(fetch(type))
    print(format_output(items, type, format))
    logger.info(f"获取 [{PLATFORM_NAME} - {type}] 步行街热帖成功，共 {len(items)} 条")
