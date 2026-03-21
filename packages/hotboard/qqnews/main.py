import asyncio
import typer
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import format_items_json, get_time, http_get
from hotboard.core.logger import logger

PLATFORM_NAME = "腾讯新闻"


async def fetch() -> list[HotItem]:
    """获取腾讯新闻热点榜"""
    url: str = "https://r.inews.qq.com/gw/event/hot_ranking_list?page_size=50"
    data: dict[str, any] = await http_get(url)
    newslist: list[dict[str, any]] = data.get("idlist")[0].get("newslist")
    item_list: list[dict[str, any]] = newslist[1:] if len(newslist) > 1 else newslist
    items: list[HotItem] = []
    for item in item_list:
        item_id: str = item.get("id")
        hot_item: HotItem = HotItem(
            id=item_id,
            title=item.get("title"),
            desc=item.get("abstract"),
            cover=item.get("miniProShareImage"),
            author=item.get("source"),
            hot=item.get("hotEvent").get("hotScore"),
            time=get_time(item.get("timestamp")),
            url=f"https://new.qq.com/rain/a/{item_id}",
            mobile_url=f"https://view.inews.qq.com/k/{item_id}",
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "热点榜")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 热点榜\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.desc:
                lines.append(f"- **描述**: {item.desc}")
            if item.author:
                lines.append(f"- **来源**: {item.author}")
            if item.hot:
                lines.append(f"- **热度**: {item.hot}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """腾讯新闻热点榜"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 热点榜] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
