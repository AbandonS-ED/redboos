"""小红书AI内容生成工具 - 兼容主入口

此文件保留向后兼容，新代码请使用 cli.py
"""
import sys
import os

# 将 cli.py 的主逻辑导入到 generate.py 命名空间
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import main

if __name__ == "__main__":
    main()