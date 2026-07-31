from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = PROJECT_ROOT / "config"


class ConfigurationError(RuntimeError):
    pass


@lru_cache(maxsize=None)
def load_yaml(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    if not path.is_file():
        raise ConfigurationError(f"缺少配置文件: {path}")
    try:
        with path.open("r", encoding="utf-8") as stream:
            data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"配置文件格式错误: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigurationError(f"配置文件根节点必须是对象: {path}")
    return data
