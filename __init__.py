"""
Excel SKU智能拼接节点
支持从Excel读取SKU分组信息，自动下载图片并拼接
"""

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# 导入服务器路由（自动注册上传端点）
try:
    from . import server
    print("✅ Excel SKU Loader 服务器模块已加载")
except Exception as e:
    print(f"⚠️ Excel SKU Loader 服务器模块加载失败: {e}")

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
__version__ = "1.1.0"
__author__ = "SKU Collage Team"