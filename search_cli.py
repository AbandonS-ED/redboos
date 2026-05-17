"""联网搜索工具 - 通过 Tavily API 搜索资料并保存为 Markdown"""
import argparse
import json
import logging
import pathlib
import sys
import urllib.request
from datetime import datetime

from generator.config import load_config, load_tavily_key

TAVILY_URL = "https://api.tavily.com/search"

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def tavily_search(query: str, max_results: int, include_answer: bool,
                 search_depth: str, config_path: str, api_key: str = None) -> dict:
    """直接调用 Tavily API，返回原始结果字典"""
    key = load_tavily_key(config_path, api_key)
    if not key:
        raise ValueError("未找到 Tavily API Key，请提供 --api-key 或在 config.yaml 中配置")

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
        raise RuntimeError(f"网络错误: {e}")

    try:
        obj = json.loads(body)
    except json.JSONDecodeError:
        raise RuntimeError("Tavily API 响应格式错误")

    if obj.get("detail"):
        raise RuntimeError(f"Tavily API 错误: {obj.get('detail')}")

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
                    include_answer: bool, search_depth: str,
                    config_path: str, api_key: str = None) -> None:
    """执行搜索并保存结果"""
    enhanced_topic = enhance_query_for_chinese(topic)
    if enhanced_topic != topic:
        logger.info(f"自动优化查询: {topic} -> {enhanced_topic}")

    logger.info(f"搜索主题: {enhanced_topic}")

    result = tavily_search(enhanced_topic, max_results, include_answer, search_depth,
                          config_path, api_key)

    lines = [f"# {topic}\n"]

    if include_answer and result.get("answer"):
        lines.append(result["answer"].strip())
        lines.append("")

    results = result.get("results") or []
    if not results:
        raise ValueError(f"未找到相关结果: {topic}")

    for i, r in enumerate(results, 1):
        title = r.get("title") or "无标题"
        url = r.get("url") or ""
        content = (r.get("content") or "").strip()

        lines.append(f"## 来源{i}")
        lines.append(f"[{title}]({url})")
        if content:
            lines.append(f"{content}\n")

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

    if args.output:
        output_dir = pathlib.Path(args.output)
    else:
        output_dir = pathlib.Path(__file__).parent.parent / "zhiliao"
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        search_and_save(args.topic, args.max_results, output_dir,
                        args.include_answer, args.search_depth,
                        args.config, args.api_key)
    except (ValueError, RuntimeError) as e:
        logger.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()