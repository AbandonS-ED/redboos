"""Markdown 格式化输出"""
from pathlib import Path
from typing import List, Dict

def save_markdown(notes: List[Dict], output_path: str) -> None:
    """保存为 Markdown 格式 - 只保存配图提示词

    Args:
        notes: 笔记列表
        output_path: 输出文件路径
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write("# 小红书配图提示词\n\n")
        for i, note in enumerate(notes, 1):
            image_prompts = note.get('image_prompts', [])
            if image_prompts:
                for j, prompt in enumerate(image_prompts, 1):
                    f.write(f"### 图片{j}\n\n")
                    f.write(f"{prompt.strip()}\n\n")
            if i < len(notes):
                f.write("---\n\n")

    print(f"[OK] 已保存 Markdown 文件: {output_path}")