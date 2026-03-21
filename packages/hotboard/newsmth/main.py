import asyncio
import typer
from urllib.parse import quote
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import http_get, format_items_json, get_time
from hotboard.core.logger import logger

PLATFORM_NAME = "水木社区"


async def fetch() -> list[HotItem]:
    """获取水木社区热门话题"""
    url: str = "https://wap.newsmth.net/wap/api/hot/global"
    data: dict[str, any] = await http_get(url)
    topics: list[dict[str, any]] = data.get("data", {}).get("topics", [])
    items: list[HotItem] = []
    for topic in topics:
        article: dict[str, any] = topic.get("article", {})
        topic_id: str = article.get("topicId")
        board_title: str = topic.get("board").get("title")
        article_url: str = (
            f"https://wap.newsmth.net/article/{topic_id}?title={quote(board_title)}&from=home"
        )
        hot_item: HotItem = HotItem(
            id=topic.get("firstArticleId"),
            title=article.get("subject"),
            desc=article.get("body"),
            author=article.get("account").get("name"),
            time=get_time(article.get("postTime")),
            url=article_url,
            mobile_url=article_url,
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "热门话题")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 热门话题\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.desc:
                lines.append(f"- **简介**: {item.desc}")
            if item.author:
                lines.append(f"- **作者**: {item.author}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """水木社区热门话题"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 热门话题] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
