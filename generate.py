"""小红书AI内容生成工具 - 主脚本"""

import argparse
import json
import sys
import time
import yaml
import requests
from datetime import datetime
from typing import List, Dict
import os

# Import prompts
from prompts import SYSTEM_PROMPT, USER_PROMPTS, CONTENT_TYPES


class XiaohongshuGenerator:
    """小红书内容生成器"""

    def __init__(self, config_path: str = "config.yaml"):
        """初始化加载配置"""
        self.config = self._load_config(config_path)
        self.api_url = self.config["api_url"]
        self.api_key = self.config["api_key"]
        self.model = self.config["model"]
        self.temperature = self.config.get("temperature", 0.8)
        self.max_tokens = self.config.get("max_tokens", 2048)

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def generate_content(self, topic: str, content_type: str, no: int = None) -> str:
        """调用 MiniMax API 生成内容"""
        # 获取提示词模板
        if content_type not in USER_PROMPTS:
            raise ValueError(f"无效的内容类型: {content_type}，可用类型: {CONTENT_TYPES}")

        # 如果有编号，添加到topic中
        if no is not None:
            topic_with_no = f"No.{no} {topic}"
        else:
            topic_with_no = topic

        user_prompt = USER_PROMPTS[content_type].format(topic=topic_with_no)

        # 构建请求
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        max_retries = 3

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"[重试] 第 {attempt + 1} 次尝试...")
                    time.sleep(2)

                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=120
                )

                if response.status_code != 200:
                    print(f"[ERROR] API 返回错误状态码: {response.status_code}")
                    print(f"[ERROR] 响应内容: {response.text}")
                    if attempt < max_retries - 1:
                        continue
                    return None

                result = response.json()

                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    print(f"[ERROR] API 响应中没有 choices: {result}")
                    if attempt < max_retries - 1:
                        continue
                    return None

            except requests.exceptions.Timeout:
                print("[ERROR] 请求超时，请检查网络连接或增加超时时间")
                if attempt < max_retries - 1:
                    continue
                return None
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] 请求异常: {e}")
                if attempt < max_retries - 1:
                    continue
                return None
            except json.JSONDecodeError as e:
                print(f"[ERROR] JSON 解析失败: {e}")
                print(f"[ERROR] 原始响应: {response.text}")
                if attempt < max_retries - 1:
                    continue
                return None

        return None

    def parse_content(self, content: str) -> Dict:
        """解析生成的文本，只提取配图提示词"""
        import re
        result = {
            "image_prompts": []
        }

        if not content:
            return result

        lines = content.split("\n")
        current_prompt_lines = []
        step_pattern = re.compile(r'^步骤[一二三四五六七八九十]+（([^）]+)）：')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检测步骤标题行，如"步骤一（封面引导图）："或"## 步骤一（封面引导图）："或"**步骤一（封面引导图）：**"或"步骤1（封面引导图）：**"
            step_match = step_pattern.match(line.lstrip('*').strip())

            if step_match:
                # 保存上一个prompt
                if current_prompt_lines:
                    result["image_prompts"].append("\n".join(current_prompt_lines).strip())
                    current_prompt_lines = []
                # 开始新的prompt
                current_prompt_lines.append(line)
            elif line.startswith("【配图提示词】"):
                # 开始新的配图提示词section，重置
                if current_prompt_lines:
                    result["image_prompts"].append("\n".join(current_prompt_lines).strip())
                    current_prompt_lines = []
            elif line.startswith("## 步骤"):
                # markdown二级标题开始的步骤，保存当前并开始新的
                if current_prompt_lines:
                    result["image_prompts"].append("\n".join(current_prompt_lines).strip())
                    current_prompt_lines = []
                current_prompt_lines.append(line)
            elif line.startswith("**步骤") and line.endswith("**"):
                # 纯粗体包裹的步骤标题行，如"**步骤一（封面引导图）：**"，保存当前并开始新prompt
                if current_prompt_lines:
                    result["image_prompts"].append("\n".join(current_prompt_lines).strip())
                    current_prompt_lines = []
                current_prompt_lines.append(line.lstrip('*').strip())
            elif line.startswith("### 图片"):
                # 遇到图片标记，跳过不作为内容（AI生成的冗余标记）
                continue
            elif line.startswith("# 小红书配图提示词") or line.startswith("# Claude Code 小红书"):
                # 跳过总标题行和主题行
                continue
            else:
                current_prompt_lines.append(line)

        # 保存最后一个prompt
        if current_prompt_lines:
            result["image_prompts"].append("\n".join(current_prompt_lines).strip())

        return result

    def save_json(self, notes: List[Dict], output_path: str):
        """保存为 JSON 格式"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
        print(f"[OK] 已保存 JSON 文件: {output_path}")

    def save_markdown(self, notes: List[Dict], output_path: str):
        """保存为 Markdown 格式 - 只保存配图提示词"""
        with open(output_path, "w", encoding="utf-8") as f:
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

    def generate_batch(self, num: int, topic: str, content_type: str, delay: float = 1.0, start_no: int = 1) -> List[Dict]:
        """批量生成笔记"""
        notes = []

        print(f"\n开始生成 {num} 条笔记...")
        print(f"主题: {topic}")
        print(f"类型: {content_type}")
        print(f"起始编号: No.{start_no}")
        print("-" * 50)

        for i in range(num):
            current_no = start_no + i
            print(f"\n[进度] 生成第 {i + 1}/{num} 条笔记 (No.{current_no})...")

            content = self.generate_content(topic, content_type, no=current_no)

            if content:
                note = self.parse_content(content)
                note["index"] = i + 1
                note["topic"] = topic
                note["type"] = content_type
                notes.append(note)

                print(f"[OK] 第 {i + 1} 条笔记生成成功")
                print(f"  标题: {note.get('title', 'N/A')[:50]}...")
            else:
                print(f"[FAIL] 第 {i + 1} 条笔记生成失败")

            # 添加延迟，避免 API 限流
            if i < num - 1 and delay > 0:
                print(f"[等待] 等待 {delay} 秒...")
                time.sleep(delay)

        print("\n" + "-" * 50)
        print(f"生成完成: 成功 {len(notes)} 条")

        return notes


def main():
    parser = argparse.ArgumentParser(
        description="小红书AI科技博主内容生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python generate.py --num 30 --topic "CodeX" --type "AI工具推荐" --start-no 1
  python generate.py --num 10 --topic "最新AI大模型动态" --type "AI资讯" --format md --start-no 31
  python generate.py --num 5 --topic "有趣的GitHub开源项目" --type "开源项目解读" --delay 2 --start-no 11
        """
    )

    parser.add_argument("--num", type=int, default=10,
                        help="生成数量，默认 10")
    parser.add_argument("--topic", type=str, required=True,
                        help="笔记主题，如：'CodeX'")
    parser.add_argument("--type", type=str,
                        choices=CONTENT_TYPES,
                        default="AI工具推荐",
                        help="内容类型，可选: " + ", ".join(CONTENT_TYPES))
    parser.add_argument("--format", type=str,
                        choices=["json", "md", "both"],
                        default="both",
                        help="输出格式: json, md, both（默认 both）")
    parser.add_argument("--config", type=str, default="config.yaml",
                        help="配置文件路径，默认 config.yaml")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="每次生成后的等待秒数，默认 1.0")
    parser.add_argument("--output", type=str, default="output",
                        help="输出目录，默认 output")
    parser.add_argument("--start-no", type=int, default=1,
                        help="起始编号，默认 1（如：--start-no 12 则从 No.12 开始）")

    args = parser.parse_args()

    # 创建输出目录
    os.makedirs(args.output, exist_ok=True)

    # 初始化生成器
    try:
        generator = XiaohongshuGenerator(args.config)
    except FileNotFoundError:
        print(f"[ERROR] 配置文件不存在: {args.config}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] 加载配置失败: {e}")
        sys.exit(1)

    # 批量生成
    notes = generator.generate_batch(
        num=args.num,
        topic=args.topic,
        content_type=args.type,
        delay=args.delay,
        start_no=args.start_no
    )

    if not notes:
        print("[ERROR] 没有生成任何笔记，退出")
        sys.exit(1)

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    topic_safe = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in args.topic)
    base_name = f"xiaohongshu_{topic_safe}_{timestamp}"

    # 保存文件
    output_dir = args.output

    if args.format in ["json", "both"]:
        json_path = os.path.join(output_dir, f"{base_name}.json")
        generator.save_json(notes, json_path)

    if args.format in ["md", "both"]:
        md_path = os.path.join(output_dir, f"{base_name}.md")
        generator.save_markdown(notes, md_path)

    print(f"\n[完成] 所有文件已保存到: {os.path.abspath(output_dir)}")


if __name__ == "__main__":
    main()