import importlib

import pytest

from hotboard.cli import PLATFORMS


@pytest.mark.parametrize("platform", PLATFORMS.keys())
def test_platform_import(platform: str):
    """测试所有平台模块可以正常导入"""
    module = importlib.import_module(f"hotboard.platforms.{platform}")
    assert hasattr(module, "main")
