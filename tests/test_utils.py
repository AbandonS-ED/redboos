"""formatters/utils.py 单元测试"""
import pytest
from formatters.utils import fix_nested_parens, fix_shadow_format, fix_format


class TestFixNestedParens:
    """fix_nested_parens 测试"""

    def test_simple_nested_parens_corner_bracket(self):
        """内层外层都是 corner bracket"""
        text = '（参考像素：（参考像素：12px））'
        result = fix_nested_parens(text)
        assert result == '（参考像素：12px）'

    def test_outer_fullwidth_inner_corner_bracket(self):
        """外层全角括号，内层 corner bracket — 修复前的实际输出格式"""
        text = '（参考像素：（参考像素：12px））'
        result = fix_nested_parens(text)
        assert result == '（参考像素：12px）'

    def test_outer_fullwidth_inner_fullwidth(self):
        """外层全角括号，内层也是全角"""
        text = '（参考边距：（参考像素：12px））'
        result = fix_nested_parens(text)
        assert result == '（参考边距：12px）'

    def test_no_nested(self):
        """没有嵌套时直接返回"""
        text = '（参考像素：12px）'
        result = fix_nested_parens(text)
        assert result == '（参考像素：12px）'

    def test_multiple_nested_in_text(self):
        """文本中有多处嵌套"""
        text = '宽度（参考像素：（参考像素：200px）），高度（参考像素：（参考像素：80px））'
        result = fix_nested_parens(text)
        assert '（参考像素：200px）' in result
        assert '（参考像素：80px）' in result
        assert '（参考像素：（参考像素：' not in result

    def test_mixed_pt_px_units(self):
        """不同单位的嵌套"""
        text = '（参考大小：（参考大小：96pt））'
        result = fix_nested_parens(text)
        assert result == '（参考大小：96pt）'


class TestFixShadowFormat:
    """fix_shadow_format 测试"""

    def test_shadow_with_single_nested_px(self):
        """阴影中只有一层嵌套像素"""
        text = '（参考阴影：0 （参考像素：4px） rgba(0,0,0,0.08)）'
        result = fix_shadow_format(text)
        assert result == '（参考阴影：0  4px  rgba(0,0,0,0.08)）'

    def test_shadow_with_double_nested_px(self):
        """阴影中有双层嵌套像素 — 实际生成的问题格式"""
        text = '（参考阴影：0  (参考像素：4px)   (参考像素：(参考像素：16px))  rgba(0,0,0,0.08)）'
        result = fix_shadow_format(text)
        assert '4px' in result
        assert '16px' in result
        assert '（参考像素：' not in result

    def test_shadow_normal_format(self):
        """阴影已经是正常格式"""
        text = '（参考阴影：0 4px 16px rgba(0,0,0,0.08)）'
        result = fix_shadow_format(text)
        assert result == '（参考阴影：0 4px 16px rgba(0,0,0,0.08)）'

    def test_no_shadow(self):
        """没有阴影时直接返回"""
        text = '（参考像素：12px）'
        result = fix_shadow_format(text)
        assert result == '（参考像素：12px）'


class TestFixFormat:
    """fix_format 完整流程测试"""

    def test_nested_parens_gets_fixed(self):
        """嵌套括号在 fix_format 中被修复"""
        text = '（参考像素：（参考像素：12px））'
        result = fix_format(text)
        assert result == '（参考像素：12px）'

    def test_shadow_with_nested_px_gets_fixed(self):
        """阴影中的嵌套像素在 fix_format 中被修复"""
        text = '（参考阴影：0 （参考像素：4px） （参考像素：16px） rgba(0,0,0,0.08)）'
        result = fix_format(text)
        assert '4px' in result
        assert '16px' in result
        assert '（参考像素：' not in result

    def test_existing_ref_not_re_wrapped(self):
        """已有的参考格式不会再被包装"""
        text = '（参考像素：12px）'
        result = fix_format(text)
        assert result == '（参考像素：12px）'

    def test_naked_pt_gets_wrapped(self):
        """裸的 pt 值被包装"""
        text = '宽度12pt'
        result = fix_format(text)
        assert '（参考大小：12pt）' in result

    def test_naked_px_gets_wrapped(self):
        """裸的 px 值被包装"""
        text = '宽度200px'
        result = fix_format(text)
        assert '（参考像素：200px）' in result

    def test_protected_ref_preserved(self):
        """保护机制：已有的参考值不会被裸值包装规则影响"""
        text = '（参考像素：12px）'
        result = fix_format(text)
        assert result == '（参考像素：12px）'
        # 确认没有被变成 （参考像素：（参考像素：12px））
        assert '（参考像素：（' not in result

    def test_shadow_output_not_re_wrapped(self):
        """fix_shadow_format 输出的阴影不会被后续裸值规则重新包装"""
        text = '（参考阴影：0 4px 16px rgba(0,0,0,0.08)）'
        result = fix_format(text)
        # 应该保持原样，不变成（参考像素：4px）等
        assert '4px' in result
        assert '（参考像素：4px）' not in result

    def test_complex_mixed_case(self):
        """混合多种格式的复杂文本"""
        text = ('宽度（参考像素：（参考像素：200px）），'
                '阴影（参考阴影：0 （参考像素：4px） （参考像素：16px） rgba(0,0,0,0.08)），'
                '（参考像素：12px）')
        result = fix_format(text)
        assert '（参考像素：200px）' in result
        assert '（参考像素：4px）' not in result
        assert '（参考像素：12px）' in result
        assert '（参考像素：（参考像素：' not in result