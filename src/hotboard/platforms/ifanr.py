import asyncio
from typing import Any

import typer

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, get_time, http_get

PLATFORM_NAME = "爱范儿"


async def fetch() -> list[HotItem]:
    """获取爱范儿快讯"""
    url: str = "https://sso.ifanr.com/api/v5/wp/buzz/?limit=20&offset=0"

    result: dict[str, Any] = await http_get(url)

    items: list[HotItem] = []
    for item in result["objects"]:
        item_id: str = item.get("id")
        post_title: str = item.get("post_title")
        post_content: str = item.get("post_content")
        created_at: str = item.get("created_at")
        like_count: int = item.get("like_count")
        comment_count: int = item.get("comment_count")
        # 原文链接
        buzz_original_url: str = item.get("buzz_original_url")
        post_id: str = item.get("post_id")

        hot: int = like_count or comment_count
        url: str = f"https://www.ifanr.com/digest/{post_id}"
        hot_item: HotItem = HotItem(
            id=item_id,
            title=post_title,
            desc=(
                post_content + "\n" + "原文链接：" + buzz_original_url
                if buzz_original_url
                else post_content
            ),
            time=get_time(created_at),
            hot=hot,
            url=url,
            mobile_url=url,
        )
        items.append(hot_item)

    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "快讯")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 快讯\n",
            f"**总数**: {len(items)} 条\n",
        ]

        for item in items:
            lines.append(f"## {item.title}\n")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            if item.hot:
                lines.append(f"- **热度**: {item.hot}")
            if item.desc:
                lines.append(f"- **描述**: {item.desc}")
            lines.append(f"- **链接**: {item.url}\n")

        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """爱范儿快讯"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 快讯] 成功，共 {len(items)} 条")
