"""Markdown 格式化输出"""
from pathlib import Path
from typing import List, Dict

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
                    f.write(f"{prompt.strip()}\n\n")
            if i < len(notes):
                f.write("---\n\n")

    print(f"[OK] 已保存 Markdown 文件: {output_path}")