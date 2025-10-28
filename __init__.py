"""
Excel SKU智能拼接节点
支持从Excel读取SKU分组信息，自动下载图片并拼接
"""

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
__version__ = "1.1.0"
__author__ = "SKU Collage Team"

# 前端扩展在 js/excel_upload.js 中自动加载
# 使用 ComfyUI 标准的文件上传机制