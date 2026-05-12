"""配置加载模块"""
import logging
import yaml
from pathlib import Path
from typing import Any

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