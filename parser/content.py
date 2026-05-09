"""内容解析模块"""
import re
from typing import Dict, List

def parse_content(content: str) -> Dict:
    """解析 AI 生成的文本，提取配图提示词

    处理 AI 输出的各种 markdown 格式：
    - ## 步骤一（xxx）：
    - **步骤一（xxx）：**
    - 步骤一（xxx）：
    - 【配图提示词】

    Returns:
        dict with image_prompts list
    """
    result = {"image_prompts": []}

    if not content:
        return result

    lines = content.split("\n")
    current_prompt_lines = []
    step_pattern = re.compile(r'^步骤[一二三四五六七八九十]+（([^）]+)）：')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        step_match = step_pattern.match(line.lstrip('*').strip())

        if step_match:
            if current_prompt_lines:
                result["image_prompts"].append("\n".join(current_prompt_lines).strip())
                current_prompt_lines = []
            current_prompt_lines.append(line)
        elif line.startswith("【配图提示词】"):
            if current_prompt_lines:
                result["image_prompts"].append("\n".join(current_prompt_lines).strip())
                current_prompt_lines = []
        elif line.startswith("## 步骤"):
            if current_prompt_lines:
                result["image_prompts"].append("\n".join(current_prompt_lines).strip())
                current_prompt_lines = []
            current_prompt_lines.append(line)
        elif line.startswith("**步骤") and line.endswith("**"):
            if current_prompt_lines:
                result["image_prompts"].append("\n".join(current_prompt_lines).strip())
                current_prompt_lines = []
            current_prompt_lines.append(line.lstrip('*').strip())
        elif line.startswith("### 图片"):
            continue
        elif line.startswith("# 小红书配图提示词") or line.startswith("# Claude Code 小红书"):
            continue
        else:
            current_prompt_lines.append(line)

    if current_prompt_lines:
        result["image_prompts"].append("\n".join(current_prompt_lines).strip())

    return result