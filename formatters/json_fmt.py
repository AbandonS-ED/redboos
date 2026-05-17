"""JSON 格式化输出"""
import json
import logging
from pathlib import Path
from typing import List, Dict

from generator.constants import IMAGEPROMPT_NOTICE
from .utils import fix_format

logger = logging.getLogger(__name__)


def save_json(notes: List[Dict], output_path: str) -> None:
    """保存为 JSON 格式

    Args:
        notes: 笔记列表
        output_path: 输出文件路径
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # 深拷贝避免修改原始 notes
    import copy
    notes_copy = copy.deepcopy(notes)
    for note in notes_copy:
        if "image_prompts" in note:
            note["image_prompts"] = [fix_format(f"{IMAGEPROMPT_NOTICE}\n{p}") for p in note["image_prompts"]]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(notes_copy, f, ensure_ascii=False, indent=2)

    logger.info(f"已保存 JSON 文件: {output_path}")