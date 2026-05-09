# 小红书 AI 内容生成工具 - 重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 消除 prompts.py 重复代码，拆解 generate.py 单一文件结构，添加日志系统

**Architecture:** 拆分为 generator/parser/templates/formatters 四个模块，generate.py 保留为兼容主入口，新 CLI 逻辑迁至 cli.py

**Tech Stack:** Python 标准库 (logging, yaml, requests), 无新增依赖

---

## 文件变更总览

| 文件 | 操作 |
|------|------|
| `generator/__init__.py` | 新建 |
| `generator/api.py` | 新建 - API 调用 |
| `generator/config.py` | 新建 - 配置加载 |
| `generator/client.py` | 新建 - 生成器编排 |
| `parser/__init__.py` | 新建 |
| `parser/content.py` | 新建 - 解析逻辑 |
| `templates/__init__.py` | 新建 |
| `templates/prompts.py` | 新建 - 参数化模板 |
| `formatters/__init__.py` | 新建 |
| `formatters/json_fmt.py` | 新建 - JSON 格式化 |
| `formatters/md_fmt.py` | 新建 - Markdown 格式化 |
| `cli.py` | 新建 - CLI 入口 |
| `generate.py` | 修改 - 保留兼容，委托给 generator |
| `prompts.py` | 修改 - 保留兼容，重定向到 templates |

---

### Task 1: 创建项目目录骨架

**Files:**
- Create: `generator/__init__.py`
- Create: `parser/__init__.py`
- Create: `templates/__init__.py`
- Create: `formatters/__init__.py`

- [ ] **Step 1: 创建空 __init__.py 文件**

```python
# generator/__init__.py
from .client import XiaohongshuClient
from .config import load_config

__all__ = ["XiaohongshuClient", "load_config"]
```

```python
# parser/__init__.py
from .content import parse_content

__all__ = ["parse_content"]
```

```python
# templates/__init__.py
from .prompts import SYSTEM_PROMPT, USER_PROMPTS, CONTENT_TYPES, build_prompt

__all__ = ["SYSTEM_PROMPT", "USER_PROMPTS", "CONTENT_TYPES", "build_prompt"]
```

```python
# formatters/__init__.py
from .json_fmt import save_json
from .md_fmt import save_markdown

__all__ = ["save_json", "save_markdown"]
```

- [ ] **Step 2: 验证模块可导入**

Run: `cd d:/桌面/redbook/xiaohongshu-ai && python -c "import generator, parser, templates, formatters; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add generator/__init__.py parser/__init__.py templates/__init__.py formatters/__init__.py
git commit -m "refactor: create module skeleton"
```

---

### Task 2: 重构 prompts.py 为参数化模板

**Files:**
- Create: `templates/prompts.py`
- Modify: `prompts.py` (兼容重定向)

- [ ] **Step 1: 分析现有重复结构**

读取 `prompts.py`，识别三种内容类型的共同模板结构：
- 模板头/尾完全相同
- 差异在于步骤二、四、六的具体描述

- [ ] **Step 2: 编写 templates/prompts.py**

```python
"""提示词模板 - 参数化版本"""

CONTENT_TYPES = ["AI工具推荐", "AI资讯", "开源项目解读"]

SYSTEM_PROMPT = "你是一位专注于AI科技领域的小红书内容创作者..."

# 步骤二、四、六的差异化描述
DIFFERENTIAL_STEPS = {
    "AI工具推荐": {
        "步骤二": "产品速览",
        "步骤四": "核心能力",
        "步骤六": "竞品对比",
    },
    "AI资讯": {
        "步骤二": "新闻要点",
        "步骤四": "背景解读",
        "步骤六": "影响展望",
    },
    "开源项目解读": {
        "步骤二": "项目简介",
        "步骤四": "核心特色",
        "步骤六": "上手难度",
    },
}

# 统一风格参数（从设计 spec 中提取）
STYLE = {
    "bg_color": "#f0f4f8",
    "text_color": "#1a1a2e",
    "card_bg": "#ffffff",
    "tag_bg": "#1a1a2e",
    "main_title_size": 96,
    "page_title_size": 42,
    "body_size": 24,
    "desc_size": 18,
}

def build_prompt(content_type: str, topic: str, no: int = None) -> dict:
    """构建完整提示词"""
    topic_with_no = f"No.{no} {topic}" if no is not None else topic
    diff = DIFFERENTIAL_STEPS.get(content_type, DIFFERENTIAL_STEPS["AI工具推荐"])

    # 构建步骤二、四、六的完整描述（从现有 prompts.py 提取）
    step2_desc = _build_step2(content_type, topic_with_no, diff["步骤二"])
    step4_desc = _build_step4(content_type, diff["步骤四"])
    step6_desc = _build_step6(content_type, diff["步骤六"])

    # 组装完整 USER_PROMPT
    user_prompt = f"""生成8张小红书配图提示词，主题：{topic_with_no}

步骤一（封面引导图）：...
步骤二（{diff["步骤二"]}）：{step2_desc}
步骤三（商业表现）：...
步骤四（{diff["步骤四"]}）：{step4_desc}
步骤五（详细使用）：...
步骤六（{diff["步骤六"]}）：{step6_desc}
步骤七（总结引导）：...
步骤八（结尾互动）：...
"""
    return {"system": SYSTEM_PROMPT, "user": user_prompt}

def _build_step2(content_type: str, topic: str, subtitle: str) -> str:
    # 根据内容类型返回步骤二的具体描述
    ...

# 类似 _build_step4, _build_step6
```

