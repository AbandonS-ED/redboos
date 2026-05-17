"""小红书内容生成客户端"""
import logging
import time
from pathlib import Path
from typing import List, Dict, Optional

from generator.config import load_config
from generator.exceptions import MaterialNotFoundError, MaterialAmbiguousError
from generator.providers import get_text_client
from generator.constants import DEFAULT_DELAY
from parser.content import parse_content, parse_body
from templates import get_template
from formatters.json_fmt import save_json
from formatters.md_fmt import save_markdown

logger = logging.getLogger(__name__)


class XiaohongshuClient:
    def __init__(self, config_path: str = "config.yaml", template_name: str = "ai_tech"):
        self.config = load_config(config_path)

        # 根据 provider 加载对应的文本生成客户端
        provider = self.config.get("provider", "minimax")
        self.api = get_text_client(provider, self.config)
        logger.info(f"使用 AI Provider: {self.api.provider_name}")

        self.template = get_template(template_name)

    def generate_note(self, topic: str, content_type: str, no: int = None,
                   material: str = None, output_dir: str = "output") -> Optional[Dict]:
        """生成单条笔记（包含配图提示词和文案）

        Args:
            topic: 主题
            content_type: 内容类型
            no: 编号
            material: 参考资料
            output_dir: 输出目录
        """
        logger.info(f"生成笔记: {topic} (No.{no})")

        prompts = self.template.build_prompt(content_type, topic, no, material)
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
        prompts = self.template.build_body_prompt(note["topic"], note["type"], note["image_prompts"], material)
        body_text = self.api.generate(prompts["system"], prompts["user"])

        if body_text:
            note["body"] = parse_body(body_text)
            logger.info("文案生成成功")
        else:
            logger.error("文案生成失败")

    def generate_batch(self, num: int, topic: str, content_type: str,
                       delay: float = DEFAULT_DELAY, start_no: int = 1,
                       material: str = None, output_dir: str = "output") -> List[Dict]:
        """批量生成笔记"""
        logger.info(f"开始生成 {num} 条笔记: {topic}")
        notes = []

        for i in range(num):
            current_no = start_no + i
            logger.info(f"进度: {i+1}/{num} (No.{current_no})")

            note = self.generate_note(topic, content_type, current_no, material, output_dir)
            if note:
                notes.append(note)
                logger.info(f"成功: No.{current_no}")
            else:
                logger.warning(f"失败: No.{current_no}")

            if i < num - 1 and delay > 0:
                time.sleep(delay)

        logger.info(f"生成完成: 成功 {len(notes)}/{num} 条")
        return notes