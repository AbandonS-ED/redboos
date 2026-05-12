# 小红书AI科技博主内容生成工具

使用 MiniMax API 批量生成小红书科技博主的配图提示词与正文文案。支持 AI工具推荐、AI资讯、开源项目解读三种内容类型，每条笔记生成 8 张配图的详细提示词 + 配套正文。

## 特性

- **批量生成** - 支持指定数量、起始编号、请求间隔
- **三种内容类型** - AI工具推荐、AI资讯、开源项目解读
- **自动匹配资料** - 根据主题自动从 `zhiliao/` 目录匹配参考资料
- **模糊匹配** - 文件名与主题模糊对应，无需精确匹配
- **双输出格式** - 支持 JSON 和 Markdown 两种输出
- **8步配图体系** - 封面 → 产品介绍 → 数据分析 → 能力分析 → 使用指南 → 竞品对比 → 行业启示 → 账号引导
- **可配置生图** - 通过 `image_api.enabled` 开关控制是否调用 MiniMax 生图 API，默认关闭
- **单元测试** - 15 个测试覆盖解析函数，修改代码时自动验证功能完整

## 安装

```bash
git clone https://github.com/AbandonS-ED/redboos.git
cd xiaohongshu-ai
pip install -r requirements.txt
pip install pytest  # 用于运行测试
```

## 配置

复制配置文件模板并填入你的 MiniMax API Key：

```bash
cp config.yaml.example config.yaml
# 编辑 config.yaml，填入 api_key
```

```yaml
# config.yaml
api_key: "YOUR_API_KEY_HERE"
api_url: "https://api.minimax.chat/v1/text/chatcompletion_v2"
model: "MiniMax-M2.7"
temperature: 0.8
max_tokens: 16384
timeout: 120  # 请求超时时间（秒）

# 生图功能（默认关闭，升级套餐后设为 true 开启）
image_api:
  enabled: false
  api_key: "YOUR_API_KEY_HERE"
  api_url: "https://api.minimaxi.com/v1/image_generation"
  model: "image-01"
  aspect_ratio: "3:4"
```

