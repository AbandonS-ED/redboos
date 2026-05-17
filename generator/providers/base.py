"""AI Provider 抽象基类"""
import logging
import time
from abc import ABC, abstractmethod
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class BaseAPIClient(ABC):
    """文本生成 API 抽象基类"""

    def __init__(self, config: dict):
        self.max_retries = 3
        self.timeout = 120
        self._init_config(config)

    def _init_config(self, config: dict) -> None:
        """子类实现：初始化 provider 配置"""
        raise NotImplementedError

    @abstractmethod
    def _build_headers(self) -> dict:
        """子类实现：返回 HTTP headers"""

    @abstractmethod
    def _build_payload(self, system_prompt: str, user_prompt: str) -> dict:
        """子类实现：构建请求 payload"""

    @abstractmethod
    def _parse_response(self, result: dict) -> Optional[str]:
        """子类实现：解析 provider 特定的响应格式"""

    def _call_api(self, payload: dict) -> Optional[dict]:
        """统一的 API 调用逻辑（重试、超时、错误处理）"""
        for attempt in range(self.max_retries):
            if attempt > 0:
                time.sleep(2)

            try:
                response = requests.post(
                    self.api_url,
                    headers=self._build_headers(),
                    json=payload,
                    timeout=self.timeout
                )

                if response.status_code != 200:
                    logger.warning(
                        "%s API 返回非200状态: %d，重试中...",
                        self.provider_name, response.status_code
                    )
                    continue

                return response.json()

            except requests.exceptions.Timeout:
                logger.warning("请求超时 (attempt %d/%d)", attempt + 1, self.max_retries)
                continue
            except requests.exceptions.RequestException as e:
                logger.warning("请求失败 (attempt %d/%d): %s", attempt + 1, self.max_retries, e)
                continue
            except Exception as e:
                logger.error("API 调用意外错误: %s", e)
                continue

        return None

    def generate(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """文本生成入口 — 模板方法"""
        payload = self._build_payload(system_prompt, user_prompt)
        result = self._call_api(payload)
        if result:
            return self._parse_response(result)
        return None

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """返回 provider 名称"""


class BaseImageAPIClient(ABC):
    """图片生成 API 抽象基类"""

    @abstractmethod
    def generate_image(self, prompt: str, **kwargs) -> Optional[bytes]:
        """调用 API 生成图片

        Args:
            prompt: 图片描述提示词
            **kwargs: 额外参数（如 aspect_ratio 等）

        Returns:
            图片二进制数据，失败返回 None
        """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """返回 provider 名称"""