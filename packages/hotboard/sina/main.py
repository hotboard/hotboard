import asyncio
import typer
from enum import StrEnum
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import format_items_json, http_get
from hotboard.core.logger import logger

PLATFORM_NAME = "新浪网"


class RankType(StrEnum):
    """榜单类型"""

    ALL = "all"
    HOTCMNT = "hotcmnt"
    MINIVIDEO = "minivideo"
    ENT = "ent"
    AI = "ai"
    AUTO = "auto"
    MOTHER = "mother"
    FASHION = "fashion"
    TRAVEL = "travel"
    ESG = "esg"


RANK_NAMES: dict[str, str] = {
    RankType.ALL: "新浪热榜",
    RankType.HOTCMNT: "热议榜",
    RankType.MINIVIDEO: "视频热榜",
    RankType.ENT: "娱乐热榜",
    RankType.AI: "AI 热榜",
    RankType.AUTO: "汽车热榜",
    RankType.MOTHER: "育儿热榜",
    RankType.FASHION: "时尚热榜",
    RankType.TRAVEL: "旅游热榜",
    RankType.ESG: "ESG 热榜",
}


async def fetch(rank_type: str = "all") -> list[HotItem]:
    """获取新浪网热榜"""
    url: str = f"https://newsapp.sina.cn/api/hotlist?newsId=HB-1-snhs%2Ftop_news_list-{rank_type}"
    data: dict[str, any] = await http_get(url)
    hot_list: list[dict[str, any]] = data.get("data", {}).get("hotList", [])
    items: list[HotItem] = []
    for item in hot_list:
        base_data: dict[str, any] = item.get("base", {}).get("base", {})
        info_data: dict[str, any] = item.get("info", {})
        item_url: str = base_data.get("url", "")
        hot_item: HotItem = HotItem(
            id=base_data.get("uniqueId"),
            title=info_data.get("title"),
            hot=info_data.get("hotValue"),
            url=item_url,
            mobile_url=item_url,
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], rank_name: str, format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, rank_name)
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - {rank_name}\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.hot:
                lines.append(f"- **热度**: {item.hot}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(
    type: RankType = typer.Option(
        RankType.ALL, help="榜单类型：" + ", ".join([f"{k}={v}" for k, v in RANK_NAMES.items()])
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """新浪网热榜"""
    items: list[HotItem] = asyncio.run(fetch(type))
    rank_name = RANK_NAMES[type]
    print(format_output(items, rank_name, format))
    logger.info(f"获取 [{PLATFORM_NAME} - {rank_name}] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
