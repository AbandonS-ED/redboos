"""配置加载模块"""
import yaml
from pathlib import Path
from typing import Any

def load_config(config_path: str = "config.yaml") -> dict[str, Any]:
    """加载 YAML 配置

    Args:
        config_path: 配置文件路径

    Returns:
        配置字典，包含 api_key, api_url, model, temperature, max_tokens

    Raises:
        FileNotFoundError: 配置文件不存在
        ValueError: 缺少必要配置项
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 验证必要字段
    required = ["api_key", "api_url", "model"]
    for key in required:
        if key not in config:
            raise ValueError(f"Missing required config: {key}")

    return config