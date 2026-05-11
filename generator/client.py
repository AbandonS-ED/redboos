"""小红书内容生成客户端"""
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from generator.api import MiniMaxAPI
from generator.config import load_config
from parser.content import parse_content, parse_body
from templates.prompts import build_prompt, build_body_prompt, CONTENT_TYPES
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

    def generate_note(self, topic: str, content_type: str, no: int = None,
                   material: str = None) -> Optional[Dict]:
        """生成单条笔记（包含配图提示词和文案）"""
        logger.info(f"生成笔记: {topic} (No.{no})")

        prompts = build_prompt(content_type, topic, no, material)
        content = self.api.generate(prompts["system"], prompts["user"])

        if not content:
            logger.error("API 调用失败")
            return None

        note = parse_content(content)
        note["index"] = no or 0
        note["topic"] = topic
        note["type"] = content_type

        # 生成文案（传入参考资料）
        self.generate_body(note, material)

        return note

    def generate_body(self, note: Dict, material: str = None) -> None:
        """根据配图提示词和参考资料生成小红书文案"""
        if "image_prompts" not in note or not note["image_prompts"]:
            logger.warning("No image_prompts to generate body from")
            return

        logger.info("生成小红书文案...")
        prompts = build_body_prompt(note["topic"], note["type"], note["image_prompts"], material)
        body_text = self.api.generate(prompts["system"], prompts["user"])

        if body_text:
            note["body"] = parse_body(body_text)
            logger.info("文案生成成功")
        else:
            logger.warning("文案生成失败")

    def generate_batch(self, num: int, topic: str, content_type: str,
                       delay: float = 1.0, start_no: int = 1,
                       material: str = None) -> List[Dict]:
        """批量生成笔记"""
        logger.info(f"开始生成 {num} 条笔记: {topic}")
        notes = []

        for i in range(num):
            current_no = start_no + i
            logger.info(f"进度: {i+1}/{num} (No.{current_no})")

            note = self.generate_note(topic, content_type, current_no, material)
            if note:
                notes.append(note)
                logger.info(f"成功: No.{current_no}")
            else:
                logger.warning(f"失败: No.{current_no}")

            if i < num - 1 and delay > 0:
                time.sleep(delay)

        logger.info(f"生成完成: 成功 {len(notes)}/{num} 条")
        return notes