"""Markdown 格式化输出"""
import re
from pathlib import Path
from typing import List, Dict

IMAGEPROMPT_NOTICE = "【重要声明】：每张图片提示词中的所有设计参数（包括但不限于十六进制颜色代码、字体大小、像素值、透明度、圆角等）仅供设计参考用途，严禁在生成的图片中渲染显示。图片尺寸：1080×1440像素（3:4比例），必须严格遵守。"

# 过滤 AI 生成时自带的多余标记行
IMAGE_PROMPT_CLEAN_LINES = (
    "## 步骤",  # 过滤 ## 步骤一 这类标题
    "**【配图提示词】**",  # 过滤 **【配图提示词】**
)

def fix_format(text: str) -> str:
    """修复格式：把裸的 pt/px 值包装成 (参考大小：NNpt) 格式
    只处理完全裸的值，不处理已有 (参考xxx：NN) 格式的值
    """
    # 先把已有的 (参考xxx：NNpt) 形式的值标记出来，避免重复匹配
    # 匹配 (参考xxx：NNpt) 或 (参考xxx：NNpx) 并替换成占位符
    protected = {}
    counter = [0]

    def protect(match):
        key = f"__PROTECTED_{counter[0]}__"
        protected[key] = match.group(0)
        counter[0] += 1
        return key

    # 保护已有格式
    text = re.sub(r'（参考[^）]+：\d+pt）', protect, text)
    text = re.sub(r'（参考[^）]+：\d+px）', protect, text)

    # 现在处理裸的 pt/px
    text = re.sub(r'(\d+)pt', r'(参考大小：\1pt)', text)
    text = re.sub(r'(\d+)px', r'(参考像素：\1px)', text)

    # 还原被保护的值
    for key, val in protected.items():
        text = text.replace(key, val)

    return text

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

    print(f"[OK] 已保存 Markdown 文件: {output_path}")