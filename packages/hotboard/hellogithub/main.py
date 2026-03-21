import asyncio

import typer
from enum import StrEnum

from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import http_get, get_time, format_items_json
from hotboard.core.logger import logger

PLATFORM_NAME = "HelloGitHub"


class SortType(StrEnum):
    """排序类型"""

    FEATURED = "featured"
    ALL = "all"


SORT_CONFIGS: dict[str, str] = {
    SortType.FEATURED: "精选",
    SortType.ALL: "全部",
}


async def fetch(sort: str = "featured") -> list[HotItem]:
    """获取 HelloGitHub 热门仓库"""
    url: str = f"https://abroad.hellogithub.com/v1/?sort_by={sort}&tid=&page=1"

    result: dict[str, any] = await http_get(url)

    items: list[HotItem] = []
    for item in result["data"]:
        item_id: str = item.get("item_id")
        title: str = item.get("title")
        summary: str = item.get("summary")
        author: str = item.get("author")
        updated_at: str = item.get("updated_at")
        clicks_total: int = item.get("clicks_total")

        hot_item: HotItem = HotItem(
            id=item_id,
            title=title,
            desc=summary,
            time=get_time(updated_at),
            hot=clicks_total,
            url=f"https://hellogithub.com/repository/{item_id}",
            mobile_url=f"https://hellogithub.com/repository/{item_id}",
            author=author,
        )
        items.append(hot_item)

    return items


def format_output(items: list[HotItem], sort: str, format: OutputFormat) -> str:
    """格式化输出"""
    sort_name = SORT_CONFIGS[sort]

    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, sort_name)
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - {sort_name}\n",
            f"**总数**: {len(items)} 条\n",
        ]

        for item in items:
            lines.append(f"## {item.title}\n")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            if item.author:
                lines.append(f"- **作者**: {item.author}")
            if item.hot:
                lines.append(f"- **点击**: {item.hot}")
            if item.desc:
                lines.append(f"- **描述**: {item.desc}")
            lines.append(f"- **链接**: {item.url}\n")

        return "\n".join(lines)


def main(
    sort: SortType = typer.Option(
        SortType.FEATURED,
        help="排序类型：" + ", ".join([f"{k}={v}" for k, v in SORT_CONFIGS.items()]),
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """HelloGitHub 热门仓库"""
    items: list[HotItem] = asyncio.run(fetch(sort))
    print(format_output(items, sort, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 热门仓库] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
