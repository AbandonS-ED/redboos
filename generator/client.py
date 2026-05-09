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