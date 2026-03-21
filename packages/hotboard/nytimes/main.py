import asyncio
import feedparser
import typer
from enum import StrEnum
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import format_items_json, get_time, http_get_text
from hotboard.core.logger import logger

PLATFORM_NAME = "纽约时报"


class AreaType(StrEnum):
    """地区类型"""

    CHINA = "china"
    GLOBAL = "global"


AREA_NAMES: dict[str, str] = {
    AreaType.CHINA: "中文网",
    AreaType.GLOBAL: "全球版",
}


async def fetch(area: str = "china") -> list[HotItem]:
    """获取纽约时报"""
    url: str = (
        "https://cn.nytimes.com/rss/"
        if area == "china"
        else "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
    )
    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    }
    text: str = await http_get_text(url, headers=headers)
    feed: feedparser.util.FeedParserDict = feedparser.parse(text)
    items: list[HotItem] = []
    for entry in feed.get("entries"):
        link: str = entry.get("link")
        hot_item: HotItem = HotItem(
            id=entry.get("id"),
            title=entry.get("title"),
            desc=entry.get("summary"),
            author=entry.get("author") or None,
            time=get_time(entry.get("published")),
            url=link,
            mobile_url=link,
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], area_name: str, format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, area_name)
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - {area_name}\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.desc:
                desc_preview: str = item.desc[:100] + "..." if len(item.desc) > 100 else item.desc
                lines.append(f"- **描述**: {desc_preview}")
            if item.author:
                lines.append(f"- **作者**: {item.author}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(
    type: AreaType = typer.Option(
        AreaType.CHINA, help="地区类型：" + ", ".join([f"{k}={v}" for k, v in AREA_NAMES.items()])
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """纽约时报"""
    items: list[HotItem] = asyncio.run(fetch(type))
    area_name = AREA_NAMES[type]
    print(format_output(items, area_name, format))
    logger.info(f"获取 [{PLATFORM_NAME} - {area_name}] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
