"""JSON 格式化输出"""
import json
from pathlib import Path
from typing import List, Dict

from .utils import fix_format


def save_json(notes: List[Dict], output_path: str) -> None:
    """保存为 JSON 格式

    Args:
        notes: 笔记列表
        output_path: 输出文件路径
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Add notice to each image_prompt
    for note in notes:
        if "image_prompts" in note:
            notice = "【重要声明】：每张图片提示词中的所有设计参数（包括但不限于十六进制颜色代码、字体大小、像素值、透明度、圆角等）仅供设计参考用途，严禁在生成的图片中渲染显示。图片尺寸：1080×1440像素（3:4比例），必须严格遵守。"
            note["image_prompts"] = [fix_format(f"{notice}\n{p}") for p in note["image_prompts"]]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

    print(f"[OK] 已保存 JSON 文件: {output_path}")