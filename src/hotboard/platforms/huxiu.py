import asyncio
import json
import re
from typing import Any

import typer

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, get_time, http_get_text

PLATFORM_NAME = "虎嗅"


async def fetch() -> list[HotItem]:
    """获取虎嗅 24 小时"""
    url: str = "https://moment-api.huxiu.com/web-v3/moment/feed?platform=www"

    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.huxiu.com/moment/",
    }

    text: str = await http_get_text(url, headers)
    result: dict[str, Any] = json.loads(text)

    items: list[HotItem] = []
    for item in result["data"]["moment_list"]["datalist"]:
        content: str = item.get("content", "")
        content = re.sub(r"<br\s*/?>", "\n", content, flags=re.IGNORECASE)

        lines: list[str] = [line.strip() for line in content.split("\n") if line.strip()]

        title: str = ""
        desc: str = ""

        if lines:
            title = lines[0].rstrip("。")
            if len(lines) > 1:
                desc = "\n".join(lines[1:])

        object_id: str | None = item.get("object_id")
        user_info: dict[str, Any] = item.get("user_info")
        username: str | None = user_info.get("username") if user_info else None
        publish_time: str | None = item.get("publish_time")
        count_info: dict[str, Any] = item.get("count_info")
        agree_num: int | None = count_info.get("agree_num") if count_info else None

        hot_item: HotItem = HotItem(
            id=object_id,
            title=title,
            desc=desc,
            author=username,
            time=get_time(publish_time),
            hot=agree_num,
            url=f"https://www.huxiu.com/moment/{object_id}.html",
            mobile_url=f"https://m.huxiu.com/moment/{object_id}.html",
        )
        items.append(hot_item)

    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "24 小时")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 24 小时\n",
            f"**总数**: {len(items)} 条\n",
        ]

        for item in items:
            lines.append(f"## {item.title}\n")
            if item.author:
                lines.append(f"- **作者**: {item.author}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            if item.hot:
                lines.append(f"- **点赞**: {item.hot}")
            if item.desc:
                lines.append(f"- **描述**: {item.desc}")
            lines.append(f"- **链接**: {item.url}\n")

        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """虎嗅 24 小时"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 24 小时] 成功，共 {len(items)} 条")
