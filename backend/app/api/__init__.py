# -*- coding: utf-8 -*-
"""
API蓝图模块
包含所有API路由的注册
"""

from flask import Blueprint

# 创建API蓝图
api_bp = Blueprint('api', __name__)

# 导入所有API路由
try:
    from . import image_qa
    from . import image_generation
    from . import image_editing
    from . import object_detection
    from . import image_segmentation
    from . import video_generation
    from . import utils
except ImportError as e:
    # 如果某些模块导入失败，记录错误但不中断应用启动
    import logging
    logging.warning(f"API模块导入失败: {e}")
