# 小红书 AI 内容生成工具 - 重构设计

## 目标

- 消除 prompts.py 的重复模板代码
- 拆解 generate.py 的单一文件结构，提升可读性和可维护性
- 添加日志系统
- 不添加测试（用户确认）

## 架构

```
xiaohongshu-ai/
├── generator/              # 新增：生成器模块
│   ├── __init__.py
│   ├── api.py              # API 调用逻辑
│   ├── config.py            # 配置加载
│   └── client.py            # 客户端封装
├── parser/
│   ├── __init__.py
│   └── content.py           # parse_content 解析逻辑
├── templates/
│   ├── __init__.py
│   └── prompts.py           # 提示词模板（消除重复）
├── formatters/
│   ├── __init__.py
│   ├── json_formatter.py    # JSON 输出
│   └── md_formatter.py      # Markdown 输出
├── cli.py                   # CLI 入口（从 generate.py 提取）
├── generate.py              # 保持兼容，主入口委托给 generator
├── prompts.py               # 旧文件，重定向到 templates/
├── config.yaml
├── requirements.txt
└── README.md
```

## prompts.py 重构：参数化模板

当前三个内容类型的模板结构完全相同，只有部分步骤的描述不同。

**解决方案**：提取每种内容类型的差异化描述为字典，主模板用占位符拼接。

```python
STEP_TEMPLATES = {
    "AI工具推荐": {
        "步骤二": "产品速览描述...",
        "步骤四": "核心能力描述...",
        "步骤六": "竞品对比描述...",
    },
    "AI资讯": { ... },
    "开源项目解读": { ... },
}

def build_prompt(content_type: str, topic: str) -> str:
    # 用主模板 + 差异化描述拼接
    ...
```

## generate.py 重构：职责分离

| 文件 | 职责 |
|------|------|
| `generator/api.py` | MiniMax API 调用、重试、超时 |
| `generator/config.py` | YAML 配置加载 |
| `parser/content.py` | parse_content 解析逻辑 |
| `formatters/json_formatter.py` | JSON 输出格式化 |
| `formatters/md_formatter.py` | Markdown 输出格式化 |
| `cli.py` | argparse CLI 参数定义 |

## 日志系统

使用 Python 标准库 `logging`，分级输出到 stdout：

```
[INFO]  开始生成第 1/10 条笔记 (No.1)...
[INFO]  API 调用成功
[WARNING]  第 2 次尝试...
[ERROR]  请求超时
```

- `--verbose` 参数开启 DEBUG 日志
- 默认 INFO 级别

## 兼容性

- `python generate.py` 保持原有 CLI 参数不变
- 输出格式和文件路径不变
- 新模块可独立导入使用

## 实施步骤

1. 创建 `generator/`、`parser/`、`templates/`、`formatters/` 目录
2. 重构 `prompts.py` 为参数化模板
3. 拆解 `generate.py` 到各模块
4. 添加日志系统
5. 验证输出与重构前一致
6. 删除旧 `generate.py` 中的重复代码

## 验证方式

运行原有命令，对比新旧输出：

```bash
python generate.py --topic "Claude Code" --type "AI工具推荐" --num 3
```

diff 输出文件应完全一致。