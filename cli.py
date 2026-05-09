"""CLI 入口"""
import argparse
import logging
import os
import sys
from datetime import datetime

from generator.client import XiaohongshuClient
from formatters.json_fmt import save_json
from formatters.md_fmt import save_markdown


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