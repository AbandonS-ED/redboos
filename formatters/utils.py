"""公共格式化工具"""
import re


def fix_nested_parens(text: str) -> str:
    """修复嵌套括号：把（参考xxx：（参考yyy：NNpt））这种嵌套结构拍平

    规则：
    - 参考像素/参考大小/参考透明度/参考圆角/参考间距 等只接受数值，
      不能嵌套另一个参考表达式
    - 例如：（参考边距：（参考像素：12px））→（参考边距：12px）
    """
    # 匹配外层（参考xxx：...）且内层包含（参考yyy：数值单位）的结构
    # 只保留内层数值
    # 支持两种括号：corner bracket （U+3008/3009）和 fullwidth parenthesis （U+FF08/FF09）
    pattern = r'[（\(]参考([^：]+)：[（\(]参考([^：]+)：(\d+)(px|pt|%)[）\)][）\)]'
    text = re.sub(pattern, r'（参考\1：\3\4）', text)
    return text


def fix_shadow_format(text: str) -> str:
    """修复阴影格式：处理阴影值中的嵌套（参考像素：NNpx）引用

    阴影应该是：（参考阴影：0 4px 20px rgba(...)）
    而非：（参考阴影：0（参考像素：4px）（参考像素：20px）rgba(...)）
    """
    if '参考阴影：' not in text:
        return text

    def replace_shadow_parts(m):
        full = m.group(0)
        # 直接把所有嵌套的（参考像素：NNpx）或(参考像素：NNpx)替换为" 数值px "格式
        inner = re.sub(r'[（\(]参考像素：(\d+)px[）\)]', r' \1px ', full)
        return inner

    # 匹配（参考阴影：...rgba(...))）整体，处理其中的像素引用
    # 使用非贪婪匹配，找到 rgba(...)) 然后向前找（参考阴影：
    text = re.sub(r'[（\(]参考阴影：.+?rgba\([^)]+\)[）\)]', replace_shadow_parts, text)
    return text


def fix_format(text: str) -> str:
    """修复格式：把裸的 pt/px 值包装成 (参考大小：NNpt) 格式
    只处理完全裸的值，不处理已有 (参考xxx：NN) 格式的值
    """
    # 先修复嵌套括号（防止内外层互相干扰）
    text = fix_nested_parens(text)

    # 修复阴影格式（只在有阴影引用时才处理）
    text = fix_shadow_format(text)

    # 先把已有的 (参考xxx：NNpt) 形式的值标记出来，避免重复匹配
    protected = {}
    counter = [0]

    def protect(match):
        key = f"__PROTECTED_{counter[0]}__"
        protected[key] = match.group(0)
        counter[0] += 1
        return key

    # 保护已有格式（支持 corner bracket 和 fullwidth parenthesis）
    text = re.sub(r'[（\(]参考[^）]+：\d+pt[）\)]', protect, text)
    text = re.sub(r'[（\(]参考[^）]+：\d+px[）\)]', protect, text)

    # 保护阴影格式的输出（fix_shadow_format 后的纯数值形式）
    text = re.sub(r'（参考阴影：[^）]+）', protect, text)

    # 现在处理裸的 pt/px，用全角括号替换
    text = re.sub(r'(\d+)pt', r'（参考大小：\1pt）', text)
    text = re.sub(r'(\d+)px', r'（参考像素：\1px）', text)

    # 还原被保护的值
    for key, val in protected.items():
        text = text.replace(key, val)

    return text
