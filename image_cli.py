"""AI 画图独立工具 - 从 .md 文件读取配图提示词生成图片"""
import argparse
import logging
import re
import sys
from pathlib import Path

from generator.config import load_config
from generator.providers import get_image_client


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def extract_image_prompts(md_path: Path) -> list:
    """从 .md 文件中提取所有配图提示词"""
    content = md_path.read_text(encoding="utf-8")

    prompts = []
    # 匹配 ### 图片N 或 ### 配图提示词 之后的列表内容
    # 找到所有 "步骤一"、"步骤二" 等标题后面的内容
    step_pattern = re.compile(r'^### (?:图片|配图提示词)\s*$.*?(?=^###|\Z)', re.MULTILINE | re.DOTALL)

    # 简单方式：找到所有以 - 开头的内容块（图片描述区域）
    # 先找到"配图提示词"部分
    prompts_section = re.search(r'[#]+ 配图提示词\s*(.*?)(?=#+ [^配图提示词]|$)', content, re.DOTALL | re.IGNORECASE)
    if not prompts_section:
        logging.warning("未找到配图提示词部分")
        return []

    section_text = prompts_section.group(1)

    # 找到所有图片块（以 ### 图片N 或 ### 配图提示词 开头）
    image_blocks = re.findall(r'### (?:图片\s*\d+|配图提示词)\s*\n(.*?)(?=### (?:图片\s*\d+|配图提示词)|$)', section_text, re.DOTALL)

    for i, block in enumerate(image_blocks, 1):
        # 提取这个块中的主体内容（去掉 - 列表前缀和其他标记）
        lines = block.strip().split('\n')
        cleaned_lines = []
        skip_first = True
        for line in lines:
            # 跳过第一行的【重要声明】行
            if skip_first and '【重要声明】' in line:
                skip_first = False
                continue
            if skip_first:
                continue
            # 跳过空行和声明行
            if line.strip() in ('', '---'):
                continue
            # 去掉列表前缀 -
            line = re.sub(r'^-\s*', '', line)
            cleaned_lines.append(line)

        if cleaned_lines:
            prompts.append('\n'.join(cleaned_lines))
            logging.info(f"提取到图片 {i} 的提示词 ({len(cleaned_lines)} 行)")

    return prompts


def main():
    parser = argparse.ArgumentParser(
        description="AI 画图工具 - 从 .md 文件读取配图提示词生成图片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python image_cli.py --input output/xiaohongshu_Anthropic公司介绍_20260515_141858.md
  python image_cli.py --input output/xxx.md --output images/
  python image_cli.py --input output/xxx.md --provider minimax
        """
    )
    parser.add_argument("--input", "-i", type=str, required=True, help="包含配图提示词的 .md 文件路径")
    parser.add_argument("--output", "-o", type=str, default="images", help="图片输出目录（默认: images）")
    parser.add_argument("--config", "-c", type=str, default="config.yaml", help="配置文件路径（默认: config.yaml）")
    parser.add_argument("--provider", "-p", type=str, default=None, help="AI Provider（默认从 config.yaml 读取）")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")

    args = parser.parse_args()
    setup_logging(args.verbose)

    # 检查输入文件
    md_path = Path(args.input)
    if not md_path.exists():
        logging.error(f"文件不存在: {args.input}")
        sys.exit(1)

    # 加载配置
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        logging.error(f"配置文件不存在: {args.config}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"加载配置失败: {e}")
        sys.exit(1)

    # 获取 provider
    provider = args.provider or config.get("provider", "minimax")
    logging.info(f"使用 Provider: {provider}")

    # 初始化生图客户端
    image_api = get_image_client(provider, config)
    if not image_api:
        logging.error(f"无法初始化生图客户端 (provider: {provider})")
        sys.exit(1)

    logging.info(f"生图 Provider: {image_api.provider_name}")

    # 提取提示词
    prompts = extract_image_prompts(md_path)
    if not prompts:
        logging.error("未能从文件中提取到配图提示词")
        sys.exit(1)

    logging.info(f"共提取到 {len(prompts)} 张图片的提示词")

    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成图片
    for i, prompt in enumerate(prompts, 1):
        logging.info(f"正在生成图片 {i}/{len(prompts)} ...")

        image_data = image_api.generate_image(prompt)
        if image_data:
            img_path = output_dir / f"image_{i}.png"
            with open(img_path, "wb") as f:
                f.write(image_data)
            logging.info(f"已保存: {img_path}")
        else:
            logging.warning(f"图片 {i} 生成失败，跳过")

    logging.info(f"完成: 共生成 {len([p for p in prompts])} 张图片，输出目录: {output_dir.absolute()}")


if __name__ == "__main__":
    main()