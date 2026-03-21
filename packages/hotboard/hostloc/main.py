import asyncio

import feedparser
import typer
from enum import StrEnum

from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import http_get_text, get_time, format_items_json
from hotboard.core.logger import logger

PLATFORM_NAME = "全球主机交流"


class ListType(StrEnum):
    """榜单类型"""

    HOT = "hot"
    DIGEST = "digest"
    NEW = "new"
    NEWTHREAD = "newthread"


LIST_CONFIGS: dict[str, str] = {
    ListType.HOT: "最新热门",
    ListType.DIGEST: "最新精华",
    ListType.NEW: "最新回复",
    ListType.NEWTHREAD: "最新发表",
}


async def fetch(type: str = "hot") -> list[HotItem]:
    """获取全球主机交流榜单"""
    url: str = f"https://hostloc.com/forum.php?mod=guide&view={type}&rss=1"

    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    }

    content: str = await http_get_text(url, headers)
    feed: feedparser.util.FeedParserDict = feedparser.parse(content)

    items: list[HotItem] = []
    for entry in feed.get("entries"):
        content_text: str = (
            entry.get("content", [{}])[0].get("value", "") if "content" in entry else ""
        )
        desc: str = content_text.strip() if content_text else entry.get("summary")

        guid: str = entry.get("id", entry.get("guid"))

        hot_item: HotItem = HotItem(
            id=guid,
            title=entry.get("title"),
            desc=desc,
            author=entry.get("author"),
            time=get_time(entry.get("published")),
            url=entry.get("link"),
            mobile_url=entry.get("link"),
        )
        items.append(hot_item)

    return items


def format_output(items: list[HotItem], type: str, format: OutputFormat) -> str:
    """格式化输出"""
    type_name = LIST_CONFIGS[type]

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
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            if item.desc:
                desc_preview: str = item.desc[:100] + "..." if len(item.desc) > 100 else item.desc
                lines.append(f"- **摘要**: {desc_preview}")
            lines.append(f"- **链接**: {item.url}\n")

        return "\n".join(lines)


def main(
    type: ListType = typer.Option(
        ListType.HOT, help="榜单类型：" + ", ".join([f"{k}={v}" for k, v in LIST_CONFIGS.items()])
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """全球主机交流论坛"""
    items: list[HotItem] = asyncio.run(fetch(type))
    print(format_output(items, type, format))
    logger.info(f"获取 [{PLATFORM_NAME} - {type}] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
