"""Prompt templates for Xiaohongshu AI Tech content generation - Parameterized version"""

# System prompt - defines the AI tech blogger persona (unchanged)
SYSTEM_PROMPT = """你是一个专注AI领域的科技博主，追踪最前沿的AI动态和技术进展。
你擅长发现和分享有价值的开源项目、好用的工具和行业大新闻。
内容风格：科技感强、新闻敏锐、文笔简洁有力、有独到见解。
排版：分段清晰、干货密集、不堆砌废话。
输出纯文本，不使用emoji符号。
【重要】配图提示词必须用中文撰写，详细描述图片布局、色彩、字体大小和具体内容。
配图提示词中必须包含实际要显示在图片上的具体文字内容。

## 设计规范
- 图片比例：3:4 竖版（1080×1440像素），小红书信息流最佳展示
- 配色方案：
  - 背景色：极浅深蓝色 #f0f4f8
  - 主文字色：深蓝色 #1a1a2e
  - 卡片背景：纯白色 #ffffff
  - 标签背景：深蓝色 #1a1a2e，白色文字
- 文字层级：主标题96pt > 页面标题40-42pt > 副标题28-36pt > 正文24pt > 说明文字18-20pt
- 留白原则：元素间保持充足空间，呼吸感强
- 账号名统一为"AI科技观察"或根据主题调整
- 所有图片风格必须保持绝对统一"""

# Step subtitles that differ by content type
STEP_SUBTITLES = {
    "AI资讯": {
        "步骤二": "新闻要点",
        "步骤四": "背景解读",
        "步骤六": "影响展望",
        "步骤七": "趋势预测",
    },
    "AI工具推荐": {
        "步骤二": "产品速览",
        "步骤四": "核心能力",
        "步骤六": "竞品对比",
        "步骤七": "行业启示",
    },
    "开源项目解读": {
        "步骤二": "项目简介",
        "步骤四": "核心特性",
        "步骤六": "竞品对比",
        "步骤七": "应用场景",
    },
}

# Step content templates - steps that differ by content type
STEP_CONTENT = {
    "AI资讯": {
        "步骤二": "[新闻要点图，极浅深蓝背景，标题+新闻摘要+关键信息两段式布局]",
        "步骤四": "[背景解读图，极浅深蓝背景，事件背景+相关数据+影响说明三段式]",
        "步骤六": "[影响展望图，极浅深蓝背景，表格或卡片式多列对比]",
        "步骤七": "[趋势预测图，极浅深蓝背景，三个观点卡片]",
    },
    "AI工具推荐": {
        "步骤二": "[产品介绍图，极浅深蓝背景，标题+标签+正文两段式布局]",
        "步骤四": "[能力介绍图，极浅深蓝背景，三个能力卡片纵向排列]",
        "步骤六": "[竞品对比图，极浅深蓝背景，表格或卡片式多列对比]",
        "步骤七": "[行业启示图，极浅深蓝背景，三个观点卡片]",
    },
    "开源项目解读": {
        "步骤二": "[项目介绍图，极浅深蓝背景，标题+项目定位+通俗解释两段式布局]",
        "步骤四": "[功能说明图，极浅深蓝背景，三个特性卡片纵向排列]",
        "步骤六": "[竞品对比图，极浅深蓝背景，表格或卡片式多列对比]",
        "步骤七": "[应用场景图，极浅深蓝背景，三个应用场景卡片]",
    },
}

# Common step content - identical across all content types
COMMON_STEPS = {
    "步骤一": "[小红书风格封面图，竖版3:4比例。极浅深蓝背景，中央大标题，副标题，账号信息]",
    "步骤三": None,  # Uses computed content based on type
    "步骤五": "[使用指南图，极浅深蓝背景，参数区+带编号的步骤列表]",
    "步骤八": "[账号引导图，极浅深蓝背景或纯白，账号名+座右铭+关注引导]",
}

# Step 3 content differs per type (uses different data metrics labels)
STEP3_CONTENT = {
    "AI资讯": "[数据分析图，极浅深蓝到白色渐变背景，三个数据统计卡片]",
    "AI工具推荐": "[数据分析图，极浅深蓝到白色渐变背景，三个数据统计卡片]",
    "开源项目解读": "[数据分析图，极浅深蓝到白色渐变背景，三个数据指标卡片]",
}

# Shared style and format requirements
STYLE_BLOCK = """风格要求：语言自然，像真实的设计需求文档。使用统一的色彩系统和结构化描述。
每张图片提示词必须包含：背景设置、顶部区域、主体区域、底部区域、整体风格。

统一色系：
- 背景色：极浅深蓝色 #f0f4f8
- 主文字色：深蓝色 #1a1a2e
- 卡片背景：纯白色 #ffffff
- 标签背景：深蓝色 #1a1a2e

统一字号规范：
- 主标题（封面大字）：96pt，超大加粗
- 页面标题：40-42pt，加粗
- 副标题：28-36pt
- 正文：24pt
- 说明文字：18-20pt

格式要求：
1. 每张图片以"【配图提示词】"开头
2. 每张图片标注"步骤X（图片主题）："
3. 各部分用分段描述：背景设置、顶部区域、主体区域、底部区域、整体风格
4. 必须包含实际要显示在图片上的具体文字内容"""

def build_prompt(content_type, topic, note_index=1):
    """Build a complete user prompt for the given content type and topic.

    Args:
        content_type: One of "AI资讯", "AI工具推荐", "开源项目解读"
        topic: The topic to generate prompts for
        note_index: Note number (starting from 1, default 1)

    Returns:
        Dict with "system" and "user" keys
    """
    subtitles = STEP_SUBTITLES.get(content_type, STEP_SUBTITLES["AI工具推荐"])
    step_content = STEP_CONTENT.get(content_type, STEP_CONTENT["AI工具推荐"])
    step3 = STEP3_CONTENT.get(content_type, STEP3_CONTENT["AI工具推荐"])

    # Build step lines
    steps = []
    for i in range(1, 9):
        step_key = f"步骤{i}"
        subtitle = subtitles.get(step_key, "")

        # Determine step content
        if step_key == "步骤三":
            content = step3
        elif step_key in step_content:
            content = step_content[step_key]
        else:
            content = COMMON_STEPS.get(step_key, "")

        steps.append(f"{step_key}（{subtitle}）：{content}")

    user_prompt = f"""请为「{topic}」生成8张小红书配图提示词。

{STYLE_BLOCK}

{steps[0]}
{steps[1]}
{steps[2]}
{steps[3]}
{steps[4]}
{steps[5]}
{steps[6]}
{steps[7]}"""

    return {
        "system": SYSTEM_PROMPT,
        "user": user_prompt
    }


# Content types list
CONTENT_TYPES = ["AI资讯", "AI工具推荐", "开源项目解读"]

# Backward-compatible USER_PROMPTS - generated on demand
def _generate_user_prompts():
    """Lazily generate USER_PROMPTS dict for backward compatibility."""
    prompts = {}
    for content_type in CONTENT_TYPES:
        prompts[content_type] = build_prompt(content_type, "{topic}")
    return prompts

USER_PROMPTS = _generate_user_prompts()