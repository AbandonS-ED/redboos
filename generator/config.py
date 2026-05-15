"""配置加载模块"""
import logging
import os
import re
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict[str, Any]:
    """加载 YAML 配置

    Args:
        config_path: 配置文件路径

    Returns:
        配置字典，包含 provider 和各 provider 配置

    Raises:
        FileNotFoundError: 配置文件不存在
        ValueError: 缺少必要配置项
    """
    path = Path(config_path)
    if not path.exists():
        logger.error("Config file not found: %s", config_path)
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 验证必要字段
    provider = config.get("provider", "minimax")
    provider_config = config.get(provider)

    if not provider_config:
        logger.error("Missing config for provider: %s", provider)
        raise ValueError(f"Missing config for provider: {provider}")

    required = ["api_key", "api_url", "model"]
    for key in required:
        if key not in provider_config:
            logger.error("Missing required config: %s.%s", provider, key)
            raise ValueError(f"Missing required config: {provider}.{key}")

    return config


def load_tavily_key(config_path: str = "config.yaml", cli_key: str = None) -> str:
    """加载 Tavily API Key

    优先级：cli_key > config.yaml > 环境变量 > ~/.openclaw/.env

    Args:
        config_path: 配置文件路径
        cli_key: 命令行传入的 key（最高优先级）

    Returns:
        Tavily API Key 或 None
    """
    if cli_key:
        return cli_key

    # 从 config.yaml 读取
    try:
        config = load_config(config_path)
        key = config.get("tavily", {}).get("api_key")
        if key:
            return key
    except Exception:
        pass

    # 从环境变量读取
    key = os.environ.get("TAVILY_API_KEY")
    if key:
        return key.strip()

    # 从 ~/.openclaw/.env 读取
    env_path = Path.home() / ".openclaw" / ".env"
    if env_path.exists():
        try:
            txt = env_path.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"^\s*TAVILY_API_KEY\s*=\s*(.+?)\s*$", txt, re.M)
            if m:
                return m.group(1).strip().strip('"').strip("'")
        except Exception:
            pass

    return None