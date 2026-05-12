"""JSON 格式化输出"""
import json
import re
from pathlib import Path
from typing import List, Dict

def fix_format(text: str) -> str:
    """修复格式：把裸的 pt/px 值包装成 (参考大小：NNpt) 格式
    只处理完全裸的值，不处理已有 (参考xxx：NN) 格式的值
    """
    # 先把已有的 (参考xxx：NNpt) 形式的值标记出来，避免重复匹配
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