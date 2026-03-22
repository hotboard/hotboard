import asyncio
from enum import StrEnum

import typer
from bs4 import BeautifulSoup

from hotboard.logger import logger
from hotboard.types import HotItem, OutputFormat
from hotboard.utils import format_items_json, http_get_text

PLATFORM_NAME = "GitHub"


class TrendType(StrEnum):
    """趋势类型"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


TREND_CONFIGS: dict[str, str] = {
    TrendType.DAILY: "日榜",
    TrendType.WEEKLY: "周榜",
    TrendType.MONTHLY: "月榜",
}


async def fetch(trend_type: str = "daily") -> list[HotItem]:
    """获取 GitHub Trending"""
    url: str = f"https://github.com/trending?since={trend_type}"

    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    html: str = await http_get_text(url, headers)

    soup = BeautifulSoup(html, "lxml")

    items: list[HotItem] = []
    for article in soup.find_all("article", class_="Box-row"):
        # 仓库标题和链接
        repo_h2 = article.find("h2")
        if not repo_h2:
            continue

        repo_anchor = repo_h2.find("a")
        if not repo_anchor:
            continue

        # 处理 "owner / repo" 格式
        full_name_text = (
            repo_anchor.get_text().strip().replace("\r\n", "").replace("\n", "").replace("  ", " ")
        )
        parts = [s.strip() for s in full_name_text.split("/")]
        owner = parts[0] if len(parts) > 0 else ""
        repo_name = parts[1] if len(parts) > 1 else ""

        href = repo_anchor.get("href")
        if not href or not isinstance(href, str):
            continue
        repo_url: str = f"https://github.com{href}"

        # 仓库描述
        desc_el = article.find("p", class_="col-9")
        description: str | None = desc_el.get_text(strip=True) if desc_el else None

        # 编程语言
        lang_el = article.find(attrs={"itemprop": "programmingLanguage"})
        language: str | None = lang_el.get_text(strip=True) if lang_el else None

        # Stars 和 Forks
        stars_anchor = article.find(
            "a", href=lambda x: isinstance(x, str) and x.endswith("/stargazers")
        )
        stars: str | None = stars_anchor.get_text(strip=True) if stars_anchor else None

        forks_anchor = article.find("a", href=lambda x: isinstance(x, str) and x.endswith("/forks"))
        forks: str | None = forks_anchor.get_text(strip=True) if forks_anchor else None

        # 构建标题
        title = f"{owner}/{repo_name}"
        if language:
            title = f"[{language}] {title}"

        # 构建描述
        desc_parts: list[str] = []
        if description:
            desc_parts.append(f"描述：{description}")
        if stars:
            desc_parts.append(f"Stars:{stars}")
        if forks:
            desc_parts.append(f"Forks:{forks}")

        hot_item: HotItem = HotItem(
            id=repo_url,
            title=title,
            desc="\n".join(desc_parts) if desc_parts else None,
            time=None,
            hot=stars,
            url=repo_url,
            mobile_url=repo_url,
            author=owner,
        )
        items.append(hot_item)

    return items


def format_output(items: list[HotItem], trend_type: str, format: OutputFormat) -> str:
    """格式化输出"""
    type_name = TREND_CONFIGS[trend_type]

    if format == OutputFormat.JSON:
        return format_items_json(PLATFORM_NAME, items, type_name)
    else:
        lines: list[str] = [
            f"# {PLATFORM_NAME} Trending - {type_name}\n",
            f"**总数**: {len(items)} 条\n",
        ]

        for item in items:
            lines.append(f"## {item.title}\n")
            if item.desc:
                lines.append(f"- **详情**:\n```\n{item.desc}\n```")
            lines.append(f"- **链接**: {item.url}\n")

        return "\n".join(lines)


def main(
    type: TrendType = typer.Option(
        TrendType.DAILY,
        help="榜单分类：" + ", ".join([f"{k}={v}" for k, v in TREND_CONFIGS.items()]),
    ),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, help="输出格式"),
):
    """GitHub Trending"""
    items: list[HotItem] = asyncio.run(fetch(type))
    print(format_output(items, type, format))
    logger.info(f"获取 [{PLATFORM_NAME} Trending - {type}] 成功，共 {len(items)} 条")
