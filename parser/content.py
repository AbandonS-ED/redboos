"""内容解析模块"""
import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)

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
    step_pattern = re.compile(r'^步骤[一二三四五六七八九十]+')
    step_pattern_with_subtitle = re.compile(r'^步骤[一二三四五六七八九十]+（([^）]+)）：')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Remove markdown headers
        clean_line = line.lstrip('#').strip()

        # 检查是否以 ### 开头（markdown header）
        if line.startswith("###"):
            # 跳过 ### 图片X
            if line.startswith("### 图片"):
                continue
            # 跳过包含"小红书配图提示词"的标题行
            if "小红书配图提示词" in line:
                continue
            # 其他 markdown 标题行（如 ### DeepSeek是谁）也跳过
            continue

        # 检查是否以 ## 开头（markdown section header）
        if line.startswith("## "):
            # 提取标题内容（去掉 ## 和可能的 ** 包装）
            title_content = line.lstrip('#').strip()
            title_clean = title_content.lstrip('*').replace('**', '').strip()
            # 如果是步骤标题格式，保存当前提示词并开始新的
            if step_pattern.match(title_clean) or step_pattern_with_subtitle.match(title_clean):
                if current_prompt_lines:
                    result["image_prompts"].append("\n".join(current_prompt_lines).strip())
                    current_prompt_lines = []
                # 添加步骤标题行
                current_prompt_lines.append(line)
                continue
            # 其他 ## 标题跳过
            continue

        step_match = step_pattern.match(clean_line.lstrip('*').replace('**', '').strip())
        step_with_subtitle_match = step_pattern_with_subtitle.match(clean_line.lstrip('*').replace('**', '').strip())

        if step_match or step_with_subtitle_match:
            # 如果是纯标题行（只有标题没有其他内容），跳过不加入
            # 但 ## 步骤标题已经在上面处理过了，这里只处理非 ## 开头的纯标题
            stripped = clean_line.lstrip('*').replace('**', '').strip()
            is_pure_title = (step_pattern.match(stripped) and len(stripped) <= 6) or \
                           (step_with_subtitle_match and len(stripped) <= 15)
            if is_pure_title:
                if current_prompt_lines:
                    result["image_prompts"].append("\n".join(current_prompt_lines).strip())
                    current_prompt_lines = []
                continue
            if current_prompt_lines:
                result["image_prompts"].append("\n".join(current_prompt_lines).strip())
                current_prompt_lines = []
            current_prompt_lines.append(line)
        elif "【配图提示词】" in clean_line:
            rest = clean_line[len("【配图提示词】"):].strip()
            # 去掉 ** 包装后再匹配步骤
            rest_clean = rest.lstrip('*').replace('**', '').strip()
            # 如果是步骤标题格式（步骤一、步骤二...）
            if step_pattern.match(rest_clean) or step_pattern_with_subtitle.match(rest_clean):
                if current_prompt_lines:
                    result["image_prompts"].append("\n".join(current_prompt_lines).strip())
                    current_prompt_lines = []
                current_prompt_lines.append(line)
            # 如果是单独的 **【配图提示词】** 或 【配图提示词】，不添加到 current_prompt_lines
            # 只是继续累积下一行内容（不加这行）
            elif clean_line == "**【配图提示词】**" or clean_line == "【配图提示词】":
                # 不保存这行，继续等待内容行
                continue
            # 如果是其他包含【配图提示词】的行（如 **【配图提示词】**背景设置），直接添加
            else:
                current_prompt_lines.append(line)
        elif line.startswith("# 小红书配图提示词") or line.startswith("# Claude Code 小红书"):
            continue
        elif re.match(r'^# .+配图提示词.*$', line):
            # 过滤 "# xxx配图提示词" 类型的标题行，如 "# Claude Code 配图提示词（8张）"
            continue
        elif clean_line.startswith("---"):
            # 跳过 markdown 分隔线，不保存
            continue
        else:
            current_prompt_lines.append(line)

    if current_prompt_lines:
        result["image_prompts"].append("\n".join(current_prompt_lines).strip())

    # 限制为 8 条（AI 可能返回多余内容）
    if len(result["image_prompts"]) > 8:
        result["image_prompts"] = result["image_prompts"][:8]

    if not result["image_prompts"]:
        logger.warning("parse_content returned 0 prompts, content length: %d", len(content))

    return result


def parse_body(content: str) -> Dict:
    """解析 AI 生成的小红书文案

    格式：
    标题：[标题]
    开头：[开头引入]
    正文：
    [分块1标题]
    [分块1内容]
    [分块2标题]
    [分块2内容]
    ...
    结尾：[结尾引导]
    标签：[话题标签，用空格分隔]

    Returns:
        dict with title, intro, sections, tags, closing
    """
    result = {
        "title": "",
        "intro": "",
        "sections": [],
        "tags": [],
        "closing": ""
    }

    if not content:
        return result

    current_section_title = ""
    current_section_content = []
    in_body_section = False

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue

        original_line = line  # 保留原始行用于判断
        clean_line = line.lstrip('#').strip()

        # 处理 markdown 标题（如 ### DeepSeek是谁）
        if original_line.startswith("###"):
            # 这些是 section 标题，跳过 ### 前缀后直接使用
            if in_body_section and clean_line:
                # 保存之前的 section（如果存在）
                if current_section_title and current_section_content:
                    result["sections"].append({
                        "title": current_section_title,
                        "content": " ".join(current_section_content)
                    })
                current_section_title = clean_line
                current_section_content = []
            continue

        if clean_line.startswith("标题："):
            result["title"] = clean_line[3:].strip()
        elif clean_line.startswith("开头："):
            result["intro"] = clean_line[3:].strip()
        elif clean_line.startswith("正文："):
            in_body_section = True
        elif clean_line.startswith("结尾："):
            in_body_section = False
            result["closing"] = clean_line[3:].strip()
        elif clean_line.startswith("标签："):
            result["tags"] = clean_line[3:].strip().split()
        elif in_body_section:
            # 判断规则：
            # - 短短语(<=15字)且不以标点结尾 → 可能是标题
            # - 超过15字 → 正文内容
            is_short_phrase = len(clean_line) <= 15 and not clean_line.endswith(("。", "，", ".", ","))

            if current_section_title:
                # 已识别到标题，等待内容行
                if is_short_phrase:
                    # 新标题出现，保存上一个
                    if current_section_content:
                        result["sections"].append({
                            "title": current_section_title,
                            "content": " ".join(current_section_content)
                        })
                    current_section_title = clean_line
                    current_section_content = []
                else:
                    # 内容行
                    current_section_content.append(clean_line)
            else:
                # 还没标题，遇到短短语就设为标题
                if is_short_phrase:
                    current_section_title = clean_line
                # 否则跳过（正文的第一行不应该直接就是长内容）

    # Save last section
    if current_section_title and current_section_content:
        result["sections"].append({
            "title": current_section_title,
            "content": " ".join(current_section_content)
        })

    if not result["title"]:
        logger.warning("parse_body returned empty title, content length: %d", len(content))

    return result