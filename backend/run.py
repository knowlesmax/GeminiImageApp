#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini图像处理应用启动文件
"""

import os
import sys
import socket

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app


def find_available_port(start_port, max_attempts=10):
    """查找可用端口，如果被占用则递增重试"""
    port = start_port

    for attempt in range(max_attempts):
        try:
            # 尝试绑定端口检查是否可用
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', port))
            sock.close()
            return port
        except OSError:
            if attempt == 0:
                print(f"⚠️  端口 {port} 被占用，尝试端口 {port + 1}")
            else:
                print(f"⚠️  端口 {port} 被占用，尝试端口 {port + 1}")
            port += 1

    raise Exception(f"无法找到可用端口 (尝试范围: {start_port}-{start_port + max_attempts - 1})")


if __name__ == '__main__':
    print(f"🚀 启动Gemini图像处理应用...", flush=True)

    # 配置参数
    start_port = int(os.environ.get('PORT', 5005))
    host = os.environ.get('HOST', '0.0.0.0')

    try:
        # 查找可用端口
        port = find_available_port(start_port)
        print(f"📍 访问地址: http://{host}:{port}", flush=True)

        # 创建应用实例
        app = create_app(os.getenv('FLASK_ENV', 'development'))
        debug_mode = app.config.get('DEBUG', True)

        print(f"📊 调试模式: {'开启' if debug_mode else '关闭'}", flush=True)
        print(f"🔧 开始启动服务器...", flush=True)

        # 启动服务器
        app.run(
            host=host,
            port=port,
            debug=debug_mode,
            threaded=True,
            use_reloader=False  # 禁用重载器避免问题
        )

    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
