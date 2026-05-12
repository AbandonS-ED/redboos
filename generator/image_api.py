"""MiniMax 图像生成 API 调用模块"""
import base64
import logging
import time
import requests
from typing import Optional

logger = logging.getLogger(__name__)


class MiniMaxImageAPIError(Exception):
    """图像 API 调用错误"""
    pass


class MiniMaxImageAPI:
    def __init__(self, api_key: str, api_url: str, model: str = "image-01"):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model

    def generate_image(self, prompt: str, aspect_ratio: str = "3:4",
                      timeout: int = 300, max_retries: int = 3) -> Optional[bytes]:
        """调用 API 生成单张图片

        Args:
            prompt: 图片描述提示词
            aspect_ratio: 图片宽高比，默认 3:4（匹配小红书配图）
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数

        Returns:
            图片二进制数据，失败返回 None
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
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

                # MiniMax 生图 API 返回格式：data.image_base64 数组
                if "data" in result and result["data"] is not None:
                    data = result["data"]
                    if isinstance(data, dict) and "image_base64" in data:
                        images = data["image_base64"]
                        if images and len(images) > 0:
                            return base64.b64decode(images[0])
                    elif isinstance(data, str):
                        # 直接是 base64 字符串
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
