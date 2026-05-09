"""JSON 格式化输出"""
import json
from pathlib import Path
from typing import List, Dict

def save_json(notes: List[Dict], output_path: str) -> None:
    """保存为 JSON 格式

    Args:
        notes: 笔记列表
        output_path: 输出文件路径
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

    print(f"[OK] 已保存 JSON 文件: {output_path}")