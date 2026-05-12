"""MiniMax API 调用模块"""
import logging
import time
import requests
from typing import Optional

logger = logging.getLogger(__name__)

class MiniMaxAPIError(Exception):
    """API 调用错误"""
    pass

class MiniMaxAPI:
    def __init__(self, api_url: str, api_key: str, model: str,
                 temperature: float = 0.8, max_tokens: int = 4096):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, system_prompt: str, user_prompt: str, max_retries: int = 3) -> Optional[str]:
        """调用 API 生成内容

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            max_retries: 最大重试次数

        Returns:
            API 返回的文本内容，失败返回 None
        """
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
                    timeout=120
                )

                if response.status_code != 200:
                    logger.warning(f"API 返回非200状态: {response.status_code}, 重试中...")
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