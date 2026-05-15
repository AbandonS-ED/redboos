"""联网搜索工具 - 通过 Tavily API 搜索资料并保存为 Markdown"""
import argparse
import json
import logging
import os
import pathlib
import re
import sys
import urllib.request
from datetime import datetime

from generator.config import load_config

TAVILY_URL = "https://api.tavily.com/search"

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def load_tavily_key(config_path: str = "config.yaml", cli_key: str = None) -> str:
    """加载 Tavily API Key"""
    if cli_key:
        return cli_key

    # 从 config.yaml 读取
    try:
        config = load_config(config_path)
        key = config.get("tavily", {}).get("api_key")
        if key:
            return key
    except Exception:
        pass

    # 从环境变量读取
    key = os.environ.get("TAVILY_API_KEY")
    if key:
        return key.strip()

    # 从 ~/.openclaw/.env 读取
    env_path = pathlib.Path.home() / ".openclaw" / ".env"
    if env_path.exists():
        try:
            txt = env_path.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"^\s*TAVILY_API_KEY\s*=\s*(.+?)\s*$", txt, re.M)
            if m:
                return m.group(1).strip().strip('"').strip("'")
        except Exception:
            pass

    return None


def tavily_search(query: str, max_results: int, include_answer: bool, search_depth: str) -> dict:
    """直接调用 Tavily API"""
    key = load_tavily_key()
    if not key:
        logger.error("未找到 Tavily API Key，请提供 --api-key 或在 config.yaml 中配置")
        sys.exit(1)

    payload = {
        "api_key": key,
        "query": query,
        "max_results": max_results,
        "search_depth": search_depth,
        "include_answer": include_answer,
        "include_images": False,
        "include_raw_content": False,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        TAVILY_URL,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        logger.error("网络错误")
        sys.exit(1)

    try:
        obj = json.loads(body)
    except json.JSONDecodeError:
        logger.error("Tavily API 报错")
        sys.exit(1)

    if obj.get("detail"):
        logger.error("Tavily API 报错")
        sys.exit(1)

    return obj


def is_chinese(text: str) -> bool:
    """检测是否包含中文字符"""
    return any('一' <= c <= '鿿' for c in text)

def enhance_query_for_chinese(query: str) -> str:
    """如果不是中文查询，自动添加中文后缀"""
    if not is_chinese(query):
        return f"{query} 中文"
    return query


def search_and_save(topic: str, max_results: int, output_dir: pathlib.Path,
                    include_answer: bool, search_depth: str) -> None:
    """执行搜索并保存结果"""
    # 增强查询：非中文自动加"中文"后缀
    enhanced_topic = enhance_query_for_chinese(topic)
    if enhanced_topic != topic:
        logger.info(f"自动优化查询: {topic} -> {enhanced_topic}")

    logger.info(f"搜索主题: {enhanced_topic}")

    try:
        result = tavily_search(enhanced_topic, max_results, include_answer, search_depth)
    except SystemExit:
        sys.exit(1)

    # 构建 Markdown
    lines = [f"# {topic}\n"]

    # AI 整理的摘要答案
    if include_answer and result.get("answer"):
        lines.append(result["answer"].strip())
        lines.append("")

    # 搜索结果
    results = result.get("results") or []
    if not results:
        logger.error("未找到相关结果")
        sys.exit(1)

    for i, r in enumerate(results, 1):
        title = r.get("title") or "无标题"
        url = r.get("url") or ""
        content = (r.get("content") or "").strip()

        lines.append(f"## 来源{i}")
        lines.append(f"[{title}]({url})")
        if content:
            lines.append(f"{content}\n")

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c for c in topic if c.isalnum() or c in (" ", "_", "-")).strip()
    safe_topic = safe_topic.replace(" ", "_")
    filename = f"{safe_topic}_{timestamp}.md"
    output_path = output_dir / filename

    output_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"已保存: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="联网搜索工具 - 通过 Tavily API 搜索资料",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--topic", "-t", type=str, required=True, help="搜索主题")
    parser.add_argument("--max-results", "-n", type=int, default=5, help="返回结果数量（默认: 5）")
    parser.add_argument("--api-key", "-k", type=str, default=None, help="Tavily API Key")
    parser.add_argument("--output", "-o", type=str, default=None, help="输出目录（默认: zhiliao）")
    parser.add_argument("--config", "-c", type=str, default="config.yaml", help="配置文件（默认: config.yaml）")
    parser.add_argument("--include-answer", "-a", action="store_true", help="包含 AI 整理的摘要答案")
    parser.add_argument("--search-depth", "-d", default="advanced",
                        choices=["basic", "advanced"], help="搜索深度（默认: advanced）")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")

    args = parser.parse_args()
    setup_logging(args.verbose)

    # 默认输出到上级 zhiliao 目录
    if args.output:
        output_dir = pathlib.Path(args.output)
    else:
        output_dir = pathlib.Path(__file__).parent.parent / "zhiliao"
    output_dir.mkdir(parents=True, exist_ok=True)

    search_and_save(args.topic, args.max_results, output_dir,
                    args.include_answer, args.search_depth)


if __name__ == "__main__":
    main()