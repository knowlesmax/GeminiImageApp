"""
图像问答服务模块
"""
import os
from flask import jsonify, current_app
from google import genai
from google.genai import types


class ImageQAService:
    def __init__(self, client):
        self.client = client

    def process_image_qa(self, file=None, question='', model='gemini-2.0-flash', image_data=None):
        """处理图像问答请求"""
        try:
            from ..utils.helpers import save_uploaded_file, image_to_bytes, allowed_file

            # 处理图像数据
            if image_data:
                # 处理base64图像数据
                import base64
                import tempfile
                if "base64," in image_data:
                    image_data = image_data.split("base64,")[1]
                image_bytes = base64.b64decode(image_data)

                # 创建临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    tmp_file.write(image_bytes)
                    filepath = tmp_file.name

                # 重新读取图像字节
                image_bytes = image_to_bytes(filepath)
            else:
                # 验证文件
                if not file or file.filename == '':
                    return {'success': False, 'error': '未选择文件'}, 400

                if not allowed_file(file.filename):
                    return {'success': False, 'error': '无效的文件类型'}, 400

                # 保存上传的文件
                upload_folder = current_app.config['UPLOAD_FOLDER']
                filepath = save_uploaded_file(file, upload_folder)

                # 读取图像
                image_bytes = image_to_bytes(filepath)

            if not question or not question.strip():
                return {'success': False, 'error': '请输入问题'}, 400

            # 构建中文提示词
            chinese_prompt = f"请用中文回答以下关于图像的问题：{question.strip()}"

            # 使用指定的 Gemini 模型生成回答
            response = self.client.models.generate_content(
                model=model,
                contents=[
                    types.Part.from_text(text=chinese_prompt),
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=f"image/{file.filename.split('.')[-1].lower()}"
                    )
                ]
            )

            answer = response.text.strip()

            return {
                'success': True,
                'answer': answer,
                'image_path': filepath,
                'question': question,
                'model_used': model
            }, 200

        except Exception as e:
            error_msg = f'处理失败: {str(e)}'
            print(f"图像问答错误: {e}")
            return {'success': False, 'error': error_msg}, 500
