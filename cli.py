"""CLI 入口"""
import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

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
    parser.add_argument("--num", type=int, default=1)
    parser.add_argument("--topic", type=str, required=True)
    parser.add_argument("--type", type=str, default="AI工具推荐")
    parser.add_argument("--format", type=str, choices=["json", "md", "both"], default="both")
    parser.add_argument("--config", type=str, default="config.yaml")
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--output", type=str, default="output")
    parser.add_argument("--start-no", type=int, default=1)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--material", type=str, default=None, help="参考资料文件路径，留空则自动按topic匹配zhiliao/目录")

    args = parser.parse_args()
    setup_logging(args.verbose)

    # 自动匹配参考资料：模糊匹配 zhiliao/ 目录下的文件
    material_content = None
    if args.material:
        mat_path = Path(args.material)
        if mat_path.exists():
            material_content = mat_path.read_text(encoding="utf-8")
            logging.info(f"已加载参考资料: {args.material}")
        else:
            logging.warning(f"参考资料文件不存在: {args.material}")
    else:
        # 模糊匹配：文件名包含 topic 关键词（去除空格和下划线后比对）
        zhiliao_dir = Path("..") / "zhiliao"
        if not zhiliao_dir.exists():
            logging.error(f"zhiliao/ 目录不存在")
            sys.exit(1)

        topic_normalized = args.topic.replace(" ", "").replace("_", "")

        def match_score(path):
            stem = path.stem.replace(" ", "").replace("_", "")
            # 关键词完全包含在文件名中，或文件名完全包含关键词
            if topic_normalized in stem or stem in topic_normalized:
                return len(stem)  # 越短越精确
            return float('inf')

        candidates = [f for f in zhiliao_dir.glob("*.md")]
        scored = [(f, match_score(f)) for f in candidates]
        candidates = [f for f, score in scored if score != float('inf')]

        if len(candidates) == 0:
            logging.error(f"zhiliao/ 目录中未找到匹配「{args.topic}」的文件")
            sys.exit(1)
        elif len(candidates) > 1:
            logging.error(f"匹配到多个候选文件，请手动指定 --material：")
            for c in candidates:
                logging.error(f"  - {c}")
            sys.exit(1)
        else:
            material_content = candidates[0].read_text(encoding="utf-8")
            logging.info(f"已自动匹配参考资料: {candidates[0]}")

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
        start_no=args.start_no,
        material=material_content
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