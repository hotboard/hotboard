"""日志模块"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def _is_debug() -> bool:
    """检查是否启用 debug 模式"""
    return os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")


def setup_logger(name: str = "hotboard", log_file: str | None = None) -> logging.Logger:
    """配置日志器"""
    logger: logging.Logger = logging.getLogger(name)

    # 根据 DEBUG 环境变量设置日志级别
    level = logging.DEBUG if _is_debug() else logging.INFO
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 控制台输出
    console_handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter: logging.Formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 文件输出（可选）
    if log_file:
        log_path: Path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler: RotatingFileHandler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter: logging.Formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


# 默认日志器
logger: logging.Logger = setup_logger()
