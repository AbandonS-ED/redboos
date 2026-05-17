"""常量定义"""

IMAGE_COUNT = 8

IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1440
IMAGE_ASPECT_RATIO = "3:4"

BG_COLOR = "#f0f4f8"
TEXT_COLOR = "#1a1a2e"
CARD_BG_COLOR = "#ffffff"
TAG_BG_COLOR = "#1a1a2e"
AUX_GRAY = "#4a5568"
LIGHT_GRAY = "#f7f8fa"

FONT_TITLE = 96
FONT_PAGE_TITLE = 40
FONT_SUBTITLE = 32
FONT_BODY = 24
FONT_CAPTION = 18

MAX_RETRIES = 3
DEFAULT_TIMEOUT = 120
DEFAULT_DELAY = 1.0
DEFAULT_TEMPERATURE = 0.8
DEFAULT_MAX_TOKENS = 16384

CONTENT_TYPES = ["AI资讯", "AI工具推荐", "开源项目解读"]

NOTE_TITLE_MAX_LEN = 15

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

IMAGEPROMPT_NOTICE = ("【重要声明】：每张图片提示词中的所有设计参数（包括但不限于十六进制颜色代码、字体大小、像素值、透明度、圆角等）"
                      "仅供设计参考用途，严禁在生成的图片中渲染显示。图片尺寸：1080×1440像素（3:4比例），必须严格遵守。")