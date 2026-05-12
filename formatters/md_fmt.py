"""Markdown 格式化输出"""
import logging
import re
from pathlib import Path
from typing import List, Dict

from .utils import fix_format

logger = logging.getLogger(__name__)

IMAGEPROMPT_NOTICE = "【重要声明】：每张图片提示词中的所有设计参数（包括但不限于十六进制颜色代码、字体大小、像素值、透明度、圆角等）仅供设计参考用途，严禁在生成的图片中渲染显示。图片尺寸：1080×1440像素（3:4比例），必须严格遵守。"

IMAGE_PROMPT_CLEAN_LINES = (
    "## 步骤",
    "**【配图提示词】**",
)

def save_markdown(notes: List[Dict], output_path: str) -> None:
    """保存为 Markdown 格式 - 包含配图提示词和文案

    Args:
        notes: 笔记列表
        output_path: 输出文件路径
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        for i, note in enumerate(notes, 1):
            # 写入文案（如果存在）
            body = note.get('body')
            if body:
                f.write(f"# {body.get('title', note.get('topic', ''))}\n\n")
                if body.get('intro'):
                    f.write(f"## 开头\n\n{body['intro']}\n\n")
                if body.get('sections'):
                    f.write("## 正文\n\n")
                    for section in body['sections']:
                        f.write(f"### {section['title']}\n\n{section['content']}\n\n")
                if body.get('closing'):
                    f.write(f"## 结尾\n\n{body['closing']}\n\n")
                if body.get('tags'):
                    f.write(f"**标签**: {' '.join(body['tags'])}\n\n")
                f.write("---\n\n")

            # 写入配图提示词
            image_prompts = note.get('image_prompts', [])
            if image_prompts:
                f.write("# 配图提示词\n\n")
                for j, prompt in enumerate(image_prompts, 1):
                    f.write(f"### 图片{j}\n\n")
                    f.write(f"{IMAGEPROMPT_NOTICE}\n\n")
                    # 过滤多余标记行并修复格式后写入
                    fixed_lines = []
                    for line in prompt.strip().split('\n'):
                        if line.strip() and not any(marker in line for marker in IMAGE_PROMPT_CLEAN_LINES):
                            fixed_lines.append(fix_format(line))
                    f.write('\n'.join(fixed_lines) + "\n\n")
            if i < len(notes):
                f.write("---\n\n")

    logger.info(f"已保存 Markdown 文件: {output_path}")