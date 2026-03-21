import asyncio
import typer
from enum import StrEnum
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import http_get, get_time, format_items_json
from hotboard.core.logger import logger

PLATFORM_NAME = "知乎"


class ListType(StrEnum):
    """榜单类型"""

    HOT = "hot"
    DAILY = "daily"


LIST_NAMES: dict[str, str] = {
    ListType.HOT: "热榜",
    ListType.DAILY: "日报",
}


async def fetch_hot() -> list[HotItem]:
    """获取知乎热榜"""
    url: str = "https://api.zhihu.com/topstory/hot-lists/total?limit=50"
    result: dict[str, any] = await http_get(url)
    data_list: list[dict[str, any]] = result.get("data", [])
    items: list[HotItem] = []
    for item in data_list:
        target: dict[str, any] = item.get("target", {})
        question_id: str = target.get("url", "").split("/")[-1]
        detail_text: str = item.get("detail_text", "")
        children: list[dict[str, any]] = item.get("children", [])
        hot_item: HotItem = HotItem(
            id=target.get("id"),
            title=target.get("title"),
            desc=target.get("excerpt"),
            cover=children[0].get("thumbnail") if children else None,
            time=get_time(target.get("created", 0)),
            hot=detail_text.split(" ")[0] if detail_text else None,
            url=f"https://www.zhihu.com/question/{question_id}",
            mobile_url=f"https://www.zhihu.com/question/{question_id}",
        )
        items.append(hot_item)
    return items


async def fetch_daily() -> list[HotItem]:
    """获取知乎日报"""
    url: str = "https://daily.zhihu.com/api/4/news/latest"
    headers: dict[str, str] = {
        "Referer": "https://daily.zhihu.com/api/4/news/latest",
        "Host": "daily.zhihu.com",
    }
    result: dict[str, any] = await http_get(url, headers)
    stories: list[dict[str, any]] = result.get("stories", [])
    filtered_stories: list[dict[str, any]] = [s for s in stories if s.get("type") == 0]
    items: list[HotItem] = []
    for item in filtered_stories:
        images: list[str] = item.get("images", [])
        item_url: str = item.get("url")
        hot_item: HotItem = HotItem(
            id=item.get("id"),
            title=item.get("title"),
            cover=images[0] if images else None,
            author=item.get("hint"),
            url=item_url,
            mobile_url=item_url,
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], list_name: str, format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, list_name)
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - {list_name}\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.hot:
                lines.append(f"- **热度**: {item.hot}")
            if item.desc:
                lines.append(f"- **摘要**: {item.desc}")
            if item.author:
                lines.append(f"- **作者**: {item.author}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(
    type: ListType = typer.Option(
        ListType.HOT, help="榜单类型：" + ", ".join([f"{k}={v}" for k, v in LIST_NAMES.items()])
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """知乎热榜"""
    items: list[HotItem] = asyncio.run(fetch_daily() if type == ListType.DAILY else fetch_hot())
    list_name = LIST_NAMES[type]
    print(format_output(items, list_name, format))
    logger.info(f"获取 [{PLATFORM_NAME} - {list_name}] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
