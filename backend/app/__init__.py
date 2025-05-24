# -*- coding: utf-8 -*-
"""
Flask应用工厂模式
创建和配置Flask应用实例
"""

from flask import Flask
from flask_cors import CORS
import os
import logging
from logging.handlers import RotatingFileHandler


def create_app(config_name='default'):
    """
    应用工厂函数

    Args:
        config_name (str): 配置名称

    Returns:
        Flask: 配置好的Flask应用实例
    """
    app = Flask(__name__,
                template_folder='../../frontend',
                static_folder='../../frontend/dist')

    # 加载配置
    from .config import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 初始化扩展
    CORS(app)

    # 注册蓝图
    try:
        from .api import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
    except ImportError as e:
        app.logger.warning(f"API蓝图导入失败: {e}")

    # 注册主路由
    try:
        from .main import main_bp
        app.register_blueprint(main_bp)
    except ImportError as e:
        app.logger.warning(f"主蓝图导入失败: {e}")

    # 配置日志
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/gemini_app.log',
                                         maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Gemini Image App startup')

    return app
