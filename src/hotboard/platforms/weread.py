import asyncio
import hashlib
from enum import StrEnum
from typing import Any

import typer

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, get_time, http_get

PLATFORM_NAME = "微信读书"


class RankType(StrEnum):
    """排行榜类型"""

    RISING = "rising"
    HOT_SEARCH = "hot_search"
    NEWBOOK = "newbook"
    NOVEL = "general_novel_rising"
    ALL = "all"


RANK_NAMES: dict[str, str] = {
    RankType.RISING: "飙升榜",
    RankType.HOT_SEARCH: "热搜榜",
    RankType.NEWBOOK: "新书榜",
    RankType.NOVEL: "小说榜",
    RankType.ALL: "总榜",
}


def get_weread_id(book_id: str) -> str:
    """将 bookId 转换为 WeRead ID"""
    hash_obj = hashlib.md5()
    hash_obj.update(book_id.encode())
    str_hash: str = hash_obj.hexdigest()
    str_sub: str = str_hash[0:3]
    if book_id.isdigit():
        chunks: list[str] = [hex(int(book_id[i : i + 9]))[2:] for i in range(0, len(book_id), 9)]
        fa: list = ["3", chunks]
    else:
        hex_str: str = "".join(hex(ord(char))[2:] for char in book_id)
        fa: list = ["4", [hex_str]]
    str_sub += fa[0] + "2" + str_hash[-2:]
    for i, sub in enumerate(fa[1]):
        str_sub += hex(len(sub))[2:].zfill(2) + sub
        if i < len(fa[1]) - 1:
            str_sub += "g"
    if len(str_sub) < 20:
        str_sub += str_hash[0 : 20 - len(str_sub)]
    final_hash = hashlib.md5()
    final_hash.update(str_sub.encode())
    str_sub += final_hash.hexdigest()[0:3]
    return str_sub


async def fetch(rank_type: str = "rising") -> list[HotItem]:
    """获取微信读书排行榜"""
    url: str = f"https://weread.qq.com/web/bookListInCategory/{rank_type}?rank=1"
    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67"
    }
    data: dict[str, Any] = await http_get(url, headers=headers)
    books: list[dict[str, Any]] = data.get("books", [])
    items: list[HotItem] = []
    for book_item in books:
        book_info: dict[str, Any] = book_item.get("bookInfo", {})
        book_id: str = book_info.get("bookId", "")
        weread_id: str = get_weread_id(book_id)
        hot_item: HotItem = HotItem(
            id=book_id,
            title=book_info.get("title"),
            desc=book_info.get("intro"),
            cover=book_info.get("cover", "").replace("s_", "t9_"),
            author=book_info.get("author"),
            hot=book_item.get("readingCount"),
            time=get_time(book_info.get("publishTime")),
            url=f"https://weread.qq.com/web/bookDetail/{weread_id}",
            mobile_url=f"https://weread.qq.com/web/bookDetail/{weread_id}",
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
            if item.author:
                lines.append(f"- **作者**: {item.author}")
            if item.desc:
                desc_preview: str = item.desc[:100] + "..." if len(item.desc) > 100 else item.desc
                lines.append(f"- **简介**: {desc_preview}")
            if item.hot:
                lines.append(f"- **阅读数**: {item.hot}")
            if item.time:
                lines.append(f"- **出版时间**: {item.time}")
            lines.append(f"- **链接**: {item.url}\n")
        return "\n".join(lines)


def main(
    type: RankType = typer.Option(
        RankType.RISING,
        help="排行榜类型：" + ", ".join([f"{k}={v}" for k, v in RANK_NAMES.items()]),
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """微信读书排行榜"""
    items: list[HotItem] = asyncio.run(fetch(type))
    rank_name = RANK_NAMES[type]
    print(format_output(items, rank_name, format))
    logger.info(f"获取 [{PLATFORM_NAME} - {rank_name}] 成功，共 {len(items)} 条")
