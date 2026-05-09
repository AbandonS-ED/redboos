# 小红书AI科技博主内容生成工具

使用 MiniMax API 批量生成小红书科技博主内容，支持 AI工具推荐、AI资讯、开源项目解读三种内容类型。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置文件

编辑 `config.yaml`，填入你的 MiniMax API Key：

```yaml
api_key: "your-api-key-here"
api_url: "https://api.minimax.chat/v1/text/chatcompletion_v2"
model: "MiniMax-M2.7"
temperature: 0.8
max_tokens: 2048
```

## 使用方法

### 基本用法

```bash
# 生成10条AI工具推荐
python generate.py --num 10 --topic "CodeX" --type "AI工具推荐" --start-no 1

# 生成5条AI资讯
python generate.py --num 5 --topic "最新AI大模型动态" --type "AI资讯" --start-no 11

# 生成3条开源项目解读
python generate.py --num 3 --topic "有趣的GitHub开源项目" --type "开源项目解读" --start-no 16
```

### 参数说明

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--num` | 否 | 10 | 生成数量 |
| `--topic` | 是 | - | 笔记主题 |
| `--type` | 否 | AI工具推荐 | 内容类型 |
| `--format` | 否 | both | 输出格式：json, md, both |
| `--delay` | 否 | 1.0 | 请求间隔（秒） |
| `--start-no` | 否 | 1 | 起始编号（如：--start-no 12 则从 No.12 开始） |
| `--output` | 否 | output | 输出目录 |

### 内容类型

- `AI工具推荐` - 好用的AI工具、网页、开源项目
- `AI资讯` - AI大新闻和科技动态
- `开源项目解读` - GitHub开源项目介绍

## 输出示例

每条笔记包含：
- 编号（每天了解一个AI产品 No.XX）
- 标题（简洁有力）
- 正文（结构清晰）
- 话题标签（3-5个）
- 配图提示词（5张图片：1封面 + 3内容 + 1结尾）

## 输出文件

生成的文件保存在 `output/` 目录下：
- `xiaohongshu_主题_时间戳.json`
- `xiaohongshu_主题_时间戳.md`

## 常见问题

### API 调用失败

检查：
1. API Key 是否正确
2. 网络连接是否正常
3. API 余额是否充足

### 中文乱码

确保使用 UTF-8 编码打开文件