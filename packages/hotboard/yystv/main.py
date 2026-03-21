import asyncio
import json
from typing import Any

import typer

from hotboard.core.logger import logger
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import format_items_json, get_time, http_get_text

PLATFORM_NAME = "游研社"


async def fetch() -> list[HotItem]:
    """获取游研社全部文章"""
    url: str = "https://www.yystv.cn/home/get_home_docs_by_page"
    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
    }
    text: str = await http_get_text(url, headers=headers)
    data: dict[str, Any] = json.loads(text)
    article_list: list[dict[str, Any]] = data.get("data", [])
    items: list[HotItem] = []
    for item in article_list:
        item_id: str = item.get("id", "")
        hot_item: HotItem = HotItem(
            id=item_id,
            title=item.get("title"),
            cover=item.get("cover"),
            author=item.get("author"),
            time=get_time(item.get("createtime")),
            url=f"https://www.yystv.cn/p/{item_id}",
            mobile_url=f"https://www.yystv.cn/p/{item_id}",
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "全部文章")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 全部文章\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.author:
                lines.append(f"- **作者**: {item.author}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """游研社全部文章"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 全部文章] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
