import importlib
import sys
from importlib.metadata import version
from pathlib import Path

import typer


def _discover_platforms() -> dict[str, str]:
    """自动发现所有平台及其描述"""
    platforms = {}
    platforms_dir = Path(__file__).parent / "platforms"
    for file in platforms_dir.glob("*.py"):
        if file.stem.startswith("_"):
            continue
        module = importlib.import_module(f"hotboard.platforms.{file.stem}")
        desc = getattr(module, "PLATFORM_NAME", file.stem)
        if hasattr(module, "main") and module.main.__doc__:
            desc = module.main.__doc__.strip()
        platforms[file.stem] = desc
    return platforms


PLATFORMS = _discover_platforms()


def cli():
    """多平台热榜数据获取 CLI 工具"""
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "list":
            typer.secho("支持的平台：", fg=typer.colors.BRIGHT_WHITE, bold=True)
            for name, desc in PLATFORMS.items():
                typer.secho(f"  {name:15}", fg=typer.colors.GREEN, nl=False)
                typer.secho(f" - {desc}", fg=typer.colors.BRIGHT_BLACK)
            return
        if cmd in ("--version", "-v"):
            typer.echo(f"hotboard {version('hotboard')}")
            return
        if cmd in PLATFORMS:
            module = importlib.import_module(f"hotboard.platforms.{cmd}")
            sys.argv = [f"hotboard-{cmd}"] + sys.argv[2:]
            typer.run(module.main)
            return
        if cmd in ("--help", "-h"):
            typer.secho("Usage: ", fg=typer.colors.BRIGHT_WHITE, nl=False)
            typer.secho("hotboard <platform> [options]", fg=typer.colors.CYAN)
            typer.secho("       hotboard list", fg=typer.colors.CYAN)
            typer.secho("       hotboard --help", fg=typer.colors.CYAN)
            typer.echo("")
            typer.secho("多平台热榜数据获取 CLI 工具", fg=typer.colors.BRIGHT_WHITE)
            typer.echo("")
            typer.secho("Commands:", fg=typer.colors.BRIGHT_WHITE)
            typer.secho("  list              ", fg=typer.colors.GREEN, nl=False)
            typer.echo("列出所有支持的平台")
            typer.secho("  <platform>        ", fg=typer.colors.GREEN, nl=False)
            typer.echo("获取指定平台的热榜数据")
            return
    typer.secho("Usage: ", fg=typer.colors.BRIGHT_WHITE, nl=False)
    typer.secho("hotboard <platform> [options]", fg=typer.colors.CYAN)
    typer.secho("       hotboard list", fg=typer.colors.CYAN)
    typer.secho("       hotboard --help", fg=typer.colors.CYAN)
