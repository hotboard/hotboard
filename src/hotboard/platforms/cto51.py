import asyncio
import time
from typing import Any

import typer

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, get_time, http_get, md5_hash

PLATFORM_NAME = "51CTO"


async def get_token() -> str:
    """获取 51CTO API token"""
    url: str = "https://api-media.51cto.com/api/token-get"
    result: dict[str, Any] = await http_get(url)
    return result.get("data", {}).get("data", {}).get("token", "")


def sign(request_path: str, params: dict[str, Any], timestamp: int, token: str) -> str:
    """生成请求签名"""
    params["timestamp"] = timestamp
    params["token"] = token
    sorted_keys: list[str] = sorted(params.keys())
    sorted_keys_str: str = "".join(sorted_keys)
    path_hash: str = md5_hash(request_path)
    token_time_hash: str = md5_hash(token) + str(timestamp)
    inner_hash: str = md5_hash(sorted_keys_str + token_time_hash)
    return md5_hash(path_hash + inner_hash)


async def fetch() -> list[HotItem]:
    """获取 51CTO 推荐榜"""
    token: str = await get_token()
    timestamp: int = int(time.time() * 1000)
    params: dict[str, Any] = {
        "page": 1,
        "page_size": 50,
        "limit_time": 0,
        "name_en": "",
    }
    request_path: str = "index/index/recommend"
    signature: str = sign(request_path, params.copy(), timestamp, token)
    url: str = "https://api-media.51cto.com/index/index/recommend"
    query_params: dict[str, Any] = {
        **params,
        "timestamp": timestamp,
        "token": token,
        "sign": signature,
    }
    # 构建完整 URL
    query_str: str = "&".join([f"{k}={v}" for k, v in query_params.items()])
    full_url: str = f"{url}?{query_str}"
    result: dict[str, Any] = await http_get(full_url)
    items: list[HotItem] = []
    item_list: list[dict[str, Any]] = result.get("data", {}).get("data", {}).get("list", [])
    for item in item_list:
        hot_item: HotItem = HotItem(
            id=item.get("source_id"),
            title=item.get("title"),
            desc=item.get("abstract"),
            cover=item.get("cover"),
            time=get_time(item.get("pubdate")),
            url=item.get("url"),
            mobile_url=item.get("url"),
        )
        items.append(hot_item)
    return items


def format_output(items: list[HotItem], format: OutputFormat) -> str:
    """格式化输出"""
    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, "推荐榜")
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} - 推荐榜\n",
            f"**总数**: {len(items)} 条\n",
        ]
        for item in items:
            lines.append(f"## {item.title}\n")
            if item.desc:
                lines.append(f"- **摘要**: {item.desc}")
            if item.time:
                lines.append(f"- **时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式")):
    """51CTO 推荐榜"""
    items: list[HotItem] = asyncio.run(fetch())
    print(format_output(items, format))
    logger.info(f"获取 [{PLATFORM_NAME} - 推荐榜] 成功，共 {len(items)} 条")
