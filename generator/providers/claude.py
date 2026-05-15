"""Anthropic Claude 文本生成 API 实现"""
import logging
from typing import Optional

from .base import BaseAPIClient

logger = logging.getLogger(__name__)


class ClaudeAPIClient(BaseAPIClient):
    """Anthropic Claude API 文本生成客户端

    Claude 使用 /v1/messages 接口，响应格式为 content[0].text
    """

    def __init__(self, config: dict):
        provider_config = config.get("claude", config)
        self.api_key = provider_config["api_key"]
        self.api_url = provider_config["api_url"]
        self.model = provider_config["model"]
        self.temperature = provider_config.get("temperature", 0.8)
        self.max_tokens = provider_config.get("max_tokens", 4096)
        self.timeout = provider_config.get("timeout", 120)
        super().__init__(config)

    @property
    def provider_name(self) -> str:
        return "claude"

    def _build_headers(self) -> dict:
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

    def _build_payload(self, system_prompt: str, user_prompt: str) -> dict:
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
            "system": system_prompt
        }

    def _parse_response(self, result: dict) -> Optional[str]:
        if "content" in result and len(result["content"]) > 0:
            for block in result["content"]:
                if block.get("type") == "text":
                    return block["text"]
        return None