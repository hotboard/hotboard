"""工具函数"""

import hashlib
import json
import os
from dataclasses import asdict
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any

import aiohttp

from hotboard.core.logger import _is_debug, logger
from hotboard.core.types import HotItem


def get_proxy() -> str | None:
    """获取代理设置"""
    return (
        os.environ.get("HTTP_PROXY")
        or os.environ.get("HTTPS_PROXY")
        or os.environ.get("http_proxy")
        or os.environ.get("https_proxy")
    )


async def http_get(url: str, headers: dict[str, str] | None = None) -> Any:
    """发送 HTTP GET 请求，返回 JSON 数据"""
    if _is_debug():
        logger.debug(f"GET {url}")
        if headers:
            logger.debug(f"Headers: {headers}")

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, proxy=get_proxy()) as response:
            data = await response.json()
            if _is_debug():
                logger.debug(f"Status: {response.status}")
                logger.debug(f"Response: {str(data)}")
            return data


async def http_get_with_headers(
    url: str, headers: dict[str, str] | None = None
) -> tuple[dict[str, Any], dict[str, str]]:
    """发送 HTTP GET 请求，返回 JSON 数据和响应头"""
    if _is_debug():
        logger.debug(f"GET {url}")
        if headers:
            logger.debug(f"Headers: {headers}")

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, proxy=get_proxy()) as response:
            json_data: dict[str, Any] = await response.json()
            response_headers: dict[str, str] = dict(response.headers)
            if _is_debug():
                logger.debug(f"Status: {response.status}")
                logger.debug(f"Response: {str(json_data)}")
            return json_data, response_headers


async def http_get_text(
    url: str, headers: dict[str, str] | None = None, encoding: str = "utf-8"
) -> str:
    """发送 HTTP GET 请求，返回文本内容"""
    if _is_debug():
        logger.debug(f"GET {url}")
        if headers:
            logger.debug(f"Headers: {headers}")

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, proxy=get_proxy()) as response:
            content: bytes = await response.read()
            text = content.decode(encoding, errors="ignore")
            if _is_debug():
                logger.debug(f"Status: {response.status}")
                logger.debug(f"Response: {text}")
            return text


async def http_post(
    url: str, headers: dict[str, str] | None = None, body: str | None = None
) -> dict[str, Any]:
    """发送 HTTP POST 请求，返回 JSON 数据"""
    if _is_debug():
        logger.debug(f"POST {url}")
        if headers:
            logger.debug(f"Headers: {headers}")
        if body:
            logger.debug(f"Body: {body}")

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=body, proxy=get_proxy()) as response:
            data = await response.json()
            if _is_debug():
                logger.debug(f"Status: {response.status}")
                logger.debug(f"Response: {str(data)}")
            return data


async def http_post_text(
    url: str,
    headers: dict[str, str] | None = None,
    body: str | None = None,
    encoding: str = "utf-8",
) -> str:
    """发送 HTTP POST 请求，返回文本内容"""
    if _is_debug():
        logger.debug(f"POST {url}")
        if headers:
            logger.debug(f"Headers: {headers}")
        if body:
            logger.debug(f"Body: {body}")

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=body, proxy=get_proxy()) as response:
            content: bytes = await response.read()
            text = content.decode(encoding, errors="ignore")
            if _is_debug():
                logger.debug(f"Status: {response.status}")
                logger.debug(f"Response: {text}")
            return text


def md5_hash(text: str) -> str:
    """计算 MD5 哈希"""
    return hashlib.md5(text.encode()).hexdigest()


def get_time(time_input: str | int | None) -> str | None:
    """将时间转换为可读格式"""
    if not time_input:
        return None

    if isinstance(time_input, int):
        # 判断是秒级还是毫秒级时间戳（以 2000-01-01 为分界）
        ts = time_input if time_input > 946684800000 else time_input * 1000
        return datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M")

    # 字符串处理
    if isinstance(time_input, str):
        # 纯数字时间戳
        if time_input.isdigit():
            num: int = int(time_input)
            ts = num if num > 946684800000 else num * 1000
            return datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M")

        # ISO 8601 格式（如 2026-02-28T08:10:09）
        if (
            "T" in time_input
            and "-" in time_input
            and time_input.index("T") > time_input.index("-")
        ):
            dt = datetime.fromisoformat(time_input.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M")

        # 常见日期格式
        if "-" in time_input:
            parts = time_input.split("-")
            # 2026-03-15-12
            if len(parts) == 4:
                return f"{parts[0]}-{parts[1]}-{parts[2]} {parts[3]}:00"
            # 2026-03-15
            elif len(parts) == 3 and len(parts[0]) == 4:
                return time_input
            # 03-13 (月 - 日，补充当前年份)
            elif len(parts) == 2:
                current_year = datetime.now().year
                return f"{current_year}-{parts[0]}-{parts[1]}"

        # RFC 2822 格式（如 feedparser 的 published 字段）
        dt = parsedate_to_datetime(time_input)
        return dt.strftime("%Y-%m-%d %H:%M") if dt else None


def format_items_json(platform: str, items: list[HotItem], type_name: str) -> str:
    """将 HotItem 列表格式化为 JSON"""
    output: dict[str, Any] = {
        "platform": platform,
        "type": type_name,
        "total": len(items),
        "items": [asdict(item) for item in items],
    }
    return json.dumps(output, ensure_ascii=False, indent=2)
