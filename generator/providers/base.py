"""AI Provider 抽象基类"""
from abc import ABC, abstractmethod
from typing import Optional


class BaseAPIClient(ABC):
    """文本生成 API 抽象基类"""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """调用 API 生成文本

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词

        Returns:
            API 返回的文本内容，失败返回 None
        """

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