"""公共格式化工具"""
import re


def fix_format(text: str) -> str:
    """修复格式：把裸的 pt/px 值包装成 (参考大小：NNpt) 格式
    只处理完全裸的值，不处理已有 (参考xxx：NN) 格式的值
    """
    # 先把已有的 (参考xxx：NNpt) 形式的值标记出来，避免重复匹配
    protected = {}
    counter = [0]

    def protect(match):
        key = f"__PROTECTED_{counter[0]}__"
        protected[key] = match.group(0)
        counter[0] += 1
        return key

    # 保护已有格式
    text = re.sub(r'（参考[^）]+：\d+pt）', protect, text)
    text = re.sub(r'（参考[^）]+：\d+px）', protect, text)

    # 现在处理裸的 pt/px
    text = re.sub(r'(\d+)pt', r'(参考大小：\1pt)', text)
    text = re.sub(r'(\d+)px', r'(参考像素：\1px)', text)

    # 还原被保护的值
    for key, val in protected.items():
        text = text.replace(key, val)

    return text