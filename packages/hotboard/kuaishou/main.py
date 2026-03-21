import asyncio
import json
import typer
from urllib.parse import unquote
from hotboard.core.types import HotItem, OutputFormat
from hotboard.core.utils import http_get_text, format_items_json
from hotboard.core.logger import logger

PLATFORM_NAME = "快手"
APOLLO_STATE_PREFIX: str = "window.__APOLLO_STATE__="


async def fetch() -> list[HotItem]:
    """获取快手热榜"""
    url: str = "https://www.kuaishou.com/?isHome=1"
    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    }
    html: str = await http_get_text(url, headers)
    start: int = html.find(APOLLO_STATE_PREFIX)
    if start == -1:
        return []
    script_slice: str = html[start + len(APOLLO_STATE_PREFIX) :]
    sentinel_a: int = script_slice.find(";(function(")
    sentinel_b: int = script_slice.find("</script>")
    cut_index: int = (
        min(sentinel_a, sentinel_b)
        if sentinel_a != -1 and sentinel_b != -1
        else max(sentinel_a, sentinel_b)
    )
    if cut_index == -1:
        return []
    raw: str = script_slice[:cut_index].strip().rstrip(";")
    last_brace: int = raw.rfind("}")
    clean_raw: str = raw[: last_brace + 1] if last_brace != -1 else raw
    json_object: dict[str, any] = json.loads(clean_raw)
    default_client: dict[str, any] = json_object.get("defaultClient", {})
    all_items: list[dict[str, any]] = default_client.get(
        '$ROOT_QUERY.visionHotRank({"page":"home"})', {}
    ).get("items", []) or default_client.get(
        '$ROOT_QUERY.visionHotRank({"page":"home","platform":"web"})', {}
    ).get(
        "items", []
    )
    items: list[HotItem] = []
    for item in all_items:
        item_id: str = item.get("id")
        hot_item_data: dict[str, any] = default_client.get(item_id, {})
        photo_id: str = hot_item_data.get("photoIds").get("json")[0]
        poster: str = hot_item_data.get("poster")
        hot_item: HotItem = HotItem(
            id=hot_item_data.get("id"),
            title=hot_item_data.get("name"),
            cover=unquote(poster),
            hot=hot_item_data.get("hotValue"),
            url=f"https://www.kuaishou.com/short-video/{photo_id}",
            mobile_url=f"https://www.kuaishou.com/short-video/{photo_id}",
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "热榜")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 热榜\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.hot:
                lines.append(f"- **热度**: {item.hot}")
            if item.cover:
                lines.append(f"- **封面**: {item.cover}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """快手热榜"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 热榜] 成功，共 {len(items)} 条")


def run():
    """CLI 入口点"""
    typer.run(main)
