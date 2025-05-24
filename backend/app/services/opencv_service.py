"""
OpenCV 图像处理服务模块
"""
import os
import cv2
import numpy as np
from PIL import Image
import tempfile
import base64
from flask import current_app
from ..utils.helpers import save_uploaded_file, allowed_file


class OpenCVService:
    def __init__(self):
        # 初始化 YOLO 模型（如果可用）
        self.yolo_net = None
        self.yolo_classes = None
        self.yolo_output_layers = None
        self._load_yolo_model()

        # 初始化 Haar Cascade 分类器
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    def _load_yolo_model(self):
        """加载 YOLO 模型（如果可用）"""
        try:
            # 这里可以加载预训练的 YOLO 模型
            # 由于模型文件较大，这里使用简化版本
            pass
        except Exception as e:
            print(f"YOLO 模型加载失败: {e}")

    def detect_objects_opencv(self, file=None, image_data=None, method='contour', object_name='对象'):
        """使用 OpenCV 进行目标检测"""
        try:
            # 处理文件输入
            if image_data:
                image_data_clean = image_data.split(',')[1] if ',' in image_data else image_data
                image_bytes = base64.b64decode(image_data_clean)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    tmp_file.write(image_bytes)
                    filepath = tmp_file.name
            else:
                if not file or file.filename == '':
                    return {'success': False, 'error': '未选择文件'}, 400
                if not allowed_file(file.filename):
                    return {'success': False, 'error': '无效的文件类型'}, 400
                # 检查是否是已经存在的文件路径（用于测试）
                if hasattr(file, 'filepath') and os.path.exists(file.filepath):
                    filepath = file.filepath
                else:
                    # 标准的Flask文件上传对象
                    filepath = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])

            # 首先检查文件是否存在和有效
            if not os.path.exists(filepath):
                error_msg = f'图像文件不存在: {filepath}'
                print(error_msg)
                return {'success': False, 'error': error_msg}, 400

            # 检查文件大小
            file_size = os.path.getsize(filepath)
            if file_size == 0:
                error_msg = f'图像文件为空: {filepath}（文件大小: 0 字节）'
                print(error_msg)
                return {'success': False, 'error': error_msg}, 400

            if file_size < 100:  # 小于100字节的图像文件通常是无效的
                error_msg = f'图像文件过小，可能已损坏: {filepath}（文件大小: {file_size} 字节）'
                print(error_msg)
                return {'success': False, 'error': error_msg}, 400

            # 读取图像 - 使用多种方法确保能够读取
            image = None

            # 方法1: 直接使用cv2.imread
            try:
                image = cv2.imread(filepath)
                if image is not None and image.size > 0:
                    print("使用cv2.imread成功读取图像")
                else:
                    image = None
            except Exception as e:
                print(f"cv2.imread 失败: {e}")

            # 方法2: 如果直接读取失败，使用PIL转换
            if image is None:
                try:
                    from PIL import Image as PILImage
                    pil_image = PILImage.open(filepath)

                    # 检查图像是否有效
                    if pil_image.size[0] == 0 or pil_image.size[1] == 0:
                        raise ValueError("图像尺寸无效")

                    # 转换为RGB（如果是RGBA）
                    if pil_image.mode == 'RGBA':
                        pil_image = pil_image.convert('RGB')
                    elif pil_image.mode == 'P':
                        pil_image = pil_image.convert('RGB')

                    # 转换为numpy数组
                    image_array = np.array(pil_image)
                    # PIL使用RGB，OpenCV使用BGR，需要转换
                    image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                    print("使用PIL成功读取图像")
                except Exception as e:
                    print(f"PIL读取失败: {e}")

            # 方法3: 如果还是失败，尝试使用numpy直接读取
            if image is None:
                try:
                    # 读取文件字节
                    with open(filepath, 'rb') as f:
                        file_bytes = f.read()

                    if len(file_bytes) == 0:
                        raise ValueError("文件内容为空")

                    # 使用numpy和cv2解码
                    nparr = np.frombuffer(file_bytes, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    if image is not None and image.size > 0:
                        print("使用numpy成功读取图像")
                    else:
                        image = None
                except Exception as e:
                    print(f"numpy读取失败: {e}")

            if image is None:
                error_msg = f'无法读取图像文件: {filepath}。文件可能已损坏或格式不支持。文件大小: {file_size} 字节'
                print(error_msg)
                return {'success': False, 'error': error_msg}, 400

            # 验证图像尺寸
            if image.shape[0] == 0 or image.shape[1] == 0:
                error_msg = f'图像尺寸无效: {filepath}。图像尺寸: {image.shape}'
                print(error_msg)
                return {'success': False, 'error': error_msg}, 400

            # 如果用户指定了特定对象名称，进行内容验证
            if object_name and object_name.strip() and object_name.strip() != '对象':
                validation_result = self._validate_image_content(filepath, object_name.strip())
                if not validation_result['is_match']:
                    return {
                        'success': False,
                        'error': f'未检测到目标：{object_name.strip()}',
                        'message': validation_result['message'],
                        'suggestion': validation_result.get('suggestion', '请检查图像内容或修改查询词汇。'),
                        'detected_objects': validation_result.get('detected_objects', []),
                        'alternative_queries': validation_result.get('alternative_queries', [])
                    }, 200  # 改为200状态码，让前端正确处理内容不匹配

            detected_objects = []

            if method == 'haar':
                # 使用 Haar Cascade 检测（仅限人脸）
                # 验证是否与用户查询匹配
                if object_name and object_name.strip() and '人脸' not in object_name and '脸' not in object_name and 'face' not in object_name.lower():
                    return {
                        'success': False,
                        'error': f'未检测到目标：{object_name}',
                        'message': f'Haar Cascade方法仅支持人脸检测，但您查询的是"{object_name}"',
                        'suggestion': '请使用其他检测方法或修改查询为"人脸"'
                    }, 200  # 改为200状态码
                detected_objects = self._detect_faces_haar(image)
            elif method == 'contour':
                # 使用轮廓检测（通用对象检测）
                # 首先验证图像内容是否包含用户查询的对象
                if object_name and object_name.strip():
                    content_match = self._validate_image_content(filepath, object_name)
                    if not content_match['is_match']:
                        return {
                            'success': False,
                            'error': f'未检测到目标：{object_name}',
                            'message': content_match["message"],
                            'suggestion': content_match.get('suggestion', '请检查图像内容或修改查询词汇。'),
                            'detected_objects': content_match.get('detected_objects', []),
                            'alternative_queries': content_match.get('alternative_queries', [])
                        }, 200  # 改为200状态码
                detected_objects = self._detect_contours(image, object_name)
            elif method == 'color':
                # 使用颜色分割检测
                # 验证图像内容
                if object_name and object_name.strip():
                    content_match = self._validate_image_content(filepath, object_name)
                    if not content_match['is_match']:
                        return {
                            'success': False,
                            'error': f'未检测到目标：{object_name}',
                            'message': content_match["message"],
                            'suggestion': content_match.get('suggestion', '请检查图像内容或修改查询词汇。'),
                            'detected_objects': content_match.get('detected_objects', []),
                            'alternative_queries': content_match.get('alternative_queries', [])
                        }, 200  # 改为200状态码
                detected_objects = self._detect_by_color(image, object_name)
            elif method == 'edge':
                # 使用边缘检测
                # 验证图像内容
                if object_name and object_name.strip():
                    content_match = self._validate_image_content(filepath, object_name)
                    if not content_match['is_match']:
                        return {
                            'success': False,
                            'error': f'未检测到目标：{object_name}',
                            'message': content_match["message"],
                            'suggestion': content_match.get('suggestion', '请检查图像内容或修改查询词汇。'),
                            'detected_objects': content_match.get('detected_objects', []),
                            'alternative_queries': content_match.get('alternative_queries', [])
                        }, 200  # 改为200状态码
                detected_objects = self._detect_by_edges(image, object_name)

            # 生成带边界框的图像
            bbox_images = []
            for i, obj in enumerate(detected_objects):
                bbox_filename = f"opencv_bbox_{obj['label']}_{i}_{os.path.basename(filepath)}"
                bbox_filepath = os.path.join(current_app.config['GENERATED_FOLDER'], bbox_filename)
                self._draw_opencv_bbox(filepath, obj['bbox'], bbox_filepath, obj['label'], obj['method'], i)
                bbox_images.append(bbox_filepath)

            if detected_objects:
                # 创建汇总图片
                summary_filename = f"opencv_summary_{os.path.basename(filepath)}"
                summary_filepath = os.path.join(current_app.config['GENERATED_FOLDER'], summary_filename)
                self._draw_all_opencv_bboxes(filepath, detected_objects, summary_filepath)

                return {
                    'success': True,
                    'detected_objects': detected_objects,
                    'original_image': filepath,
                    'bbox_images': bbox_images,
                    'summary_image': summary_filepath,
                    'method': f'OpenCV {method}'
                }, 200
            else:
                return {
                    'success': False,
                    'error': f'使用 OpenCV {method} 方法未检测到对象',
                    'method': f'OpenCV {method}'
                }, 200

        except Exception as e:
            error_msg = f'OpenCV 检测失败: {str(e)}'
            print(f"OpenCV 检测错误: {e}")
            return {'success': False, 'error': error_msg}, 500

    def _validate_image_content(self, image_path, object_name):
        """改进的图像内容验证方法 - 更严格的验证策略"""
        try:
            print(f"OpenCV内容验证：开始验证图像是否包含 '{object_name}'")

            # 首先检查是否是通用查询词，如果是则要求用户输入具体对象
            generic_queries = ['对象', '物体', '东西', '主要对象', 'object', 'thing', 'item']
            if object_name.strip().lower() in [q.lower() for q in generic_queries]:
                return {
                    'is_match': False,
                    'message': f'请输入具体的对象名称，而不是通用词汇"{object_name}"',
                    'suggestion': '请指定您想要分割的具体对象，如：人、狗、汽车、花朵等',
                    'detected_objects': [],
                    'validation_method': '通用词汇拒绝',
                    'is_generic_query': True
                }

            # 方法1: 首先尝试使用YOLO进行快速验证（如果可用）
            yolo_validation = self._validate_with_yolo(image_path, object_name)
            if yolo_validation['is_available']:
                if yolo_validation['is_match']:
                    print(f"YOLO验证成功：检测到 '{object_name}'")
                    return {
                        'is_match': True,
                        'message': f'YOLO检测到匹配的对象: {object_name}',
                        'validation_method': 'YOLO快速验证',
                        'detected_objects': yolo_validation.get('detected_objects', [])
                    }
                else:
                    # YOLO明确表示不匹配，直接返回失败
                    print(f"YOLO验证失败：未检测到 '{object_name}'")
                    detected_objects = yolo_validation.get('detected_objects', [])
                    return {
                        'is_match': False,
                        'message': f'未检测到"{object_name}"。图像中检测到的对象: {", ".join(detected_objects[:5])}',
                        'suggestion': f'请尝试检测图像中实际存在的对象，如：{", ".join(detected_objects[:3])}' if detected_objects else '请上传包含明确对象的图像',
                        'detected_objects': detected_objects,
                        'validation_method': 'YOLO验证失败',
                        'yolo_available': True
                    }

            # 方法2: 如果YOLO不可用，使用Gemini进行详细验证
            gemini_validation = self._validate_with_gemini(image_path, object_name)
            if gemini_validation.get('is_available', True):
                if gemini_validation['is_match']:
                    print(f"Gemini验证成功：检测到 '{object_name}'")
                    return {
                        'is_match': True,
                        'message': f'Gemini检测到匹配的对象: {object_name}',
                        'validation_method': 'Gemini智能验证',
                        'detected_objects': gemini_validation.get('detected_objects', [])
                    }
                else:
                    # Gemini明确表示不匹配
                    print(f"Gemini验证失败：未检测到 '{object_name}'")
                    detected_objects = gemini_validation.get('detected_objects', [])
                    return {
                        'is_match': False,
                        'message': f'Gemini验证未检测到"{object_name}"。图像中检测到的对象: {", ".join(detected_objects[:5])}',
                        'suggestion': f'请尝试检测图像中实际存在的对象，如：{", ".join(detected_objects[:3])}' if detected_objects else '请上传包含明确对象的图像',
                        'detected_objects': detected_objects,
                        'validation_method': 'Gemini验证失败',
                        'gemini_available': True
                    }

            # 方法3: 如果前两种方法都不可用，使用OpenCV基础特征验证（更严格）
            opencv_validation = self._validate_with_opencv_features(image_path, object_name)
            if opencv_validation['is_match']:
                print(f"OpenCV特征验证成功：检测到相关特征")
                return {
                    'is_match': True,
                    'message': f'OpenCV检测到相关特征',
                    'validation_method': 'OpenCV特征验证',
                    'detected_objects': opencv_validation.get('detected_objects', []),
                    'opencv_limitation': True  # 标记这是OpenCV的限制性验证
                }

            # 所有验证方法都失败，返回详细的失败信息
            print(f"所有验证方法都失败，未检测到 '{object_name}'")

            # 收集所有检测到的对象
            all_detected = []
            if yolo_validation.get('detected_objects'):
                all_detected.extend(yolo_validation['detected_objects'])
            if gemini_validation.get('detected_objects'):
                all_detected.extend(gemini_validation['detected_objects'])
            if opencv_validation.get('detected_objects'):
                all_detected.extend(opencv_validation['detected_objects'])

            # 去重
            unique_detected = list(set(all_detected))

            return {
                'is_match': False,
                'message': f'多重验证均未检测到"{object_name}"。图像中检测到的对象: {", ".join(unique_detected[:5])}' if unique_detected else f'多重验证均未检测到"{object_name}"，且图像中未识别到明确对象',
                'suggestion': f'请尝试检测图像中实际存在的对象，如：{", ".join(unique_detected[:3])}' if unique_detected else '请上传包含明确对象的图像，或检查图像质量',
                'detected_objects': unique_detected,
                'validation_method': '多重验证失败',
                'yolo_available': yolo_validation.get('is_available', False),
                'gemini_available': gemini_validation.get('is_available', True)
            }

        except Exception as e:
            print(f"内容验证过程出错: {str(e)}")
            # 验证过程出错时，为了安全起见，拒绝继续处理
            return {
                'is_match': False,
                'message': f'内容验证过程出错: {str(e)}',
                'suggestion': '请重试或检查图像文件是否正确',
                'validation_method': '验证异常-拒绝处理',
                'detected_objects': []
            }

    def _validate_with_yolo(self, image_path, object_name):
        """使用YOLO进行内容验证"""
        try:
            # 尝试导入YOLO相关模块
            from ultralytics import YOLO
            import cv2

            # 检查是否有可用的YOLO模型
            yolo_model_path = 'yolo11n.pt'  # 使用检测模型而不是分割模型
            if not os.path.exists(yolo_model_path):
                return {
                    'is_available': False,
                    'is_match': False,
                    'message': 'YOLO模型不可用'
                }

            # 加载YOLO模型
            model = YOLO(yolo_model_path)

            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                return {
                    'is_available': True,
                    'is_match': False,
                    'message': '无法读取图像'
                }

            # 进行检测
            results = model(image, conf=0.3)  # 使用较低的置信度

            detected_objects = []
            for result in results:
                if result.boxes is not None:
                    classes = result.boxes.cls.cpu().numpy()
                    confidences = result.boxes.conf.cpu().numpy()

                    for cls, conf in zip(classes, confidences):
                        class_name = model.names[int(cls)]
                        detected_objects.append(class_name)

            # 检查是否匹配用户查询
            is_match = self._check_object_match(object_name, detected_objects)

            return {
                'is_available': True,
                'is_match': is_match,
                'detected_objects': detected_objects,
                'message': f'YOLO检测到: {", ".join(detected_objects[:5])}'
            }

        except ImportError:
            return {
                'is_available': False,
                'is_match': False,
                'message': 'YOLO模块不可用'
            }
        except Exception as e:
            return {
                'is_available': False,
                'is_match': False,
                'message': f'YOLO验证出错: {str(e)}'
            }

    def _validate_with_gemini(self, image_path, object_name):
        """使用Gemini进行智能内容验证 - 充分利用AI的语义理解能力"""
        try:
            from google import genai
            from google.genai import types
            from flask import current_app
            from ..utils.helpers import image_to_bytes

            # 初始化Gemini客户端
            client = genai.Client(api_key=current_app.config['GEMINI_API_KEY'])

            # 读取图像
            image_bytes = image_to_bytes(image_path)

            # 构建智能验证提示词 - 利用Gemini的强大理解能力
            validation_prompt = f"""
            你是一个专业的图像分析AI助手。请仔细分析这张图像，判断是否包含用户查询的对象："{object_name.strip()}"

            分析要求：
            1. 🔍 仔细观察图像中的所有对象、人物、动物、物品等
            2. 🧠 运用语义理解能力，考虑以下匹配情况：
               - 直接匹配：图像中确实有该对象
               - 同义词匹配：如"汽车"与"car"、"狗"与"dog"
               - 上下级关系：如"哈士奇"属于"狗"，"狗"属于"动物"
               - 相关对象：如查询"宠物"时图像有"狗"或"猫"
               - 模糊描述：如"毛茸茸的动物"可以匹配各种毛发动物
            3. 🎯 判断标准：
               - 严格匹配：图像中明确包含查询对象
               - 语义匹配：图像中有语义相关的对象
               - 不匹配：图像中完全没有相关对象

            请以JSON格式返回详细分析结果：
            {{
                "contains_object": true/false,
                "match_type": "direct/semantic/none",
                "confidence": 0.95,
                "detected_objects": ["具体检测到的对象1", "对象2", ...],
                "matching_objects": ["与查询匹配的对象1", "对象2", ...],
                "explanation": "详细说明匹配或不匹配的原因",
                "semantic_relationship": "说明语义关系，如：狗属于动物类别",
                "suggestions": ["如果不匹配，建议查询的对象1", "对象2", ...]
            }}

            特别注意：
            - 如果查询对象是通用词汇（如"对象"、"东西"），请在explanation中指出这是无效查询
            - 如果图像质量不佳或无法识别内容，请如实说明
            - 对于边缘情况，请给出合理的置信度评分
            - 充分利用你的常识和语义理解能力进行判断

            用户查询："{object_name.strip()}"
            """

            # 进行智能内容验证
            response = client.models.generate_content(
                model=current_app.config['GEMINI_VISION_MODEL'],
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    types.Part.from_text(text=validation_prompt)
                ]
            )

            # 解析响应
            import json
            import re

            response_text = response.text.strip()
            print(f"Gemini原始响应: {response_text[:200]}...")

            # 尝试提取JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    validation_result = json.loads(json_match.group())

                    contains_object = validation_result.get('contains_object', False)
                    match_type = validation_result.get('match_type', 'none')
                    confidence = validation_result.get('confidence', 0.5)
                    detected_objects = validation_result.get('detected_objects', [])
                    matching_objects = validation_result.get('matching_objects', [])
                    explanation = validation_result.get('explanation', '')
                    semantic_relationship = validation_result.get('semantic_relationship', '')
                    suggestions = validation_result.get('suggestions', [])

                    # 智能判断逻辑
                    is_match = False
                    if contains_object:
                        if match_type == 'direct' and confidence > 0.7:
                            is_match = True
                        elif match_type == 'semantic' and confidence > 0.6:
                            is_match = True
                        elif confidence > 0.8:  # 高置信度情况
                            is_match = True

                    # 合并所有相关对象
                    all_objects = list(set(detected_objects + matching_objects))

                    return {
                        'is_available': True,
                        'is_match': is_match,
                        'detected_objects': all_objects,
                        'matching_objects': matching_objects,
                        'explanation': explanation,
                        'semantic_relationship': semantic_relationship,
                        'confidence': confidence,
                        'match_type': match_type,
                        'suggestions': suggestions,
                        'gemini_analysis': {
                            'contains_object': contains_object,
                            'match_type': match_type,
                            'confidence': confidence
                        }
                    }

                except json.JSONDecodeError as e:
                    print(f"JSON解析失败: {e}")
                    # 继续使用文本分析作为备选方案

            # 如果JSON解析失败，使用增强的文本分析
            return self._fallback_text_analysis(response_text, object_name)

        except Exception as e:
            print(f"Gemini验证失败: {str(e)}")
            return {
                'is_available': False,
                'is_match': False,
                'message': f'Gemini验证出错: {str(e)}'
            }

    def _fallback_text_analysis(self, response_text, object_name):
        """备选的文本分析方法 - 当JSON解析失败时使用"""
        object_name_lower = object_name.lower()
        response_lower = response_text.lower()

        # 增强的匹配指标
        positive_indicators = [
            f'包含{object_name_lower}',
            f'有{object_name_lower}',
            f'存在{object_name_lower}',
            f'检测到{object_name_lower}',
            f'发现{object_name_lower}',
            f'看到{object_name_lower}',
            f'contains {object_name_lower}',
            f'has {object_name_lower}',
            f'detected {object_name_lower}',
            f'found {object_name_lower}',
            f'shows {object_name_lower}',
            f'includes {object_name_lower}',
            'true',
            '是的',
            '确实',
            '匹配'
        ]

        negative_indicators = [
            f'没有{object_name_lower}',
            f'不包含{object_name_lower}',
            f'未检测到{object_name_lower}',
            f'no {object_name_lower}',
            f'does not contain {object_name_lower}',
            f'not found {object_name_lower}',
            'false',
            '不是',
            '没有',
            '不匹配'
        ]

        # 计算匹配分数
        positive_score = sum(1 for indicator in positive_indicators if indicator in response_lower)
        negative_score = sum(1 for indicator in negative_indicators if indicator in response_lower)

        # 提取可能的检测对象
        detected_objects = []
        # 简单的对象提取逻辑
        common_objects = ['dog', 'cat', 'person', 'car', 'tree', 'house', 'bird', 'flower', 'chair', 'table']
        for obj in common_objects:
            if obj in response_lower:
                detected_objects.append(obj)

        is_match = positive_score > negative_score and positive_score > 0
        confidence = min(0.9, max(0.1, positive_score / max(1, positive_score + negative_score)))

        return {
            'is_available': True,
            'is_match': is_match,
            'detected_objects': detected_objects,
            'explanation': response_text[:300] + '...' if len(response_text) > 300 else response_text,
            'confidence': confidence,
            'match_type': 'text_analysis',
            'analysis_scores': {
                'positive': positive_score,
                'negative': negative_score
            }
        }

    def _validate_with_opencv_features(self, image_path, object_name):
        """使用OpenCV特征进行基础验证 - 更严格的验证"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {
                    'is_match': False,
                    'detected_objects': [],
                    'message': '无法读取图像'
                }

            detected_features = []

            # 1. 人脸检测（如果查询与人相关）
            if any(keyword in object_name.lower() for keyword in ['人', '脸', '头', 'person', 'face', 'head', '男', '女', '小孩', '儿童']):
                face_features = self._detect_face_features(image)
                if face_features:
                    detected_features.extend(face_features)
                    # 如果检测到人脸，直接返回匹配
                    return {
                        'is_match': True,
                        'detected_objects': face_features,
                        'message': f'OpenCV检测到人脸特征: {", ".join(face_features)}'
                    }

            # 2. 颜色特征检测（仅当查询明确包含颜色词时）
            color_features = self._detect_color_features(image, object_name)
            if color_features:
                detected_features.extend(color_features)

            # 3. 形状特征检测（仅当查询明确包含形状词时）
            shape_features = self._detect_shape_features(image, object_name)
            if shape_features:
                detected_features.extend(shape_features)

            # 4. 纹理特征检测（仅作为辅助信息）
            texture_features = self._detect_texture_features(image, object_name)
            if texture_features:
                detected_features.extend(texture_features)

            # 更严格的匹配条件：必须有明确的特征匹配
            if detected_features:
                is_match = self._validate_opencv_feature_match(object_name, detected_features)
                if is_match:
                    return {
                        'is_match': True,
                        'detected_objects': detected_features,
                        'message': f'OpenCV检测到匹配特征: {", ".join(detected_features)}'
                    }

            # 如果没有检测到相关特征，返回失败
            return {
                'is_match': False,
                'detected_objects': detected_features,
                'message': f'OpenCV未检测到与"{object_name}"相关的特征。检测到的特征: {", ".join(detected_features)}' if detected_features else f'OpenCV未检测到与"{object_name}"相关的任何特征'
            }

        except Exception as e:
            return {
                'is_match': False,
                'detected_objects': [],
                'message': f'OpenCV特征验证出错: {str(e)}'
            }

    def _check_object_match(self, query, detected_objects):
        """检查查询对象是否与检测到的对象匹配 - 增强版匹配逻辑"""
        if not detected_objects:
            return False

        query_lower = query.lower().strip()
        detected_lower = [obj.lower().strip() for obj in detected_objects]

        # 1. 直接匹配
        if query_lower in detected_lower:
            return True

        # 2. 部分匹配（更严格的条件）
        for detected in detected_lower:
            # 只有当查询词是检测到的对象的完整子串，或者检测到的对象是查询词的完整子串时才匹配
            if (len(query_lower) >= 2 and query_lower in detected) or (len(detected) >= 2 and detected in query_lower):
                return True

        # 3. 扩展的同义词匹配（大幅扩展映射表）
        synonym_map = {
            # 人类相关
            '人': ['person', 'people', 'human', 'man', 'woman', 'boy', 'girl', 'child'],
            '人物': ['person', 'people', 'human', 'man', 'woman'],
            '男人': ['man', 'person'],
            '女人': ['woman', 'person'],
            '小孩': ['child', 'boy', 'girl', 'person'],
            '儿童': ['child', 'boy', 'girl', 'person'],

            # 动物相关（大幅扩展）
            '狗': ['dog', 'puppy'],
            '小狗': ['dog', 'puppy'],
            '犬': ['dog'],
            '猫': ['cat', 'kitten'],
            '小猫': ['cat', 'kitten'],
            '猫咪': ['cat', 'kitten'],
            '鸟': ['bird'],
            '小鸟': ['bird'],
            '马': ['horse'],
            '牛': ['cow'],
            '羊': ['sheep'],
            '大象': ['elephant'],
            '象': ['elephant'],
            '斑马': ['zebra'],
            '长颈鹿': ['giraffe'],
            '鹿': ['giraffe'],
            '狮子': ['lion'],
            '老虎': ['tiger'],
            '虎': ['tiger'],
            '熊': ['bear'],
            '猴子': ['monkey'],
            '猴': ['monkey'],
            '兔子': ['rabbit'],
            '兔': ['rabbit'],
            '老鼠': ['mouse'],
            '鼠': ['mouse'],
            '动物': ['animal', 'dog', 'cat', 'bird', 'horse', 'cow', 'sheep', 'elephant', 'bear', 'zebra', 'giraffe', 'lion', 'tiger', 'monkey', 'rabbit', 'mouse'],

            # 交通工具相关
            '汽车': ['car', 'vehicle', 'automobile'],
            '车': ['car', 'vehicle', 'automobile', 'truck', 'bus'],
            '轿车': ['car', 'automobile'],
            '小车': ['car'],
            '卡车': ['truck'],
            '货车': ['truck'],
            '大车': ['truck', 'bus'],
            '公交车': ['bus'],
            '巴士': ['bus'],
            '自行车': ['bicycle', 'bike'],
            '单车': ['bicycle', 'bike'],
            '脚踏车': ['bicycle'],
            '摩托车': ['motorcycle'],
            '机车': ['motorcycle'],
            '飞机': ['airplane', 'aircraft'],
            '客机': ['airplane'],
            '船': ['boat', 'ship'],
            '小船': ['boat'],
            '火车': ['train'],
            '交通工具': ['car', 'truck', 'bus', 'motorcycle', 'bicycle', 'airplane', 'boat', 'train'],

            # 物品相关（大幅扩展）
            '瓶子': ['bottle'],
            '水瓶': ['bottle'],
            '椅子': ['chair'],
            '座椅': ['chair'],
            '桌子': ['table', 'desk'],
            '餐桌': ['table'],
            '书': ['book'],
            '书本': ['book'],
            '电脑': ['laptop', 'computer'],
            '笔记本电脑': ['laptop'],
            '手机': ['phone', 'cell phone'],
            '电话': ['phone'],
            '时钟': ['clock'],
            '钟表': ['clock'],
            '键盘': ['keyboard'],
            '鼠标': ['mouse'],
            '显示器': ['monitor'],
            '屏幕': ['monitor', 'tv'],
            '电视': ['tv'],
            '剪刀': ['scissors'],
            '剪子': ['scissors'],
            '泰迪熊': ['teddy bear'],
            '玩具熊': ['teddy bear'],
            '熊娃娃': ['teddy bear'],
            '吹风机': ['hair drier'],
            '电吹风': ['hair drier'],
            '牙刷': ['toothbrush'],
            '电动牙刷': ['toothbrush'],
            '雨伞': ['umbrella'],
            '伞': ['umbrella'],
            '手提包': ['handbag'],
            '包': ['handbag', 'backpack'],
            '背包': ['backpack'],
            '行李箱': ['suitcase'],
            '箱子': ['suitcase'],

            # 自然物体相关
            '花': ['flower'],
            '花朵': ['flower'],
            '树': ['tree'],
            '树木': ['tree'],
            '房子': ['house', 'building'],
            '建筑': ['building', 'house'],
            '楼房': ['building'],

            # 食物相关（新增）
            '苹果': ['apple'],
            '香蕉': ['banana'],
            '橙子': ['orange'],
            '橘子': ['orange'],
            '蛋糕': ['cake'],
            '面包': ['bread'],
            '三明治': ['sandwich'],
            '热狗': ['hot dog'],
            '披萨': ['pizza'],
            '甜甜圈': ['donut'],
            '胡萝卜': ['carrot'],
            '萝卜': ['carrot'],

            # 运动相关
            '球': ['ball', 'sports ball'],
            '足球': ['sports ball'],
            '篮球': ['sports ball'],
            '网球': ['sports ball', 'tennis racket'],
            '网球拍': ['tennis racket'],
            '棒球棒': ['baseball bat'],
            '滑板': ['skateboard'],
            '滑雪板': ['skis'],
            '风筝': ['kite'],

            # 英文到中文的反向映射（大幅扩展）
            'person': ['人', '人物', '人类'],
            'dog': ['狗', '小狗', '犬'],
            'cat': ['猫', '小猫', '猫咪'],
            'car': ['汽车', '车', '轿车', '小车'],
            'truck': ['卡车', '货车', '大车'],
            'bus': ['公交车', '巴士', '大车'],
            'bird': ['鸟', '小鸟'],
            'horse': ['马'],
            'cow': ['牛'],
            'sheep': ['羊'],
            'elephant': ['大象', '象'],
            'zebra': ['斑马'],
            'giraffe': ['长颈鹿', '鹿'],
            'lion': ['狮子'],
            'tiger': ['老虎', '虎'],
            'bear': ['熊'],
            'monkey': ['猴子', '猴'],
            'rabbit': ['兔子', '兔'],
            'mouse': ['老鼠', '鼠'],
            'bicycle': ['自行车', '单车', '脚踏车'],
            'motorcycle': ['摩托车', '机车'],
            'airplane': ['飞机', '客机'],
            'boat': ['船', '小船'],
            'train': ['火车'],
            'bottle': ['瓶子', '水瓶'],
            'chair': ['椅子', '座椅'],
            'table': ['桌子', '餐桌'],
            'book': ['书', '书本'],
            'laptop': ['电脑', '笔记本电脑'],
            'phone': ['手机', '电话'],
            'clock': ['时钟', '钟表'],
            'keyboard': ['键盘'],
            'mouse': ['鼠标'],
            'monitor': ['显示器', '屏幕'],
            'tv': ['电视', '屏幕'],
            'scissors': ['剪刀', '剪子'],
            'teddy bear': ['泰迪熊', '玩具熊', '熊娃娃'],
            'hair drier': ['吹风机', '电吹风'],
            'toothbrush': ['牙刷', '电动牙刷'],
            'umbrella': ['雨伞', '伞'],
            'handbag': ['手提包', '包'],
            'backpack': ['背包', '包'],
            'suitcase': ['行李箱', '箱子'],
            'flower': ['花', '花朵'],
            'tree': ['树', '树木'],
            'house': ['房子'],
            'building': ['建筑', '楼房'],
            'apple': ['苹果'],
            'banana': ['香蕉'],
            'orange': ['橙子', '橘子'],
            'cake': ['蛋糕'],
            'bread': ['面包'],
            'sandwich': ['三明治'],
            'hot dog': ['热狗'],
            'pizza': ['披萨'],
            'donut': ['甜甜圈'],
            'carrot': ['胡萝卜', '萝卜'],
            'ball': ['球'],
            'sports ball': ['足球', '篮球', '球'],
            'tennis racket': ['网球拍'],
            'baseball bat': ['棒球棒'],
            'skateboard': ['滑板'],
            'skis': ['滑雪板'],
            'kite': ['风筝']
        }

        # 4. 检查同义词匹配
        for key, synonyms in synonym_map.items():
            if key == query_lower:
                # 查询词在同义词映射的键中
                for synonym in synonyms:
                    if synonym in detected_lower:
                        return True
            elif query_lower in synonyms:
                # 查询词在同义词列表中
                if key in detected_lower:
                    return True
                # 检查其他同义词
                for synonym in synonyms:
                    if synonym in detected_lower:
                        return True

        # 5. 模糊匹配（仅对长度大于3的词进行）
        if len(query_lower) > 3:
            for detected in detected_lower:
                if len(detected) > 3:
                    # 计算相似度（简单的字符重叠）
                    common_chars = set(query_lower) & set(detected)
                    similarity = len(common_chars) / max(len(query_lower), len(detected))
                    if similarity > 0.6:  # 60%以上的字符重叠
                        return True

        # 6. 语义组匹配（新增）
        semantic_groups = {
            'animals': ['dog', 'cat', 'bird', 'horse', 'cow', 'sheep', 'elephant', 'zebra', 'giraffe', 'lion', 'tiger', 'bear', 'monkey', 'rabbit', 'mouse'],
            'vehicles': ['car', 'truck', 'bus', 'motorcycle', 'bicycle', 'airplane', 'boat', 'train'],
            'furniture': ['chair', 'table', 'sofa', 'bed'],
            'electronics': ['laptop', 'phone', 'tv', 'keyboard', 'mouse', 'monitor'],
            'food': ['apple', 'banana', 'orange', 'cake', 'bread', 'sandwich', 'hot dog', 'pizza', 'donut', 'carrot'],
            'sports': ['ball', 'sports ball', 'tennis racket', 'baseball bat', 'skateboard', 'skis', 'kite']
        }

        # 检查是否属于同一语义组
        query_group = None
        detected_groups = set()

        # 找到查询词所属的语义组
        for group_name, items in semantic_groups.items():
            if any(synonym in query_lower for synonym in items):
                query_group = group_name
                break
            # 检查中文同义词
            for item in items:
                if item in synonym_map and query_lower in synonym_map[item]:
                    query_group = group_name
                    break

        # 找到检测对象所属的语义组
        for detected in detected_lower:
            for group_name, items in semantic_groups.items():
                if detected in items:
                    detected_groups.add(group_name)

        # 如果属于同一语义组，则认为可能匹配（降低匹配严格度）
        if query_group and query_group in detected_groups:
            # 对于语义组匹配，我们可以给出提示而不是直接匹配
            # 这里暂时返回False，让上层逻辑处理
            pass

        return False

    def _detect_color_features(self, image, object_name):
        """检测颜色特征"""
        features = []

        # 颜色关键词映射
        color_keywords = {
            '红': [(0, 0, 100), (10, 255, 255), (170, 255, 255), (180, 255, 255)],
            '绿': [(40, 40, 40), (80, 255, 255)],
            '蓝': [(100, 40, 40), (130, 255, 255)],
            '黄': [(20, 40, 40), (40, 255, 255)],
            '白': [(0, 0, 200), (180, 30, 255)],
            '黑': [(0, 0, 0), (180, 255, 50)]
        }

        # 检查查询中是否包含颜色词
        for color_name, hsv_ranges in color_keywords.items():
            if color_name in object_name:
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

                # 创建颜色掩码
                mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
                for i in range(0, len(hsv_ranges), 2):
                    lower = np.array(hsv_ranges[i])
                    upper = np.array(hsv_ranges[i+1])
                    color_mask = cv2.inRange(hsv, lower, upper)
                    mask = cv2.bitwise_or(mask, color_mask)

                # 检查颜色区域大小
                color_area = cv2.countNonZero(mask)
                total_area = image.shape[0] * image.shape[1]

                if color_area > total_area * 0.05:  # 颜色区域占5%以上
                    features.append(f'{color_name}色区域')

        return features

    def _detect_shape_features(self, image, object_name):
        """检测形状特征"""
        features = []

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # 检测圆形
        if any(keyword in object_name for keyword in ['圆', '球', 'circle', 'ball']):
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
                                     param1=50, param2=30, minRadius=10, maxRadius=100)
            if circles is not None:
                features.append('圆形对象')

        # 检测直线和矩形
        if any(keyword in object_name for keyword in ['方', '矩形', '直线', 'square', 'rectangle', 'line']):
            edges = cv2.Canny(blurred, 50, 150)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            if lines is not None and len(lines) > 4:
                features.append('矩形/直线结构')

        return features

    def _detect_texture_features(self, image, object_name):
        """检测纹理特征"""
        features = []

        # 简单的纹理检测
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 计算图像的标准差（纹理复杂度指标）
        std_dev = np.std(gray)

        if std_dev > 50:  # 高纹理复杂度
            features.append('复杂纹理')
        elif std_dev < 20:  # 低纹理复杂度
            features.append('平滑表面')

        return features

    def _detect_face_features(self, image):
        """检测人脸特征"""
        features = []

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 使用Haar级联检测人脸
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) > 0:
            features.append('人脸')

        # 检测眼睛
        eyes = self.eye_cascade.detectMultiScale(gray, 1.1, 4)
        if len(eyes) > 0:
            features.append('眼部特征')

        return features

    def _validate_opencv_feature_match(self, object_name, detected_features):
        """验证OpenCV检测到的特征是否与查询对象匹配 - 更严格的匹配规则"""
        if not detected_features:
            return False

        object_name_lower = object_name.lower().strip()

        # 严格的特征匹配规则
        feature_matches = {
            # 颜色匹配 - 只有明确包含颜色词才匹配
            '红': ['红色区域'],
            '红色': ['红色区域'],
            '绿': ['绿色区域'],
            '绿色': ['绿色区域'],
            '蓝': ['蓝色区域'],
            '蓝色': ['蓝色区域'],
            '黄': ['黄色区域'],
            '黄色': ['黄色区域'],
            '白': ['白色区域'],
            '白色': ['白色区域'],
            '黑': ['黑色区域'],
            '黑色': ['黑色区域'],

            # 形状匹配 - 只有明确包含形状词才匹配
            '圆': ['圆形对象'],
            '圆形': ['圆形对象'],
            '球': ['圆形对象'],
            '方': ['矩形/直线结构'],
            '方形': ['矩形/直线结构'],
            '矩形': ['矩形/直线结构'],
            '正方形': ['矩形/直线结构'],
            '长方形': ['矩形/直线结构'],

            # 人脸匹配 - 人相关的查询
            '人': ['人脸', '眼部特征'],
            '脸': ['人脸', '眼部特征'],
            '人脸': ['人脸', '眼部特征'],
            '头': ['人脸', '眼部特征'],
            '男人': ['人脸', '眼部特征'],
            '女人': ['人脸', '眼部特征'],
            '小孩': ['人脸', '眼部特征'],
            '儿童': ['人脸', '眼部特征'],
            '人物': ['人脸', '眼部特征'],
            'person': ['人脸', '眼部特征'],
            'face': ['人脸', '眼部特征'],
            'head': ['人脸', '眼部特征'],
            'man': ['人脸', '眼部特征'],
            'woman': ['人脸', '眼部特征'],
            'child': ['人脸', '眼部特征'],
            'boy': ['人脸', '眼部特征'],
            'girl': ['人脸', '眼部特征']
        }

        # 检查是否有精确匹配的特征
        for keyword, expected_features in feature_matches.items():
            if keyword in object_name_lower:
                for feature in detected_features:
                    if any(expected in feature for expected in expected_features):
                        return True

        # 对于非特定特征查询，不允许通过OpenCV验证
        # 这样可以避免误判，让YOLO或Gemini来处理复杂对象识别
        return False

    def _detect_faces_haar(self, image):
        """使用 Haar Cascade 检测人脸"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        detected_objects = []
        height, width = image.shape[:2]

        # 检测人脸
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        for (x, y, w, h) in faces:
            ymin = y / height
            xmin = x / width
            ymax = (y + h) / height
            xmax = (x + w) / width

            detected_objects.append({
                'label': '人脸',
                'confidence': 0.8,
                'bbox': [ymin, xmin, ymax, xmax],
                'method': 'Haar Cascade'
            })

        return detected_objects

    def _detect_contours(self, image, object_name='对象'):
        """使用轮廓检测对象"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 多种预处理方法
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # 自适应阈值
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # 形态学操作
        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # 查找轮廓
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected_objects = []
        height, width = image.shape[:2]

        # 按面积排序，取最大的几个
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        for i, contour in enumerate(contours[:5]):  # 最多取5个最大的轮廓
            area = cv2.contourArea(contour)
            if area > 1000:  # 过滤太小的轮廓
                x, y, w, h = cv2.boundingRect(contour)

                # 计算轮廓的紧密度（用于评估对象质量）
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    confidence = min(0.9, max(0.3, circularity))
                else:
                    confidence = 0.5

                # 转换为归一化坐标
                ymin = y / height
                xmin = x / width
                ymax = (y + h) / height
                xmax = (x + w) / width

                detected_objects.append({
                    'label': f'{object_name}_{i+1}',
                    'confidence': confidence,
                    'bbox': [ymin, xmin, ymax, xmax],
                    'method': 'Contour Detection'
                })

        return detected_objects

    def _detect_by_color(self, image, object_name='对象'):
        """使用颜色分割检测对象"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        height, width = image.shape[:2]
        detected_objects = []

        # 定义多个颜色范围
        color_ranges = [
            # 红色
            ([0, 50, 50], [10, 255, 255]),
            ([170, 50, 50], [180, 255, 255]),
            # 绿色
            ([40, 50, 50], [80, 255, 255]),
            # 蓝色
            ([100, 50, 50], [130, 255, 255]),
            # 黄色
            ([20, 50, 50], [40, 255, 255]),
        ]

        for i, (lower, upper) in enumerate(color_ranges):
            lower = np.array(lower)
            upper = np.array(upper)

            # 创建掩码
            mask = cv2.inRange(hsv, lower, upper)

            # 形态学操作
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for j, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if area > 500:
                    x, y, w, h = cv2.boundingRect(contour)

                    ymin = y / height
                    xmin = x / width
                    ymax = (y + h) / height
                    xmax = (x + w) / width

                    color_names = ['红色', '红色', '绿色', '蓝色', '黄色']

                    detected_objects.append({
                        'label': f'{color_names[i]}{object_name}_{j+1}',
                        'confidence': 0.7,
                        'bbox': [ymin, xmin, ymax, xmax],
                        'method': 'Color Segmentation'
                    })

        return detected_objects[:3]  # 最多返回3个对象

    def _detect_by_edges(self, image, object_name='对象'):
        """使用边缘检测对象"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 多尺度边缘检测
        edges1 = cv2.Canny(gray, 50, 150)
        edges2 = cv2.Canny(gray, 100, 200)

        # 合并边缘
        edges = cv2.bitwise_or(edges1, edges2)

        # 膨胀操作连接断开的边缘
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)

        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected_objects = []
        height, width = image.shape[:2]

        # 按面积排序
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        for i, contour in enumerate(contours[:3]):  # 最多取3个
            area = cv2.contourArea(contour)
            if area > 800:
                x, y, w, h = cv2.boundingRect(contour)

                ymin = y / height
                xmin = x / width
                ymax = (y + h) / height
                xmax = (x + w) / width

                detected_objects.append({
                    'label': f'边缘{object_name}_{i+1}',
                    'confidence': 0.6,
                    'bbox': [ymin, xmin, ymax, xmax],
                    'method': 'Edge Detection'
                })

        return detected_objects

    def _draw_opencv_bbox(self, image_path, bbox_coords, output_path, label, method, color_index=0):
        """绘制 OpenCV 检测的边界框 - 支持不同颜色"""
        image = cv2.imread(image_path)
        height, width = image.shape[:2]

        ymin, xmin, ymax, xmax = bbox_coords
        x1 = int(xmin * width)
        y1 = int(ymin * height)
        x2 = int(xmax * width)
        y2 = int(ymax * height)

        # 颜色调色板
        colors = [
            (255, 0, 0),    # 红色
            (0, 255, 0),    # 绿色
            (0, 0, 255),    # 蓝色
            (255, 255, 0),  # 青色
            (255, 0, 255),  # 洋红色
            (0, 255, 255),  # 黄色
            (128, 0, 255),  # 紫色
            (255, 128, 0),  # 橙色
        ]

        color = colors[color_index % len(colors)]

        # 绘制边界框
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)

        # 添加标签背景和文本
        label_text = f"{label} ({method})"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        font_thickness = 2
        (text_width, text_height), baseline = cv2.getTextSize(label_text, font, font_scale, font_thickness)

        # 绘制标签背景
        cv2.rectangle(image, (x1, y1 - text_height - 10), (x1 + text_width + 10, y1), color, -1)

        # 绘制标签文本（白色）
        cv2.putText(image, label_text, (x1 + 5, y1 - 5), font, font_scale, (255, 255, 255), font_thickness)

        cv2.imwrite(output_path, image)
        return output_path

    def _draw_all_opencv_bboxes(self, image_path, detected_objects, output_path):
        """绘制所有 OpenCV 检测的边界框 - 使用不同颜色区分对象"""
        image = cv2.imread(image_path)
        height, width = image.shape[:2]

        # 扩展颜色调色板，使用更鲜明的颜色
        colors = [
            (255, 0, 0),    # 红色
            (0, 255, 0),    # 绿色
            (0, 0, 255),    # 蓝色
            (255, 255, 0),  # 青色
            (255, 0, 255),  # 洋红色
            (0, 255, 255),  # 黄色
            (128, 0, 255),  # 紫色
            (255, 128, 0),  # 橙色
            (0, 128, 255),  # 天蓝色
            (128, 255, 0),  # 青绿色
            (255, 0, 128),  # 粉红色
            (0, 255, 128),  # 春绿色
        ]

        for i, obj in enumerate(detected_objects):
            bbox = obj['bbox']
            label = obj['label']
            method = obj['method']
            confidence = obj.get('confidence', 0.0)

            ymin, xmin, ymax, xmax = bbox
            x1 = int(xmin * width)
            y1 = int(ymin * height)
            x2 = int(xmax * width)
            y2 = int(ymax * height)

            # 使用不同颜色
            color = colors[i % len(colors)]

            # 绘制边界框，线条粗细根据置信度调整
            thickness = max(2, int(confidence * 4)) if confidence > 0 else 3
            cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)

            # 添加标签背景
            label_text = f"{label} ({confidence:.2f})" if confidence > 0 else f"{label} ({method})"

            # 计算文本尺寸
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_thickness = 2
            (text_width, text_height), baseline = cv2.getTextSize(label_text, font, font_scale, font_thickness)

            # 绘制标签背景
            cv2.rectangle(image, (x1, y1 - text_height - 10), (x1 + text_width + 10, y1), color, -1)

            # 绘制标签文本（白色）
            cv2.putText(image, label_text, (x1 + 5, y1 - 5), font, font_scale, (255, 255, 255), font_thickness)

            # 在右上角添加对象编号
            number_text = f"#{i+1}"
            cv2.putText(image, number_text, (x2 - 30, y1 + 20), font, 0.5, color, 2)

        cv2.imwrite(output_path, image)
        return output_path

    def segment_image_opencv(self, file=None, image_data=None, method='contour_mask', object_name = ""):
        """使用 OpenCV 进行图像分割"""
        try:
            # 处理文件输入
            if image_data:
                image_data_clean = image_data.split(',')[1] if ',' in image_data else image_data
                image_bytes = base64.b64decode(image_data_clean)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    tmp_file.write(image_bytes)
                    filepath = tmp_file.name
            else:
                if not file or not hasattr(file, 'filename') or file.filename == '':
                    return {'success': False, 'error': '未选择文件'}, 400
                if not allowed_file(file.filename):
                    return {'success': False, 'error': '无效的文件类型'}, 400

                # 检查是否是已经存在的文件路径（用于测试）
                if hasattr(file, 'filepath') and os.path.exists(file.filepath):
                    filepath = file.filepath
                else:
                    # 标准的Flask文件上传对象
                    filepath = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])

            # 读取图像 - 使用多种方法确保能够读取
            image = None

            # 方法1: 直接使用cv2.imread
            try:
                image = cv2.imread(filepath)
            except Exception as e:
                print(f"cv2.imread 失败: {e}")

            # 方法2: 如果直接读取失败，使用PIL转换
            if image is None:
                try:
                    from PIL import Image as PILImage
                    pil_image = PILImage.open(filepath)
                    # 转换为RGB（如果是RGBA）
                    if pil_image.mode == 'RGBA':
                        pil_image = pil_image.convert('RGB')
                    # 转换为numpy数组
                    image_array = np.array(pil_image)
                    # PIL使用RGB，OpenCV使用BGR，需要转换
                    image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                    print("使用PIL成功读取图像")
                except Exception as e:
                    print(f"PIL读取失败: {e}")

            # 方法3: 如果还是失败，尝试使用numpy直接读取
            if image is None:
                try:
                    # 读取文件字节
                    with open(filepath, 'rb') as f:
                        file_bytes = f.read()

                    # 使用numpy和cv2解码
                    nparr = np.frombuffer(file_bytes, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    print("使用numpy成功读取图像")
                except Exception as e:
                    print(f"numpy读取失败: {e}")

            if image is None:
                error_msg = f'无法读取图像文件: {filepath}。请检查文件格式是否正确。'
                print(error_msg)
                return {'success': False, 'error': error_msg}, 400

            # 与Gemini分割服务保持一致的输入验证
            if not object_name or not object_name.strip():
                return {'success': False, 'error': '请输入要分割的对象名称'}, 400

            # 进行内容验证，确保图像中包含指定对象
            print(f"OpenCV分割：开始验证图像内容是否包含 '{object_name.strip()}'")
            validation_result = self._validate_image_content(filepath, object_name.strip())
            if not validation_result['is_match']:
                print(f"OpenCV分割：内容验证失败，未检测到 '{object_name.strip()}'")
                return {
                    'success': False,
                    'error': f'未检测到目标：{object_name.strip()}',
                    'message': validation_result['message'],
                    'suggestion': validation_result.get('suggestion', '请检查图像内容或修改查询词汇。'),
                    'detected_objects': validation_result.get('detected_objects', []),
                    'alternative_queries': validation_result.get('alternative_queries', []),
                    'content_mismatch': True,
                    'user_query': object_name.strip(),
                    'validation_method': validation_result.get('validation_method', 'OpenCV验证'),
                    'opencv_limitation': validation_result.get('opencv_limitation', False)
                }, 200  # 改为200状态码，让前端正确处理内容不匹配
            else:
                print(f"OpenCV分割：内容验证成功，使用方法：{validation_result.get('validation_method', '未知')}")

            segmented_objects = []
            segment_images = []

            if method == 'contour_mask':
                # 使用轮廓掩码分割（推荐）
                segments = self._contour_mask_segmentation(image, filepath, object_name)
                segmented_objects.extend(segments)

            elif method == 'grabcut':
                # 使用 GrabCut 算法
                segments = self._grabcut_segmentation(image, filepath)
                segmented_objects.extend(segments)

            elif method == 'watershed':
                # 使用 Watershed 算法
                segments = self._watershed_segmentation(image, filepath)
                segmented_objects.extend(segments)

            elif method == 'kmeans':
                # 使用 K-means 聚类
                segments = self._kmeans_segmentation(image, filepath)
                segmented_objects.extend(segments)

            # 收集分割图像路径
            for i, segment in enumerate(segmented_objects):
                if 'segment_image' in segment and os.path.exists(segment['segment_image']):
                    segment_images.append(segment['segment_image'])
                    print(f"分割图像已保存: {segment['segment_image']}")
                else:
                    print(f"分割图像不存在: {segment.get('segment_image', 'N/A')}")

            if segmented_objects:
                return {
                    'success': True,
                    'original_image': filepath,
                    'segmented_objects': segmented_objects,
                    'segment_images': segment_images,
                    'method': f'OpenCV {method}'
                }, 200
            else:
                return {
                    'success': False,
                    'error': f'使用 OpenCV {method} 方法未能分割出对象',
                    'method': f'OpenCV {method}'
                }, 200

        except Exception as e:
            error_msg = f'OpenCV 分割失败: {str(e)}'
            print(f"OpenCV 分割错误: {e}")
            return {'success': False, 'error': error_msg}, 500

    def _contour_mask_segmentation(self, image, filepath, object_name='主要对象'):
        """基于轮廓的掩码分割 - 精确分割对象轮廓"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = image.shape[:2]

        # 多种预处理方法组合
        # 1. 高斯模糊去噪
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # 2. 多种阈值方法
        # 自适应阈值
        thresh1 = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # Otsu阈值
        _, thresh2 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 组合阈值结果
        thresh = cv2.bitwise_or(thresh1, thresh2)

        # 3. 形态学操作优化轮廓
        # 闭运算：连接断开的轮廓
        kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel_close)

        # 开运算：去除噪声
        kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_open)

        # 4. 查找轮廓
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 5. 轮廓筛选和质量评估
        valid_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)

            # 面积筛选
            if area < 1000:  # 过滤太小的轮廓
                continue

            # 计算轮廓质量指标
            if perimeter > 0:
                # 圆形度：越接近1越圆
                circularity = 4 * np.pi * area / (perimeter * perimeter)

                # 凸包比率：轮廓面积与其凸包面积的比率
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                if hull_area > 0:
                    solidity = area / hull_area
                else:
                    solidity = 0

                # 长宽比
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h if h > 0 else 0

                # 综合质量评分
                quality_score = (circularity * 0.3 + solidity * 0.4 +
                               min(aspect_ratio, 1/aspect_ratio) * 0.3 if aspect_ratio > 0 else 0)

                valid_contours.append({
                    'contour': contour,
                    'area': area,
                    'quality': quality_score,
                    'circularity': circularity,
                    'solidity': solidity,
                    'aspect_ratio': aspect_ratio
                })

        # 按质量和面积排序
        valid_contours.sort(key=lambda x: (x['quality'] * 0.6 + (x['area'] / (width * height)) * 0.4), reverse=True)

        segmented_objects = []

        for i, contour_info in enumerate(valid_contours[:3]):  # 最多取3个最好的轮廓
            contour = contour_info['contour']

            # 创建精确的轮廓掩码
            mask = np.zeros(gray.shape, np.uint8)
            cv2.fillPoly(mask, [contour], 255)

            # 轮廓平滑处理
            epsilon = 0.02 * cv2.arcLength(contour, True)
            smoothed_contour = cv2.approxPolyDP(contour, epsilon, True)

            # 创建平滑后的掩码
            smooth_mask = np.zeros(gray.shape, np.uint8)
            cv2.fillPoly(smooth_mask, [smoothed_contour], 255)

            # 应用掩码到原图像
            result = image.copy()

            # 创建渐变边缘效果
            # 对掩码进行轻微的高斯模糊，创建柔和边缘
            blurred_mask = cv2.GaussianBlur(smooth_mask, (3, 3), 0)
            blurred_mask_3ch = cv2.cvtColor(blurred_mask, cv2.COLOR_GRAY2BGR) / 255.0

            # 应用掩码
            result = result * blurred_mask_3ch

            # 将背景设为白色
            background = np.ones_like(result) * 255
            result = result + background * (1 - blurred_mask_3ch)
            result = result.astype(np.uint8)

            # 获取精确的边界框
            x, y, w, h = cv2.boundingRect(smoothed_contour)

            # 智能裁剪：保持对象完整性
            # 计算对象的实际边界
            mask_coords = np.where(smooth_mask > 0)
            if len(mask_coords[0]) > 0:
                y_min, y_max = np.min(mask_coords[0]), np.max(mask_coords[0])
                x_min, x_max = np.min(mask_coords[1]), np.max(mask_coords[1])

                # 添加适当的边距
                padding_x = max(10, int((x_max - x_min) * 0.05))
                padding_y = max(10, int((y_max - y_min) * 0.05))

                x1 = max(0, x_min - padding_x)
                y1 = max(0, y_min - padding_y)
                x2 = min(width, x_max + padding_x)
                y2 = min(height, y_max + padding_y)
            else:
                # 回退到边界框
                padding = 10
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(width, x + w + padding)
                y2 = min(height, y + h + padding)

            cropped_result = result[y1:y2, x1:x2]

            # 保存分割结果
            import time
            timestamp = int(time.time() * 1000)  # 使用毫秒级时间戳避免重复
            safe_object_name = object_name.replace('/', '_').replace('\\', '_').replace(' ', '_')
            seg_filename = f"opencv_contour_{safe_object_name}_{i}_{timestamp}.png"
            seg_filepath = os.path.join(current_app.config['GENERATED_FOLDER'], seg_filename)
            cv2.imwrite(seg_filepath, cropped_result)

            # 计算置信度
            confidence = min(0.95, max(0.4, contour_info['quality']))

            # 转换为归一化坐标
            ymin = y1 / height
            xmin = x1 / width
            ymax = y2 / height
            xmax = x2 / width

            segmented_objects.append({
                'label': f'{object_name}_精确轮廓_{i+1}',
                'description': f'基于精确轮廓分割的{object_name}对象（质量评分: {contour_info["quality"]:.2f}）',
                'confidence': confidence,
                'bbox': [ymin, xmin, ymax, xmax],
                'segment_image': seg_filepath,
                'method': 'Precise Contour Mask',
                'quality_metrics': {
                    'circularity': contour_info['circularity'],
                    'solidity': contour_info['solidity'],
                    'aspect_ratio': contour_info['aspect_ratio'],
                    'area_ratio': contour_info['area'] / (width * height)
                }
            })

        return segmented_objects

    def _grabcut_segmentation(self, image, filepath):
        """GrabCut 分割算法"""
        height, width = image.shape[:2]

        # 创建一个矩形作为前景区域（图像中心区域）
        rect = (width//4, height//4, width//2, height//2)

        # 初始化掩码
        mask = np.zeros((height, width), np.uint8)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)

        # 应用 GrabCut
        cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)

        # 创建最终掩码
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        result = image * mask2[:, :, np.newaxis]

        # 保存分割结果
        import time
        timestamp = int(time.time() * 1000)
        seg_filename = f"opencv_grabcut_{timestamp}.png"
        seg_filepath = os.path.join(current_app.config['GENERATED_FOLDER'], seg_filename)
        cv2.imwrite(seg_filepath, result)

        return [{
            'label': 'GrabCut 前景',
            'description': '使用 GrabCut 算法分割的前景对象',
            'confidence': 0.8,
            'bbox': [0.25, 0.25, 0.75, 0.75],  # 近似边界框
            'segment_image': seg_filepath,
            'method': 'GrabCut'
        }]

    def _watershed_segmentation(self, image, filepath):
        """Watershed 分割算法"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 应用阈值
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # 噪声去除
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

        # 确定背景区域
        sure_bg = cv2.dilate(opening, kernel, iterations=3)

        # 查找前景区域
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)

        # 查找未知区域
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)

        # 标记标签
        _, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0

        # 应用 watershed
        markers = cv2.watershed(image, markers)
        image[markers == -1] = [255, 0, 0]

        # 保存结果
        import time
        timestamp = int(time.time() * 1000)
        seg_filename = f"opencv_watershed_{timestamp}.png"
        seg_filepath = os.path.join(current_app.config['GENERATED_FOLDER'], seg_filename)
        cv2.imwrite(seg_filepath, image)

        return [{
            'label': 'Watershed 分割',
            'description': '使用 Watershed 算法分割的区域',
            'confidence': 0.7,
            'bbox': [0.1, 0.1, 0.9, 0.9],
            'segment_image': seg_filepath,
            'method': 'Watershed'
        }]

    def _kmeans_segmentation(self, image, filepath):
        """K-means 聚类分割"""
        # 重塑图像数据
        data = image.reshape((-1, 3))
        data = np.float32(data)

        # 定义标准并应用 K-means
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        k = 3  # 聚类数量
        _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        # 转换回 uint8 并重塑为原始图像形状
        centers = np.uint8(centers)
        segmented_data = centers[labels.flatten()]
        segmented_image = segmented_data.reshape(image.shape)

        # 保存结果
        import time
        timestamp = int(time.time() * 1000)
        seg_filename = f"opencv_kmeans_{timestamp}.png"
        seg_filepath = os.path.join(current_app.config['GENERATED_FOLDER'], seg_filename)
        cv2.imwrite(seg_filepath, segmented_image)

        return [{
            'label': 'K-means 聚类',
            'description': f'使用 K-means 算法分割为 {k} 个区域',
            'confidence': 0.6,
            'bbox': [0.0, 0.0, 1.0, 1.0],
            'segment_image': seg_filepath,
            'method': 'K-means'
        }]


