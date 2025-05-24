# -*- coding: utf-8 -*-
"""
主蓝图模块
处理主要的页面路由
"""

from flask import Blueprint

# 创建主蓝图
main_bp = Blueprint('main', __name__)

# 导入路由
from . import routes
