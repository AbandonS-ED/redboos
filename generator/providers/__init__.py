"""AI Provider 抽象层"""
from .base import BaseAPIClient, BaseImageAPIClient
from .minimax import MiniMaxAPIClient
from .openai import OpenAIAPIClient
from .claude import ClaudeAPIClient

PROVIDERS = {
    "minimax": MiniMaxAPIClient,
    "openai": OpenAIAPIClient,
    "claude": ClaudeAPIClient,
}


def get_text_client(provider: str, config: dict):
    """根据 provider 获取文本生成客户端"""
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(PROVIDERS.keys())}")
    return PROVIDERS[provider](config)


def get_image_client(provider: str, config: dict):
    """根据 provider 获取图片生成客户端"""
    from .image_minimax import MiniMaxImageAPIClient

    # 目前只有 MiniMax 支持生图
    if provider == "minimax":
        return MiniMaxImageAPIClient(config)
    return None


__all__ = [
    "BaseAPIClient",
    "BaseImageAPIClient",
    "MiniMaxAPIClient",
    "OpenAIAPIClient",
    "ClaudeAPIClient",
    "get_text_client",
    "get_image_client",
]