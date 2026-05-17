"""自定义异常"""


class OpenCodeError(Exception):
    """基础异常"""
    pass


class ConfigError(OpenCodeError):
    """配置错误"""
    pass


class APIError(OpenCodeError):
    """API 调用错误"""
    pass


class MaterialNotFoundError(OpenCodeError):
    """参考资料未找到"""
    pass


class MaterialAmbiguousError(OpenCodeError):
    """参考资料匹配歧义（多个候选）"""
    pass