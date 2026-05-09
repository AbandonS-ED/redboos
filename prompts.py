"""Prompt templates for Xiaohongshu AI Tech content generation - Compatibility layer.

This module re-exports from templates.prompts for backward compatibility.
New code should use templates.prompts directly.
"""

# Re-export everything from templates.prompts
from templates.prompts import (
    SYSTEM_PROMPT,
    USER_PROMPTS,
    CONTENT_TYPES,
    build_prompt,
    STEP_SUBTITLES,
    STEP_CONTENT,
    COMMON_STEPS,
    STEP3_CONTENT,
    STYLE_BLOCK,
)

# Keep this module's __all__ for backward compatibility
__all__ = [
    "SYSTEM_PROMPT",
    "USER_PROMPTS",
    "CONTENT_TYPES",
    "build_prompt",
    "STEP_SUBTITLES",
    "STEP_CONTENT",
    "COMMON_STEPS",
    "STEP3_CONTENT",
    "STYLE_BLOCK",
]