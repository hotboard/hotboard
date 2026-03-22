import asyncio
from enum import StrEnum
from typing import Any

import typer

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, get_time, http_get

PLATFORM_NAME = "米游社"


class GameType(StrEnum):
    """游戏类型"""

    BH3 = "1"
    YS = "2"
    BH2 = "3"
    WDSJ = "4"
    DBY = "5"
    BHXQTD = "6"
    ZQL = "8"


class ContentType(StrEnum):
    """内容类型"""

    NOTICE = "1"
    ACTIVITY = "2"
    NEWS = "3"


GAME_NAMES: dict[str, str] = {
    GameType.BH3: "崩坏 3",
    GameType.YS: "原神",
    GameType.BH2: "崩坏学园 2",
    GameType.WDSJ: "未定事件簿",
    GameType.DBY: "大别野",
    GameType.BHXQTD: "崩坏：星穹铁道",
    GameType.ZQL: "绝区零",
}

CONTENT_NAMES: dict[str, str] = {
    ContentType.NOTICE: "公告",
    ContentType.ACTIVITY: "活动",
    ContentType.NEWS: "资讯",
}


async def fetch(game: str = "2", content_type: str = "3") -> list[HotItem]:
    """获取米游社榜单"""
    url: str = (
        f"https://bbs-api-static.miyoushe.com/painter/wapi/getNewsList?client_type=4&gids={game}&last_id=&page_size=30&type={content_type}"
    )
    data: dict[str, Any] = await http_get(url)
    item_list: list[dict[str, Any]] = data.get("data", {}).get("list", [])
    items: list[HotItem] = []
    for item in item_list:
        post: dict[str, Any] = item.get("post", {})
        post_id: str = post.get("post_id", "")
        hot_item: HotItem = HotItem(
            id=post_id,
            title=post.get("subject"),
            desc=post.get("content"),
            cover=post.get("cover") or post.get("images", [])[0],
            time=get_time(post.get("created_at")),
            url=f"https://www.miyoushe.com/ys/article/{post_id}",
            mobile_url=f"https://m.miyoushe.com/ys/#/article/{post_id}",
        )
        items.append(hot_item)
    return items


def format_output(
    items: list[HotItem], game_name: str, content_name: str, format: OutputFormat
) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, f"{game_name} - 最新{content_name}")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} · {game_name} - 最新{content_name}\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.desc:
                lines.append(f"- **简介**: {item.desc}")
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


def main(
    game: GameType = typer.Option(
        GameType.YS, help="游戏类型：" + ", ".join([f"{k}={v}" for k, v in GAME_NAMES.items()])
    ),
    type: ContentType = typer.Option(
        ContentType.NEWS,
        help="内容类型：" + ", ".join([f"{k}={v}" for k, v in CONTENT_NAMES.items()]),
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """米游社游戏公告/活动/咨询"""
    items: list[HotItem] = asyncio.run(fetch(game, type))
    game_name = GAME_NAMES[game]
    content_name = CONTENT_NAMES[type]
    print(format_output(items, game_name, content_name, format))
    logger.info(
        f"获取 [{PLATFORM_NAME} · {game_name} - 最新{content_name}] 成功，共 {len(items)} 条"
    )
