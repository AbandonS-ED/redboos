"""内容解析模块"""
import logging
import re
from enum import Enum, auto
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


# 正则表达式（编译一次）
STEP_PATTERN = re.compile(r'^步骤[一二三四五六七八九十]+')
STEP_PATTERN_WITH_SUBTITLE = re.compile(r'^步骤[一二三四五六七八九十]+（([^）]+)）：')
IMAGE_PROMPT_MARKER = "【配图提示词】"


def _strip_markup(line: str) -> str:
    """去掉 # * 等标记，返回干净的内容"""
    return line.lstrip('#').strip().lstrip('*').replace('**', '').strip()


def _is_step_title(line: str) -> Tuple[bool, bool]:
    """判断是否是步骤标题

    Returns:
        (is_step, has_subtitle)
    """
    stripped = _strip_markup(line)
    has_subtitle = bool(STEP_PATTERN_WITH_SUBTITLE.match(stripped))
    is_step = bool(STEP_PATTERN.match(stripped))
    return is_step, has_subtitle


def _is_pure_title(stripped: str) -> bool:
    """判断是否是纯标题行（只有标题，没有内容）"""
    if STEP_PATTERN_WITH_SUBTITLE.match(stripped):
        return len(stripped) <= 15
    if STEP_PATTERN.match(stripped):
        return len(stripped) <= 4
    return False


class ParseState(Enum):
    """解析状态"""
    SKIP = auto()
    COLLECT = auto()


def _transition(state: ParseState, line: str, current: List[str], result: Dict) -> ParseState:
    """状态转移函数"""
    stripped = line.strip()
    if not stripped:
        return ParseState.SKIP

    # --- 跳过规则 ---
    if line.startswith("###"):
        return ParseState.SKIP
    if stripped.startswith("---"):
        return ParseState.SKIP
    if stripped.startswith("# 小红书配图提示词") or stripped.startswith("# Claude Code 小红书"):
        return ParseState.SKIP
    if re.match(r'^# .+配图提示词.*$', stripped):
        return ParseState.SKIP

    # --- ## 开头处理 ---
    if line.startswith("## "):
        title_clean = _strip_markup(line)
        is_step, _ = _is_step_title(title_clean)
        if is_step:
            if current:
                result["image_prompts"].append("\n".join(current).strip())
                current.clear()
            current.append(line)
        return ParseState.SKIP

    # --- 处理行内容 ---
    clean_line = _strip_markup(line)
    is_step, _ = _is_step_title(clean_line)

    if is_step:
        if _is_pure_title(clean_line):
            if current:
                result["image_prompts"].append("\n".join(current).strip())
                current.clear()
            return ParseState.SKIP
        else:
            if current:
                result["image_prompts"].append("\n".join(current).strip())
                current.clear()
            current.append(line)
            return ParseState.COLLECT

    # --- 【配图提示词】处理 ---
    if IMAGE_PROMPT_MARKER in stripped:
        rest = stripped[len(IMAGE_PROMPT_MARKER):].strip()
        rest_clean = _strip_markup(rest)
        rest_is_step, _ = _is_step_title(rest_clean)
        if rest_is_step:
            if current:
                result["image_prompts"].append("\n".join(current).strip())
                current.clear()
            current.append(line)
            return ParseState.COLLECT
        if stripped == "**【配图提示词】**" or stripped == "【配图提示词】":
            return ParseState.SKIP
        current.append(line)
        return ParseState.COLLECT

    # --- 其他内容行 ---
    current.append(line)
    return ParseState.COLLECT


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

    state = ParseState.SKIP
    current: List[str] = []

    for line in content.split("\n"):
        state = _transition(state, line, current, result)

    if current:
        result["image_prompts"].append("\n".join(current).strip())

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

        original_line = line
        clean_line = line.lstrip('#').strip()

        if original_line.startswith("###"):
            if in_body_section and clean_line:
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
            is_short_phrase = len(clean_line) <= 15 and not clean_line.endswith(("。", "，", ".", ","))

            if current_section_title:
                if is_short_phrase:
                    if current_section_content:
                        result["sections"].append({
                            "title": current_section_title,
                            "content": " ".join(current_section_content)
                        })
                    current_section_title = clean_line
                    current_section_content = []
                else:
                    current_section_content.append(clean_line)
            else:
                if is_short_phrase:
                    current_section_title = clean_line

    if current_section_title and current_section_content:
        result["sections"].append({
            "title": current_section_title,
            "content": " ".join(current_section_content)
        })

    if not result["title"]:
        logger.warning("parse_body returned empty title, content length: %d", len(content))

    return result