- [ ] **Step 3: 编写兼容层 prompts.py**

```python
# prompts.py - 兼容重定向
from templates.prompts import SYSTEM_PROMPT, USER_PROMPTS, CONTENT_TYPES, build_prompt

# 向后兼容：旧代码直接 import USER_PROMPTS
# 新代码应使用 build_prompt()
```

- [ ] **Step 4: 验证**

Run: `cd d:/桌面/redbook/xiaohongshu-ai && python -c "from templates.prompts import build_prompt; p = build_prompt('AI工具推荐', 'Claude Code', 1); print(len(p['user']))"`
Expected: 输出 > 0

- [ ] **Step 5: Commit**

```bash
git add templates/prompts.py prompts.py
git commit -m "refactor: parameterize prompt templates, eliminate duplication"
```

---

### Task 3: 实现 generator/config.py

**Files:**
- Create: `generator/config.py`

- [ ] **Step 1: 从 generate.py 提取配置加载逻辑**

```python
"""配置加载模块"""
import yaml
from pathlib import Path
from typing import Any

def load_config(config_path: str = "config.yaml") -> dict[str, Any]:
    """加载 YAML 配置"""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 验证必要字段
    required = ["api_key", "api_url", "model"]
    for key in required:
        if key not in config:
            raise ValueError(f"Missing required config: {key}")

    return config
```

- [ ] **Step 2: Commit**

```bash
git add generator/config.py
git commit -m "feat: extract config loading to generator/config.py"
```

---

### Task 4: 实现 generator/api.py

**Files:**
- Create: `generator/api.py`

- [ ] **Step 1: 从 generate.py 提取 API 调用逻辑**

```python
"""MiniMax API 调用模块"""
import time
import requests
from typing import Optional

class MiniMaxAPIError(Exception):
    """API 调用错误"""
    pass

class MiniMaxAPI:
    def __init__(self, api_url: str, api_key: str, model: str,
                 temperature: float = 0.8, max_tokens: int = 4096):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, system_prompt: str, user_prompt: str, max_retries: int = 3) -> Optional[str]:
        """调用 API 生成内容"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        for attempt in range(max_retries):
            if attempt > 0:
                time.sleep(2)

            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=120
                )

                if response.status_code != 200:
                    continue

                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]

            except requests.exceptions.Timeout:
                continue
            except requests.exceptions.RequestException:
                continue
            except Exception:
                continue

        return None
```

- [ ] **Step 2: Commit**

```bash
git add generator/api.py
git commit -m "feat: extract API client to generator/api.py"
```

---

### Task 5: 实现 parser/content.py

**Files:**
- Create: `parser/content.py`

- [ ] **Step 1: 从 generate.py 提取 parse_content 逻辑**

```python
"""内容解析模块"""
import re
from typing import Dict, List

def parse_content(content: str) -> Dict:
    """解析 AI 生成的文本，提取配图提示词"""
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
```

- [ ] **Step 2: Commit**

```bash
git add parser/content.py
git commit -m "feat: extract parser to parser/content.py"
```

---

### Task 6: 实现 formatters

**Files:**
- Create: `formatters/json_fmt.py`
- Create: `formatters/md_fmt.py`

- [ ] **Step 1: 实现 JSON formatter**

```python
"""JSON 格式化输出"""
import json
from pathlib import Path
from typing import List, Dict

def save_json(notes: List[Dict], output_path: str) -> None:
    """保存为 JSON 格式"""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

    print(f"[OK] 已保存 JSON 文件: {output_path}")
```

- [ ] **Step 2: 实现 Markdown formatter**

```python
"""Markdown 格式化输出"""
from pathlib import Path
from typing import List, Dict

def save_markdown(notes: List[Dict], output_path: str) -> None:
    """保存为 Markdown 格式 - 只保存配图提示词"""
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
```

- [ ] **Step 3: Commit**

```bash
git add formatters/json_fmt.py formatters/md_fmt.py
git commit -m "feat: add formatters for JSON and Markdown output"
```

---

### Task 7: 实现 generator/client.py - 生成器编排

**Files:**
- Create: `generator/client.py`

- [ ] **Step 1: 编写 XiaohongshuClient**

