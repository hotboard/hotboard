import asyncio
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any

import typer

from hotboard.core.logger import logger
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import format_items_json, get_time, http_get

PLATFORM_NAME = "中国地震台"


class LocationRange(StrEnum):
    """地理区域"""

    CHINA = "china"
    WORLD = "world"


async def fetch(days: int = 7, location_range: str = "1") -> list[HotItem]:
    """获取中国地震台地震速报"""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)

    start_time_str = start_time.strftime("%Y-%m-%d+%H:%M:%S")
    end_time_str = end_time.strftime("%Y-%m-%d+%H:%M:%S")

    url: str = (
        f"https://www.cenc.ac.cn/prodlaunch-web-backend/open/data/catalogs?orderBy=id&isAsc=false&startMg=3&endMg=10&startTime={start_time_str}&endTime={end_time_str}"
    )

    if location_range:
        url += f"&locationRange={location_range}"

    headers: dict[str, str] = {
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Referer": "https://www.cenc.ac.cn/earthquake-manage-publish-web/search",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
    }

    result: dict[str, Any] = await http_get(url, headers)

    items: list[HotItem] = []
    for item in result["data"]:
        earthquake_id: str = item.get("id")
        location: str = item.get("locName")
        magnitude: str = item.get("magnitude")
        origin_time: str = item.get("oriTime")

        # 构建详细描述
        content_parts: list[str] = [
            f"发震时刻 (UTC+8)：{origin_time}",
            f"参考位置：{location}",
            f"震级 (M)：{magnitude}",
            f"纬度 (°)：{item.get('epiLat')}",
            f"经度 (°)：{item.get('epiLon')}",
            f"深度 (千米)：{item.get('focDepth')}",
        ]

        url = f"https://www.cenc.ac.cn/earthquake-manage-publish-web/product-list/{earthquake_id}/summarize"

        hot_item: HotItem = HotItem(
            id=earthquake_id,
            title=f"{location} 发生 {magnitude} 级地震",
            desc="\n".join(content_parts),
            time=get_time(origin_time),
            url=url,
            mobile_url=url,
        )
        items.append(hot_item)

    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "地震速报")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 地震速报\n",
            f"**总数**: {len(items)} 条\n",
        ]

        for item in items:
            lines.append(f"## {item.title}\n")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            if item.desc:
                lines.append(f"- **详情**:\n```\n{item.desc}\n```")
            lines.append(f"- **链接**: {item.url}\n")

        return "\n".join(lines)


def main(
    days: int = typer.Option(7, help="查询天数"),
    range: LocationRange = typer.Option(
        LocationRange.CHINA, help="地理区域：china=中国范围，world=世界范围"
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """中国地震台地震速报"""
    location_range = "" if range == LocationRange.WORLD else "1"
    items: list[HotItem] = asyncio.run(fetch(days, location_range))
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 地震速报] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
