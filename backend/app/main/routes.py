# -*- coding: utf-8 -*-
"""
主路由模块
处理页面渲染和基本路由
"""

from flask import send_from_directory, current_app
from . import main_bp
import os


@main_bp.route('/')
def index():
    """主页路由 - 服务Vue应用"""
    # 服务Vue应用的index.html
    frontend_dir = os.path.join(current_app.root_path, '../../frontend')
    return send_from_directory(frontend_dir, 'index.html')


@main_bp.route('/<path:path>')
def serve_vue_app(path):
    """服务Vue应用的静态文件和路由"""
    frontend_dir = os.path.join(current_app.root_path, '../../frontend')

    # 如果是静态文件，直接服务
    if path.startswith('src/') or path.startswith('assets/') or path.endswith('.js') or path.endswith('.css') or path.endswith('.png') or path.endswith('.jpg') or path.endswith('.ico'):
        try:
            return send_from_directory(frontend_dir, path)
        except:
            pass

    # 对于Vue路由，返回index.html让Vue Router处理
    return send_from_directory(frontend_dir, 'index.html')


@main_bp.route('/storage/<path:filename>')
def serve_storage_files(filename):
    """服务存储目录中的文件"""
    storage_dir = os.path.join(current_app.root_path, '../../storage')
    return send_from_directory(storage_dir, filename)


@main_bp.route('/health')
def health_check():
    """健康检查接口"""
    return {
        'status': 'healthy',
        'message': 'Gemini Image App is running'
    }
