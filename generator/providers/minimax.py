"""MiniMax 文本生成 API 实现"""
import logging
import time
import requests
from typing import Optional

from .base import BaseAPIClient

logger = logging.getLogger(__name__)


class MiniMaxAPIError(Exception):
    """API 调用错误"""
    pass


class MiniMaxAPIClient(BaseAPIClient):
    """MiniMax API 文本生成客户端"""

    def __init__(self, config: dict):
        provider_config = config.get("minimax", config)
        self.api_key = provider_config["api_key"]
        self.api_url = provider_config["api_url"]
        self.model = provider_config["model"]
        self.temperature = provider_config.get("temperature", 0.8)
        self.max_tokens = provider_config.get("max_tokens", 4096)
        self.timeout = provider_config.get("timeout", 120)

    @property
    def provider_name(self) -> str:
        return "minimax"

    def generate(self, system_prompt: str, user_prompt: str, max_retries: int = 3) -> Optional[str]:
        """调用 MiniMax API 生成内容"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        for attempt in range(max_retries):
            if attempt > 0:
                time.sleep(2)

            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )

                if response.status_code != 200:
                    logger.warning(f"MiniMax API 返回非200状态: {response.status_code}, 重试中...")
                    continue

                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]

            except requests.exceptions.Timeout:
                logger.warning("Request timeout (attempt %d/%d)", attempt + 1, max_retries)
                continue
            except requests.exceptions.RequestException as e:
                logger.warning("Request failed (attempt %d/%d): %s", attempt + 1, max_retries, e)
                continue
            except Exception as e:
                logger.error("Unexpected error during API call: %s", e)
                continue

        return None