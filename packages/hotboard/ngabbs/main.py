import asyncio
import json
from typing import Any

import typer

from hotboard.core.logger import logger
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import format_items_json, get_time, http_post_text

PLATFORM_NAME = "NGA"


async def fetch() -> list[HotItem]:
    """获取 NGA 论坛热帖"""
    url: str = (
        "https://ngabbs.com/nuke.php?__lib=load_topic&__act=load_topic_reply_ladder2&opt=1&all=1"
    )
    headers: dict[str, str] = {
        "Accept": "*/*",
        "Host": "ngabbs.com",
        "Referer": "https://ngabbs.com/",
        "Connection": "keep-alive",
        "Content-Length": "11",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-Hans-CN;q=1",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "X-User-Agent": "NGA_skull/7.3.1(iPhone13,2;iOS 17.2.1)",
    }
    text: str = await http_post_text(url, headers=headers, body="__output=14")
    data: dict[str, Any] = json.loads(text)
    result_list: list[list[dict[str, Any]]] = data.get("result", [[]])
    item_list: list[dict[str, Any]] = result_list[0] if result_list else []
    items: list[HotItem] = []
    for item in item_list:
        tpcurl: str = item.get("tpcurl", "")
        hot_item: HotItem = HotItem(
            id=item.get("tid"),
            title=item.get("subject"),
            author=item.get("author"),
            hot=item.get("replies"),
            time=get_time(item.get("postdate")),
            url=f"https://bbs.nga.cn{tpcurl}",
            mobile_url=f"https://bbs.nga.cn{tpcurl}",
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "论坛热帖")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 论坛热帖\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.author:
                lines.append(f"- **作者**: {item.author}")
            if item.hot:
                lines.append(f"- **回复**: {item.hot}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """NGA 论坛热帖"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 论坛热帖] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
