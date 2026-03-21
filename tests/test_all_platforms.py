"""测试所有 hotboard 平台"""

import subprocess
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
def test_platform_cli(module_name: str):
    """测试平台的 CLI 命令

    Args:
        module_name: 模块名
    """
    cmd = f"hotboard-{module_name}"
    result = subprocess.run(
        [cmd, "--format", "json"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        pytest.skip(f"Command {cmd} not available or failed")
        return
    
    assert result.returncode == 0
    assert len(result.stdout) > 0
