"""AI 科技账号模板实现"""
from .base import BaseTemplate


class AITechTemplate(BaseTemplate):
    """AI 科技博主账号的模板实现"""

    @property
    def name(self) -> str:
        return "ai_tech"

    @property
    def content_types(self) -> list:
        return ["AI资讯", "AI工具推荐", "开源项目解读"]

    # System prompt - defines the AI tech blogger persona (unchanged)
    SYSTEM_PROMPT = """你是一个专注AI领域的科技博主，追踪最前沿的AI动态和技术进展。
你擅长发现和分享有价值的开源项目、好用的工具和行业大新闻。
内容风格：科技感强、新闻敏锐、文笔简洁有力、有独到见解。
排版：分段清晰、干货密集、不堆砌废话。
输出纯文本，不使用emoji符号。
【重要】配图提示词必须用中文撰写，详细描述图片布局、色彩、字体大小和具体内容。
配图提示词中必须包含实际要显示在图片上的具体文字内容。
**关键: 显示文字用双引号""括起来，颜色代码和尺寸数值不加引号**

## 设计规范
- 图片尺寸：1080×1440像素（3:4比例），必须严格遵守
- 配色方案：
  - 背景色：极浅深蓝色 #f0f4f8
  - 主文字色：深蓝色 #1a1a2e
  - 卡片背景：纯白色 #ffffff
  - 标签背景：深蓝色 #1a1a2e
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
- 背景色：浅灰蓝色（参考色值：#f0f4f8）
- 主文字色：深靛蓝色（参考色值：#1a1a2e）
- 卡片背景：白色（参考色值：#ffffff）
- 标签背景：深靛蓝色（参考色值：#1a1a2e）
- 辅助灰：#4a5568（中灰色）、#f7f8fa（浅灰白色）

尺寸：1080×1440像素（3:4比例），必须严格遵守

统一字号规范：
- 主标题（封面大字）：96pt，超大加粗
- 页面标题：40-42pt，加粗
- 副标题：28-36pt
- 正文：24pt
- 说明文字：18-20pt

格式要求：
1. 每张图片必须以"【配图提示词】"开头
2. 每张图片标题格式："步骤一"、"步骤二"、"步骤三"……"步骤八"（注意：必须用中文数字，不能用阿拉伯数字）
3. 每张图片必须包含：背景设置、顶部区域、主体区域、底部区域、整体风格
4. 重要: 要显示在图片上的文字必须用双引号""括起来，例如: 放置文字"从安装到精通"、标题"Claude Code"、副标题"官方编程工具"
5. 所有设计参数（颜色代码、字体大小、像素值、透明度、圆角等）不是显示内容，用括号注明仅供参考：
   - 字体大小：（参考大小：20pt）
   - 像素值：（参考像素：80px）
   - 透明度：（参考透明度：30%）
   - 圆角：（参考圆角：8px）
6. 8张图片必须严格按顺序：步骤一、步骤二、步骤三、步骤四、步骤五、步骤六、步骤七、步骤八，不可缺少任何一步，不可添加额外步骤

【颜色代码格式规则】
- 颜色代码必须跟在颜色名称后面，用括号注明"（参考色值：#XXXXXX）"
- 正确：纯色背景，浅灰蓝色（参考色值：#f0f4f8）
- 错误：纯色背景 #f0f4f8
- 正确：深靛蓝色（参考色值：#1a1a2e），96pt超粗
- 错误：96pt超粗 #1a1a2e深靛蓝色

示例(正确格式):
- 底部放置文字"从安装到精通"，（参考大小：20pt）深靛蓝色，距底部（参考像素：120px）
- 中央显示标题"Claude Code"，（参考大小：96pt）超粗，深靛蓝色（参考色值：#1a1a2e）
- 纯色背景，浅灰蓝色（参考色值：#f0f4f8）
- 圆角矩形背景，深靛蓝色（参考色值：#1a1a2e），（参考圆角：8px）
- 透明度30%，（参考透明度：30%）

示例(错误格式):
- 底部放置"从安装到精通"，使用20pt字体
- 标题"Claude Code"，使用96pt超粗
- 纯色背景，无任何装饰元素
- 透明度30%，距顶部80px"""

    # Body generation prompt
    BODY_SYSTEM_PROMPT = """你是一个专注AI领域的科技博主，擅长写小红书风格的内容。
内容风格：科技感强、新闻敏锐、文笔简洁有力、有独到见解。
排版：分段清晰、干货密集、不堆砌废话。
输出纯文本，不用emoji符号。
根据提供的配图提示词，写出配套的小红书正文。"""

    def build_prompt(self, content_type, topic, note_index=1, material=None):
        """Build a complete user prompt for the given content type and topic."""
        subtitles = self.STEP_SUBTITLES.get(content_type, self.STEP_SUBTITLES["AI工具推荐"])
        step_content = self.STEP_CONTENT.get(content_type, self.STEP_CONTENT["AI工具推荐"])
        step3 = self.STEP3_CONTENT.get(content_type, self.STEP3_CONTENT["AI工具推荐"])

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
                content = self.COMMON_STEPS.get(step_key, "")

            steps.append(f"{step_key}（{subtitle}）：{content}")

        material_section = f"\n\n参考资料：\n{material}\n" if material else ""

        user_prompt = f"""请为「{topic}」生成8张小红书配图提示词。{material_section}

【重要】每张配图提示词必须包含从参考资料中提取的具体内容，不能只描述样式。

每个步骤的内容要求：
- 步骤一（封面）：必须包含主题标题、副标题（从资料中提取的核心亮点）
- 步骤二（产品速览）：必须包含产品名称、版本号、核心功能列表（来自资料）
- 步骤三（数据分析）：必须包含具体数据、指标、数字（来自资料）
- 步骤四（核心能力）：必须包含具体功能名称和能力描述（来自资料）
- 步骤五（使用指南）：必须包含具体命令、参数、步骤编号（来自资料）
- 步骤六（竞品对比）：必须包含对比项名称和具体对比内容（来自资料）
- 步骤七（行业启示）：必须包含具体观点和说明（来自资料）
- 步骤八（账号引导）：固定格式，账号名"AI科技观察"+"关注我，持续追踪AI前沿动态"

{self.STYLE_BLOCK}

{steps[0]}
{steps[1]}
{steps[2]}
{steps[3]}
{steps[4]}
{steps[5]}
{steps[6]}
{steps[7]}"""

        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt
        }

    def build_body_prompt(self, topic, content_type, image_prompts, material=None):
        """Build a prompt for generating Xiaohongshu body text."""
        prompts_text = "\n\n".join([f"步骤{i+1}：{p}" for i, p in enumerate(image_prompts)])

        material_section = f"\n\n参考资料：\n{material}\n" if material else ""

        user_prompt = f"""请为「{topic}」生成小红书正文。

根据以下8条配图提示词的内容，重新组织成按主题分块的小红书正文。{material_section}

要求：
1. 标题：简洁有力，一句话概括核心亮点
2. 开头引入：2-3句话引入话题，吸引读者
3. 内容分块：按主题重新组织（不是严格按步骤顺序），每个分块有标题和2-3句说明
4. 结尾引导：1-2句话引导互动，如"关注我，持续追踪AI前沿动态"
5. 话题标签：3-5个相关话题标签，如 #AI #科技 #人工智能 等
6. 总字数控制在300-500字
7. 输出纯文本，不用emoji

【重要】技术内容必须保留具体细节：
- 命令、代码、路径、参数等要原样保留
- 安装说明要写清楚具体命令，不能只说"用xxx安装"
- 数字、版本号、配置值等要精确

格式：
标题：[标题]
开头：[开头引入]
正文：
[分块1标题]
[分块1内容]
[分块2标题]
[分块2内容]
...
结尾：[结尾引导]
标签：[话题标签，用空格分隔]"""

        return {
            "system": self.BODY_SYSTEM_PROMPT,
            "user": user_prompt
        }