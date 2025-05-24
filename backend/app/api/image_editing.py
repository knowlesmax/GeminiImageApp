# -*- coding: utf-8 -*-
"""
图像编辑API模块
处理图像编辑相关的API请求
"""

from flask import request, jsonify, current_app
from . import api_bp


def get_image_editing_service():
    """获取图像编辑服务实例"""
    try:
        from ..services.image_editing_service import ImageEditingService
        from ..utils.helpers import init_gemini_client
        client = init_gemini_client()
        return ImageEditingService(client)
    except Exception as e:
        current_app.logger.error(f"初始化图像编辑服务失败: {e}")
        return None


@api_bp.route('/image-editing', methods=['POST'])
def image_editing():
    """
    图像编辑API
    
    支持的参数:
    - image: 图像文件
    - edit_type: 编辑类型 (gemini, filter, enhance, transform, repair)
    - edit_params: 编辑参数
    """
    try:
        # 获取服务实例
        service = get_image_editing_service()
        if not service:
            return jsonify({
                'success': False,
                'error': '服务初始化失败'
            }), 500

        # 支持JSON和form数据
        if request.is_json:
            data = request.get_json()
            edit_type = data.get('edit_type', 'gemini')
            edit_params = data.get('edit_params', {})
            image_data = data.get('image_data')
            result, status_code = service.edit_image(
                file=None,
                image_data=image_data,
                edit_type=edit_type,
                edit_params=edit_params
            )
        else:
            file = request.files.get('image')
            edit_type = request.form.get('edit_type', 'gemini')
            edit_params = {}

            if not file:
                return jsonify({
                    'success': False,
                    'error': '请上传图像文件'
                }), 400

            # 根据编辑类型获取参数
            if edit_type == 'gemini':
                edit_params['instruction'] = request.form.get('instruction', '')
                edit_params['gemini_model'] = request.form.get('gemini_model', 'gemini-2.0-flash-exp-image-generation')
            elif edit_type == 'filter':
                edit_params['filter_type'] = request.form.get('filter_type', 'blur')
                edit_params['intensity'] = float(request.form.get('intensity', 1.0))
            elif edit_type == 'enhance':
                edit_params['enhance_type'] = request.form.get('enhance_type', 'brightness')
                edit_params['factor'] = float(request.form.get('factor', 1.2))
            elif edit_type == 'transform':
                edit_params['transform_type'] = request.form.get('transform_type', 'resize')
                if edit_params['transform_type'] == 'resize':
                    edit_params['width'] = int(request.form.get('width', 800))
                    edit_params['height'] = int(request.form.get('height', 600))
                elif edit_params['transform_type'] == 'rotate':
                    edit_params['angle'] = float(request.form.get('angle', 90))
            elif edit_type == 'repair':
                edit_params['repair_type'] = request.form.get('repair_type', 'denoise')
                if edit_params['repair_type'] == 'gamma_correction':
                    edit_params['gamma'] = float(request.form.get('gamma', 1.2))

            result, status_code = service.edit_image(
                file=file,
                edit_type=edit_type,
                edit_params=edit_params
            )

        return jsonify(result), status_code

    except Exception as e:
        current_app.logger.error(f"图像编辑API错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'图像编辑失败: {str(e)}'
        }), 500


@api_bp.route('/image-editing/operations', methods=['GET'])
def get_editing_operations():
    """获取可用的图像编辑操作"""
    try:
        service = get_image_editing_service()
        if not service:
            return jsonify({
                'success': False,
                'error': '服务初始化失败'
            }), 500
            
        operations = service.get_available_operations()
        return jsonify({
            'success': True,
            'operations': operations
        })
    except Exception as e:
        current_app.logger.error(f"获取编辑操作错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'获取操作列表失败: {str(e)}'
        }), 500
