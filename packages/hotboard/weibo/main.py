import asyncio
import typer
from urllib.parse import quote
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import http_get, format_items_json
from hotboard.core.logger import logger

PLATFORM_NAME = "微博"


async def fetch() -> list[HotItem]:
    """获取微博热搜榜"""
    url: str = "https://weibo.com/ajax/side/hotSearch"
    headers: dict[str, str] = {
        "Referer": "https://weibo.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }
    result: dict[str, any] = await http_get(url, headers)
    realtime: list[dict[str, any]] = result.get("data", {}).get("realtime", [])
    items: list[HotItem] = []
    for item in realtime:
        title: str = item.get("word")
        url: str = f"https://s.weibo.com/weibo?q={quote(title)}"
        hot_item: HotItem = HotItem(
            title=title,
            url=url,
            mobile_url=url,
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "热搜榜")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 热搜榜\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """微博热搜榜"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 热搜榜] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