获取 API Key：[MiniMax 开放平台](https://platform.minimax.chat/user-center/basic-information/interface-key)

## 使用方法

### 基本命令

```bash
# 生成10条AI工具推荐（默认）
python cli.py --topic "Claude Code" --type "AI工具推荐"

# 生成5条AI资讯
python cli.py --num 5 --topic "DeepSeek V4" --type "AI资讯"

# 指定起始编号（从第11条开始）
python cli.py --num 10 --topic "OpenAI Codex" --type "AI工具推荐" --start-no 11

# 指定参考资料文件
python cli.py --topic "DeepSeek融资" --material ../zhiliao/DeepSeek融资500亿.md
```

### 参数说明

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--num` | 否 | 1 | 生成数量 |
| `--topic` | 是 | - | 笔记主题 |
| `--type` | 否 | AI工具推荐 | 内容类型：`AI工具推荐`、`AI资讯`、`开源项目解读` |
| `--format` | 否 | both | 输出格式：`json`、`md`、`both` |
| `--material` | 否 | 自动匹配 | 参考资料文件路径 |
| `--delay` | 否 | 1.0 | 请求间隔（秒），避免 API 限流 |
| `--start-no` | 否 | 1 | 起始编号，连续生成时递增 |
| `--output` | 否 | output | 输出目录 |
| `--config` | 否 | config.yaml | 配置文件路径 |
| `--verbose` | 否 | False | 显示详细日志 |
| `--template` | 否 | ai_tech | 模板名称 |

### 内容类型说明

| 类型 | 适用场景 |
|------|----------|
| `AI工具推荐` | 好用的AI工具、网站、浏览器插件等 |
| `AI资讯` | 大模型动态、行业新闻、技术突破 |
| `开源项目解读` | GitHub开源项目分析、技术架构解读 |

### 自动匹配参考资料

不指定 `--material` 时，工具会自动从上级 `zhiliao/` 目录匹配文件：

```bash
# 主题"Claude Code"会匹配 zhiliao/Claude_Code_资料.md
python cli.py --topic "Claude Code" --type "AI工具推荐"

# 主题"OpenAI Codex"会匹配 zhiliao/OpenAI_Codex_资料.md
python cli.py --topic "OpenAI Codex" --type "AI工具推荐"
```

匹配规则：去除空格和下划线后模糊匹配，匹配到多个文件时报错退出避免歧义。

### 运行测试

```bash
pytest tests/ -v
```

## 输出示例

生成的文件保存在 `output/` 目录下，文件名格式：`xiaohongshu_{主题}_{时间戳}.json` 或 `.md`

### Markdown 输出结构

```markdown
# DeepSeek融资500亿：23天估值涨5倍背后的行业变局

## 开头

一家曾坚持"不融资、不商业化、不路演"的AI公司，今天官宣500亿融资...

## 正文

### 融资规模超预期
500亿人民币的融资额，515亿美元的估值...

### 商业化不是选择题
...

## 结尾
关注我，持续追踪AI前沿动态。

**标签**: #AI #人工智能 #大模型 #科技投资 #DeepSeek

---

# 配图提示词

### 图片1
【配图提示词】步骤一：封面震撼数据
背景设置：极浅深蓝色 #f0f4f8...
...
```

### JSON 输出结构

```json
{
  "index": 1,
  "topic": "DeepSeek融资500亿",
  "type": "AI资讯",
  "body": {
    "title": "DeepSeek融资500亿：23天估值涨5倍背后的行业变局",
    "intro": "一家曾坚持"不融资、不商业化、不路演"的AI公司...",
    "sections": [
      {"title": "融资规模超预期", "content": "500亿人民币的融资额..."},
      ...
    ],
    "tags": ["#AI", "#人工智能", "#大模型", "#科技投资", "#DeepSeek"],
    "closing": "关注我，持续追踪AI前沿动态。"
  },
  "image_prompts": [
    "【配图提示词】步骤一：封面震撼数据\n背景设置：...",
    "【配图提示词】步骤二：...\n..."
  ]
}
```

## 配图提示词设计规范

每条笔记生成 8 张图的提示词，严格遵循统一规范：

| 元素 | 规范 |
|------|------|
| 图片尺寸 | 1080×1440像素（3:4比例） |
| 背景色 | #f0f4f8 极浅深蓝色 |
| 主文字色 | #1a1a2e 深蓝色 |
| 卡片背景 | #ffffff 纯白色 |
| 标签背景 | #1a1a2e 深蓝色，白色文字 |
| 主标题 | 96pt 超大加粗 |
| 页面标题 | 40-42pt 加粗 |
| 副标题 | 28-36pt |
| 正文 | 24pt |
| 说明文字 | 18-20pt |
| 账号名 | AI科技观察 |

### 设计参数格式

所有设计参数（颜色代码、字体大小、像素值、透明度、圆角等）必须用括号注明为"仅供参考"，严禁在生成的图片中渲染显示：

| 参数类型 | 正确格式 | 错误格式 |
|---------|---------|---------|
| 颜色 | 浅灰蓝色（参考色值：#f0f4f8） | 浅灰蓝色 #f0f4f8 |
| 字号 | （参考大小：20pt） | 20pt |
| 像素 | （参考像素：80px） | 80px |
| 透明度 | （参考透明度：30%） | 透明度30% |
| 圆角 | （参考圆角：8px） | 圆角8px |

### 每张图片后的声明

生成时每张图片会统一添加声明：

> 【重要声明】：每张图片提示词中的所有设计参数（包括但不限于十六进制颜色代码、字体大小、像素值、透明度、圆角等）仅供设计参考用途，严禁在生成的图片中渲染显示。图片尺寸：1080×1440像素（3:4比例），必须严格遵守。

### 8张图的逻辑线：
1. **封面** - 震撼数据引入
2. **步骤二** - 新闻要点 / 产品速览
3. **步骤三** - 数据分析
4. **步骤四** - 背景解读 / 核心能力
5. **步骤五** - 使用指南
6. **步骤六** - 竞品对比
7. **步骤七** - 影响展望 / 行业启示
8. **步骤八** - 账号引导总结

## 项目结构

```
xiaohongshu-ai/
├── cli.py                    # CLI 入口
├── generate.py               # 兼容主入口（调用 cli.py）
├── generator/
│   ├── api.py               # MiniMax API 调用封装
│   ├── client.py            # 主编排生成流程
│   ├── config.py            # 配置文件加载
│   └── image_api.py        # MiniMax 生图 API 调用
├── parser/
│   └── content.py           # 解析 API 响应，提取提示词和文案
├── templates/
│   ├── base.py              # 模板抽象基类
│   ├── ai_tech.py           # AI 科技博主模板实现
│   └── __init__.py          # 模板注册表
├── formatters/
│   ├── json_fmt.py          # JSON 输出格式化
│   ├── md_fmt.py            # Markdown 输出格式化
│   └── utils.py             # 格式修复工具
├── tests/
│   ├── test_parse_content.py  # parse_content 单元测试
│   └── test_parse_body.py    # parse_body 单元测试
├── templates/               # 提示词模板目录
├── output/                  # 生成文件输出目录
├── config.yaml              # 配置文件（含 API Key）
├── config.yaml.example      # 配置模板
└── requirements.txt         # Python 依赖
```

## 常见问题

### API 调用失败

1. 检查 API Key 是否正确
2. 检查网络连接
3. 确认 API 余额充足
4. 尝试增加 `--delay` 参数避免限流

### 生图功能无法使用

1. 确认 `config.yaml` 中 `image_api.enabled` 已设为 `true`
2. 确认 Token Plan 支持生图功能（Starter 套餐可能不支持）
3. 生图功能每周限额，月末会重置

### 参考资料匹配失败

1. 确认 `zhiliao/` 目录位于项目上级目录
2. 检查文件名是否包含主题关键词
3. 使用 `--material` 手动指定文件路径

### 中文乱码

确保使用 UTF-8 编码打开文件。Markdown 文件用任意文本编辑器或 VS Code 打开即可。

## 依赖

- Python 3.8+
- requests >= 2.28.0
- PyYAML >= 6.0
- pytest >= 7.0（测试可选）

## 许可

MIT License