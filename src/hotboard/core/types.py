from dataclasses import dataclass
from enum import StrEnum


class OutputFormat(StrEnum):
    """输出格式"""

    MARKDOWN = "markdown"
    JSON = "json"


@dataclass
class HotItem:
    """热榜条目"""

    id: int | str | None = None
    title: str | None = None
    desc: str | None = None
    author: str | None = None
    time: str | None = None
    hot: int | str | None = None
    cover: str | None = None
    url: str | None = None
    mobile_url: str | None = None
