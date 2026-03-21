import asyncio
from typing import Any

import typer

from hotboard.core.logger import logger
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import format_items_json, get_time, http_get

PLATFORM_NAME = "澎湃新闻"


async def fetch() -> list[HotItem]:
    """获取澎湃新闻热榜"""
    url: str = "https://cache.thepaper.cn/contentapi/wwwIndex/rightSidebar"
    data: dict[str, Any] = await http_get(url)
    hot_news: list[dict[str, Any]] = data.get("data", {}).get("hotNews", [])
    items: list[HotItem] = []
    for item in hot_news:
        cont_id: str = item.get("contId", "")
        hot_item: HotItem = HotItem(
            id=cont_id,
            title=item.get("name"),
            cover=item.get("pic"),
            hot=item.get("praiseTimes"),
            time=get_time(item.get("pubTimeLong")),
            url=f"https://www.thepaper.cn/newsDetail_forward_{cont_id}",
            mobile_url=f"https://m.thepaper.cn/newsDetail_forward_{cont_id}",
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
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.hot:
                lines.append(f"- **点赞**: {item.hot}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """澎湃新闻热榜"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 热榜] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