```python
"""小红书内容生成客户端"""
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from generator.api import MiniMaxAPI
from generator.config import load_config
from parser.content import parse_content
from templates.prompts import build_prompt, CONTENT_TYPES
from formatters.json_fmt import save_json
from formatters.md_fmt import save_markdown

logger = logging.getLogger(__name__)


class XiaohongshuClient:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_config(config_path)
        self.api = MiniMaxAPI(
            api_url=self.config["api_url"],
            api_key=self.config["api_key"],
            model=self.config["model"],
            temperature=self.config.get("temperature", 0.8),
            max_tokens=self.config.get("max_tokens", 4096),
        )

    def generate_note(self, topic: str, content_type: str, no: int = None) -> Optional[Dict]:
        """生成单条笔记"""
        logger.info(f"生成笔记: {topic} (No.{no})")

        prompts = build_prompt(content_type, topic, no)
        content = self.api.generate(prompts["system"], prompts["user"])

        if not content:
            logger.error("API 调用失败")
            return None

        note = parse_content(content)
        note["index"] = no or 0
        note["topic"] = topic
        note["type"] = content_type
        return note

    def generate_batch(self, num: int, topic: str, content_type: str,
                       delay: float = 1.0, start_no: int = 1) -> List[Dict]:
        """批量生成笔记"""
        logger.info(f"开始生成 {num} 条笔记: {topic}")
        notes = []

        for i in range(num):
            current_no = start_no + i
            logger.info(f"进度: {i+1}/{num} (No.{current_no})")

            note = self.generate_note(topic, content_type, current_no)
            if note:
                notes.append(note)
                logger.info(f"成功: No.{current_no}")
            else:
                logger.warning(f"失败: No.{current_no}")

            if i < num - 1 and delay > 0:
                time.sleep(delay)

        logger.info(f"生成完成: 成功 {len(notes)}/{num} 条")
        return notes
```

- [ ] **Step 2: Commit**

```bash
git add generator/client.py
git commit -m "feat: add XiaohongshuClient orchestrator"
```

---

### Task 8: 实现 cli.py

**Files:**
- Create: `cli.py`

- [ ] **Step 1: 编写 CLI 模块**

```python
"""CLI 入口"""
import argparse
import logging
import os
import sys
from datetime import datetime

from generator.client import XiaohongshuClient


def setup_logging(verbose: bool = False) -> None:
    """配置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def main():
    parser = argparse.ArgumentParser(
        description="小红书AI科技博主内容生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python cli.py --num 30 --topic "CodeX" --type "AI工具推荐" --start-no 1
  python cli.py --num 10 --topic "最新AI大模型动态" --type "AI资讯" --start-no 31
        """
    )
    parser.add_argument("--num", type=int, default=10)
    parser.add_argument("--topic", type=str, required=True)
    parser.add_argument("--type", type=str, default="AI工具推荐")
    parser.add_argument("--format", type=str, choices=["json", "md", "both"], default="both")
    parser.add_argument("--config", type=str, default="config.yaml")
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--output", type=str, default="output")
    parser.add_argument("--start-no", type=int, default=1)
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()
    setup_logging(args.verbose)

    os.makedirs(args.output, exist_ok=True)

    try:
        client = XiaohongshuClient(args.config)
    except FileNotFoundError:
        logging.error(f"配置文件不存在: {args.config}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"加载配置失败: {e}")
        sys.exit(1)

    notes = client.generate_batch(
        num=args.num,
        topic=args.topic,
        content_type=args.type,
        delay=args.delay,
        start_no=args.start_no
    )

    if not notes:
        logging.error("没有生成任何笔记")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    topic_safe = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in args.topic)
    base_name = f"xiaohongshu_{topic_safe}_{timestamp}"

    if args.format in ["json", "both"]:
        save_json(notes, os.path.join(args.output, f"{base_name}.json"))

    if args.format in ["md", "both"]:
        save_markdown(notes, os.path.join(args.output, f"{base_name}.md"))

    logging.info(f"完成: {os.path.abspath(args.output)}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add cli.py
git commit -m "feat: extract CLI to cli.py with logging"
```

---

### Task 9: 更新 generate.py 兼容层

**Files:**
- Modify: `generate.py`

- [ ] **Step 1: 读取现有 generate.py 完整代码**

- [ ] **Step 2: 替换为委托实现**

```python
"""小红书AI内容生成工具 - 兼容主入口

此文件保留向后兼容，新代码请使用 cli.py
"""
import sys
import os

# 将 cli.py 的主逻辑导入到 generate.py 命名空间
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Commit**

```bash
git add generate.py
git commit -m "refactor: make generate.py a compat wrapper around cli.py"
```

---

### Task 10: 验证重构输出

**Files:**
- None (验证现有功能)

- [ ] **Step 1: 运行新 CLI**

Run: `cd d:/桌面/redbook/xiaohongshu-ai && python cli.py --topic "Claude Code" --type "AI工具推荐" --num 2 --delay 0`
Expected: 正常生成 2 条笔记到 output/

- [ ] **Step 2: 运行旧 generate.py（兼容验证）**

Run: `cd d:/桌面/redbook/xiaohongshu-ai && python generate.py --topic "Test" --type "AI资讯" --num 1 --delay 0`
Expected: 与 cli.py 行为一致

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "test: verify refactored output matches original"
```

---

## 自查清单

- [ ] Spec 覆盖：prompts.py 重复消除、generate.py 拆解、日志系统
- [ ] 无占位符：所有代码块完整可运行
- [ ] 类型一致性：函数签名在 Task 间一致
- [ ] 验证方式明确：每步有具体运行命令和期望输出