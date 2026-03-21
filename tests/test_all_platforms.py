"""测试所有 hotboard 平台"""

import importlib
from pathlib import Path

import pytest


def get_all_platforms() -> list[str]:
    """获取所有平台模块名"""
    packages_dir = Path(__file__).parent.parent / "packages" / "hotboard"

    if not packages_dir.exists():
        return []

    return [
        d.name
        for d in packages_dir.iterdir()
        if d.is_dir() and not d.name.startswith("_") and d.name != "core"
    ]


@pytest.mark.parametrize("module_name", get_all_platforms())
def test_platform_fetch(module_name: str):
    """测试平台的 fetch 函数

    Args:
        module_name: 模块名
    """
    module = importlib.import_module(f"hotboard.{module_name}.main")
    fetch = getattr(module, "fetch")

    import asyncio

    data = asyncio.run(fetch())

    assert isinstance(data, list)
    assert len(data) > 0

    for item in data:
        assert hasattr(item, "title")
        assert hasattr(item, "url")
