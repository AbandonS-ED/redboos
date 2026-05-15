"""OpenAI 文本生成 API 实现"""
import logging
from typing import Optional

from .base import BaseAPIClient

logger = logging.getLogger(__name__)


class OpenAIAPIClient(BaseAPIClient):
    """OpenAI API 文本生成客户端"""

    def __init__(self, config: dict):
        provider_config = config.get("openai", config)
        self.api_key = provider_config["api_key"]
        self.api_url = provider_config["api_url"]
        self.model = provider_config["model"]
        self.temperature = provider_config.get("temperature", 0.8)
        self.max_tokens = provider_config.get("max_tokens", 4096)
        self.timeout = provider_config.get("timeout", 120)
        super().__init__(config)

    @property
    def provider_name(self) -> str:
        return "openai"

    def _build_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _build_payload(self, system_prompt: str, user_prompt: str) -> dict:
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

    def _parse_response(self, result: dict) -> Optional[str]:
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        return None