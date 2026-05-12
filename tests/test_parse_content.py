"""parse_content() 单元测试"""
import pytest
from parser.content import parse_content


class TestParseContent:
    """测试配图提示词解析"""

    def test_standard_8_steps(self):
        """标准输出：AI 按 markdown 格式返回 8 条提示词"""
        content = """【配图提示词】
## 步骤一（封面）：
极浅深蓝背景，中央大标题

## 步骤二（产品速览）：
三个特性卡片

## 步骤三（数据分析）：
数据统计卡片

## 步骤四（核心能力）：
能力说明

## 步骤五（使用指南）：
使用步骤

## 步骤六（竞品对比）：
对比表格

## 步骤七（行业启示）：
观点卡片

## 步骤八（账号引导）：
账号名+引导"""
        result = parse_content(content)
        assert len(result["image_prompts"]) == 8
        assert "步骤一" in result["image_prompts"][0]
        assert "步骤八" in result["image_prompts"][7]

    def test_extra_steps_truncated_to_8(self):
        """边界情况：返回多余内容，应截断到 8 条"""
        content = """【配图提示词】
步骤一：内容1
步骤二：内容2
步骤三：内容3
步骤四：内容4
步骤五：内容5
步骤六：内容6
步骤七：内容7
步骤八：内容8
步骤九：内容9
步骤十：内容10"""
        result = parse_content(content)
        assert len(result["image_prompts"]) == 8
        assert "步骤九" not in str(result["image_prompts"])

    def test_missing_steps(self):
        """边界情况：返回不足 8 条，应正常返回"""
        content = """【配图提示词】
步骤一：内容1
步骤二：内容2
步骤三：内容3"""
        result = parse_content(content)
        assert len(result["image_prompts"]) == 3

    def test_empty_input(self):
        """空输入"""
        result = parse_content("")
        assert result["image_prompts"] == []

    def test_none_input(self):
        """None 输入"""
        result = parse_content(None)
        assert result["image_prompts"] == []

    def test_mixed_format_with_bold_markers(self):
        """混合格式：包含 ** 包裹的标题"""
        content = """**【配图提示词】**
**步骤一（封面）：**
极浅深蓝背景

**步骤二（产品速览）：**
三个特性卡片"""
        result = parse_content(content)
        assert len(result["image_prompts"]) >= 2

    def test_skip_markdown_headers(self):
        """跳过 markdown 标题行（如 ### xxx）"""
        content = """### 标题
## 步骤一（封面）：
内容1
### 其他标题
## 步骤二（产品速览）：
内容2"""
        result = parse_content(content)
        # 应跳过 ### 和 ## 标题行，只保留步骤内容
        assert "内容1" in str(result["image_prompts"])