"""模板基类"""
from abc import ABC, abstractmethod


class BaseTemplate(ABC):
    """模板抽象基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """模板标识符，如 'ai_tech'"""

    @property
    def content_types(self) -> list:
        """支持的账号内容类型"""
        return ["AI资讯", "AI工具推荐", "开源项目解读"]

    @abstractmethod
    def build_prompt(self, content_type, topic, note_index=1, material=None):
        """构建配图提示词请求，返回 {"system": ..., "user": ...}"""

    @abstractmethod
    def build_body_prompt(self, topic, content_type, image_prompts, material=None):
        """构建正文请求，返回 {"system": ..., "user": ...}"""