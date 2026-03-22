import asyncio
from typing import Any
from urllib.parse import quote

import typer

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, http_get

PLATFORM_NAME = "中央气象台"


async def fetch(province: str = "") -> list[HotItem]:
    """获取中央气象台气象预警"""
    url: str = f"http://www.nmc.cn/rest/findAlarm?pageNo=1&pageSize=20&signaltype=&signallevel=&province={quote(province)}"
    data: dict[str, Any] = await http_get(url)
    alarm_list: list[dict[str, Any]] = data.get("data", {}).get("page", {}).get("list", [])
    items: list[HotItem] = []
    for item in alarm_list:
        issue_time: str = item.get("issuetime", "")
        title: str = item.get("title", "")
        hot_item: HotItem = HotItem(
            id=item.get("alertid"),
            title=title,
            desc=f"{issue_time} {title}" if issue_time else title,
            cover=item.get("pic"),
            time=issue_time,
            url=f"http://nmc.cn{item.get('url')}",
            mobile_url=f"http://nmc.cn{item.get('url')}",
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], province: str, format: OutputFormat) -> str:
    """格式化输出"""
    area: str = province if province else "全国"
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, f"{area} 气象预警")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - {area} 气象预警\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.desc:
                lines.append(f"- **描述**: {item.desc}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(
    province: str = typer.Option("", help="预警区域（省份名称，例如：广东省）"),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """中央气象台气象预警"""
    items: list[HotItem] = asyncio.run(fetch(province))
    area: str = province if province else "全国"
    print(format_output(items, province, format))
    logger.info(f"获取 [{PLATFORM_NAME} - {area}] 气象预警成功，共 {len(items)} 条")
