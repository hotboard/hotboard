import asyncio
from enum import StrEnum
from typing import Any

import typer

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, get_time, http_get

PLATFORM_NAME = "AcFun"


class ChannelType(StrEnum):
    """频道类型"""

    ALL = "-1"
    BANGUMI = "155"
    ANIMATION = "1"
    ENTERTAINMENT = "60"
    LIFE = "201"
    MUSIC = "58"
    DANCE = "123"
    GAME = "59"
    TECH = "70"
    FILM = "68"
    SPORT = "69"
    FISHPOND = "125"


class TimeRange(StrEnum):
    """时间范围"""

    DAY = "DAY"
    THREE_DAYS = "THREE_DAYS"
    WEEK = "WEEK"


CHANNEL_CONFIGS: dict[str, str] = {
    ChannelType.ALL: "综合",
    ChannelType.BANGUMI: "番剧",
    ChannelType.ANIMATION: "动画",
    ChannelType.ENTERTAINMENT: "娱乐",
    ChannelType.LIFE: "生活",
    ChannelType.MUSIC: "音乐",
    ChannelType.DANCE: "舞蹈·偶像",
    ChannelType.GAME: "游戏",
    ChannelType.TECH: "科技",
    ChannelType.FILM: "影视",
    ChannelType.SPORT: "体育",
    ChannelType.FISHPOND: "鱼塘",
}

RANGE_CONFIGS: dict[str, str] = {
    TimeRange.DAY: "今日",
    TimeRange.THREE_DAYS: "三日",
    TimeRange.WEEK: "本周",
}


async def fetch(channel_type: str = "-1", time_range: str = "DAY") -> list[HotItem]:
    """获取 AcFun 排行榜"""
    channel_id: str = "" if channel_type == "-1" else channel_type
    url: str = (
        f"https://www.acfun.cn/rest/pc-direct/rank/channel?channelId={channel_id}&rankLimit=30&rankPeriod={time_range}"
    )

    headers: dict[str, str] = {
        "Referer": f"https://www.acfun.cn/rank/list/?cid=-1&pcid={channel_type}&range={time_range}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    }

    result: dict[str, Any] = await http_get(url, headers)

    items: list[HotItem] = []
    for item in result.get("rankList", []):
        douga_id: str = item.get("dougaId")
        hot_item: HotItem = HotItem(
            id=douga_id,
            title=item.get("contentTitle"),
            desc=item.get("contentDesc"),
            cover=item.get("coverUrl"),
            author=item.get("userName"),
            time=get_time(item.get("contributeTime")),
            hot=item.get("viewCountShow"),
            url=f"https://www.acfun.cn/v/ac{douga_id}",
            mobile_url=item.get("shareUrl"),  # f"https://m.acfun.cn/v/?ac={douga_id}"
        )
        items.append(hot_item)

    return items


def format_output(
    items: list[HotItem], channel_type: str, time_range: str, format: OutputFormat
) -> str:
    """格式化输出"""
    type_name: str = CHANNEL_CONFIGS[channel_type]
    range_name: str = RANGE_CONFIGS[time_range]

    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, f"{type_name} · {range_name}")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 排行榜 · {type_name} · {range_name}\n",
            f"**总数**: {len(items)} 条\n",
        ]

        for item in items:
            lines.append(f"## {item.title}\n")
            if item.hot:
                lines.append(f"- **热度**: {item.hot}")
            if item.author:
                lines.append(f"- **UP 主**: {item.author}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            if item.desc:
                desc_preview: str = item.desc[:100] + "..." if len(item.desc) > 100 else item.desc
                lines.append(f"- **简介**: {desc_preview}")
            lines.append(f"- **链接**: {item.url}\n")

        return "\n".join(lines)


def main(
    type: ChannelType = typer.Option(
        ChannelType.ALL,
        help="频道类型：" + ", ".join([f"{k}={v}" for k, v in CHANNEL_CONFIGS.items()]),
    ),
    range: TimeRange = typer.Option(
        TimeRange.DAY, help="时间范围：" + ", ".join([f"{k}={v}" for k, v in RANGE_CONFIGS.items()])
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """AcFun 排行榜"""
    items: list[HotItem] = asyncio.run(fetch(type, range))
    print(format_output(items, type, range, format))
    logger.info(
        f"获取 [{PLATFORM_NAME} - {CHANNEL_CONFIGS[type]} · {RANGE_CONFIGS[range]}] 成功，共 {len(items)} 条"
    )
