import asyncio
from enum import StrEnum
from typing import Any

import typer

from hotboard.core.logger import logger
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import format_items_json, http_get

PLATFORM_NAME = "哔哩哔哩"


class CategoryType(StrEnum):
    """分类类型"""

    ALL = "0"
    ANIMATION = "1"
    MUSIC = "3"
    GAME = "4"
    ENTERTAINMENT = "5"
    TECH = "188"
    KICHIKU = "119"
    DANCE = "129"
    FASHION = "155"
    LIFE = "160"
    GUOCHUANG = "168"
    FILM = "181"


CATEGORY_CONFIGS: dict[str, str] = {
    CategoryType.ALL: "全站",
    CategoryType.ANIMATION: "动画",
    CategoryType.MUSIC: "音乐",
    CategoryType.GAME: "游戏",
    CategoryType.ENTERTAINMENT: "娱乐",
    CategoryType.TECH: "科技",
    CategoryType.KICHIKU: "鬼畜",
    CategoryType.DANCE: "舞蹈",
    CategoryType.FASHION: "时尚",
    CategoryType.LIFE: "生活",
    CategoryType.GUOCHUANG: "国创相关",
    CategoryType.FILM: "影视",
}


async def fetch(type_id: str = "0") -> list[HotItem]:
    """获取 B 站热门榜单"""
    url: str = (
        f"https://api.bilibili.com/x/web-interface/ranking?jsonp=jsonp?rid={type_id}&type=all&callback=__jp0"
    )

    headers: dict[str, str] = {
        "Referer": "https://www.bilibili.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    }

    result: dict[str, Any] = await http_get(url, headers)
    print(result)
    items: list[HotItem] = []
    for item in result.get("data", {}).get("list", []):
        bvid: str = item.get("bvid")
        pic: str = item.get("pic")
        if pic and pic.startswith("http:"):
            pic = pic.replace("http:", "https:")

        hot_item: HotItem = HotItem(
            id=bvid,
            title=item.get("title"),
            cover=pic,
            author=item.get("author"),
            hot=item.get("play"),  # 播放量。item.get("video_review") 是弹幕数量。
            url=f"https://www.bilibili.com/video/{bvid}",
            mobile_url=f"https://m.bilibili.com/video/{bvid}",
        )
        items.append(hot_item)

    return items


def format_output(items: list[HotItem], type_name: str, format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, type_name)
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 热榜 · {type_name}\n",
            f"**总数**: {len(items)} 条\n",
        ]

        for item in items:
            lines.append(f"## {item.title}\n")
            if item.hot:
                lines.append(f"- **播放量**: {item.hot}")
            if item.author:
                lines.append(f"- **UP 主**: {item.author}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")

        return "\n".join(lines)


def main(
    type: CategoryType = typer.Option(
        CategoryType.ALL,
        help="分类类型：" + ", ".join([f"{k}={v}" for k, v in CATEGORY_CONFIGS.items()]),
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """哔哩哔哩热榜"""
    items: list[HotItem] = asyncio.run(fetch(type))
    type_name = CATEGORY_CONFIGS[type]
    print(format_output(items, type_name, format))
    logger.info(f"获取 [{PLATFORM_NAME} - {type_name}] 热榜成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
