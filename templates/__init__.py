"""模板系统"""
from .ai_tech import AITechTemplate

TEMPLATES = {
    "ai_tech": AITechTemplate(),
}


def get_template(name: str):
    """获取指定名称的模板，不存在则报错"""
    if name not in TEMPLATES:
        raise ValueError(f"Unknown template: {name}. Available: {list(TEMPLATES.keys())}")
    return TEMPLATES[name]


__all__ = ["get_template", "TEMPLATES", "AITechTemplate"]