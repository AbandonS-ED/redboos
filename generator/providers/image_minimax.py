"""MiniMax 图片生成 API 实现"""
import base64
import logging
import time
import requests
from typing import Optional

from .base import BaseImageAPIClient

logger = logging.getLogger(__name__)


class MiniMaxImageAPIError(Exception):
    """图像 API 调用错误"""
    pass


class MiniMaxImageAPIClient(BaseImageAPIClient):
    """MiniMax API 图片生成客户端"""

    def __init__(self, config: dict):
        provider_config = config.get("minimax", config)
        img_config = config.get("image_api", provider_config)
        self.api_key = img_config.get("api_key", provider_config.get("api_key"))
        self.api_url = img_config.get("api_url", "https://api.minimaxi.com/v1/image_generation")
        self.model = img_config.get("model", "image-01")
        self.aspect_ratio = img_config.get("aspect_ratio", "3:4")

    @property
    def provider_name(self) -> str:
        return "minimax"

    def generate_image(self, prompt: str, aspect_ratio: str = "3:4",
                      timeout: int = 300, max_retries: int = 3) -> Optional[bytes]:
        """调用 MiniMax API 生成单张图片"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio or self.aspect_ratio,
            "response_format": "base64",
        }

        for attempt in range(max_retries):
            if attempt > 0:
                time.sleep(2)

            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=timeout
                )

                if response.status_code != 200:
                    logger.warning(f"生图 API 返回非200状态: {response.status_code}, 重试中...")
                    continue

                result = response.json()
                logger.debug(f"生图 API 原始响应: {result}")

                if "data" in result and result["data"] is not None:
                    data = result["data"]
                    if isinstance(data, dict) and "image_base64" in data:
                        images = data["image_base64"]
                        if images and len(images) > 0:
                            return base64.b64decode(images[0])
                    elif isinstance(data, str):
                        return base64.b64decode(data)

                logger.warning(f"生图 API 返回格式异常: {result}")
                continue

            except requests.exceptions.Timeout:
                logger.warning("生图请求超时 (attempt %d/%d)", attempt + 1, max_retries)
                continue
            except requests.exceptions.RequestException as e:
                logger.warning("生图请求失败 (attempt %d/%d): %s", attempt + 1, max_retries, e)
                continue
            except Exception as e:
                logger.error("生图意外错误: %s", e)
                continue

        return None