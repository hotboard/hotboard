import asyncio
from typing import Any
from urllib.parse import quote

import typer

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, get_time, http_get

PLATFORM_NAME = "英雄联盟"


async def fetch() -> list[HotItem]:
    """获取英雄联盟更新公告"""
    url: str = "https://apps.game.qq.com/cmc/zmMcnTargetContentList?r0=json&page=1&num=30&target=24&source=web_pc"
    data: dict[str, Any] = await http_get(url)
    result_list: list[dict[str, Any]] = data.get("data", {}).get("result", [])
    items: list[HotItem] = []
    for item in result_list:
        doc_id: str = item.get("iDocID", "")
        img: str = item.get("sIMG", "")
        url: str = f"https://lol.qq.com/news/detail.shtml?docid={quote(doc_id)}"
        hot_item: HotItem = HotItem(
            id=doc_id,
            title=item.get("sTitle"),
            cover=f"https:{img}" if img else None,
            author=item.get("sAuthor"),
            hot=item.get("iTotalPlay"),
            time=get_time(item.get("sCreated")),
            url=url,
            mobile_url=url,
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "更新公告")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 更新公告\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.author:
                lines.append(f"- **作者**: {item.author}")
            if item.hot:
                lines.append(f"- **热度**: {item.hot}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            if item.cover:
                lines.append(f"- **封面**: {item.cover}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """英雄联盟更新公告"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 更新公告] 成功，共 {len(items)} 条")
