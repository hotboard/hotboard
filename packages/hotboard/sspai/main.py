import asyncio
import typer
from urllib.parse import quote
from enum import StrEnum
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import format_items_json, get_time, http_get
from hotboard.core.logger import logger

PLATFORM_NAME = "少数派"


class ArticleType(StrEnum):
    """文章类型"""

    HOT = "热门文章"
    APP = "应用推荐"
    LIFE = "生活方式"
    EFFICIENCY = "效率技巧"
    PODCAST = "少数派播客"


async def fetch(article_type: str = "热门文章") -> list[HotItem]:
    """获取少数派热榜"""
    url: str = f"https://sspai.com/api/v1/article/tag/page/get?limit=40&tag={quote(article_type)}"
    data: dict[str, any] = await http_get(url)
    item_list: list[dict[str, any]] = data.get("data", [])
    items: list[HotItem] = []
    for item in item_list:
        item_id: str = item.get("id")
        hot_item: HotItem = HotItem(
            id=item_id,
            title=item.get("title"),
            desc=item.get("summary"),
            author=item.get("author").get("nickname"),
            hot=item.get("like_count"),
            time=get_time(item.get("released_time")),
            url=f"https://sspai.com/post/{item_id}",
            mobile_url=f"https://sspai.com/post/{item_id}",
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], article_type: str, format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, article_type)
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - {article_type}\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.desc:
                desc_preview: str = item.desc[:100] + "..." if len(item.desc) > 100 else item.desc
                lines.append(f"- **描述**: {desc_preview}")
            if item.author:
                lines.append(f"- **作者**: {item.author}")
            if item.hot:
                lines.append(f"- **点赞**: {item.hot}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(
    type: ArticleType = typer.Option(
        ArticleType.HOT, help="文章类型：" + ", ".join([f"{t.value}" for t in ArticleType])
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """少数派热榜"""
    items: list[HotItem] = asyncio.run(fetch(type.value))
    print(format_output(items, type.value, format))
    logger.info(f"获取 [{PLATFORM_NAME} - {type.value}] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
