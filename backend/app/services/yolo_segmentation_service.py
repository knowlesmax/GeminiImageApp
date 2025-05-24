"""
YOLO 图像分割服务
使用 YOLOv11 模型进行图像分割
"""
import os
import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import time
import base64
import tempfile
from flask import current_app
from ..utils.helpers import allowed_file, save_uploaded_file


class YOLOSegmentationService:
    """YOLO图像分割服务"""

    def __init__(self):
        self.models = {
            'yolo11n-seg': None,  # YOLOv11 nano segmentation
            'yolo11s-seg': None,  # YOLOv11 small segmentation
            'yolo11m-seg': None,  # YOLOv11 medium segmentation
            'yolo11l-seg': None,  # YOLOv11 large segmentation
            'yolo11x-seg': None,  # YOLOv11 extra large segmentation
        }
        self.current_model = None
        self.current_model_name = None

    def load_model(self, model_name='yolo11n-seg'):
        """加载YOLO分割模型"""
        try:
            if model_name not in self.models:
                model_name = 'yolo11n-seg'  # 默认使用nano版本

            if self.models[model_name] is None:
                # 使用配置中定义的模型目录
                models_folder = current_app.config.get('MODELS_FOLDER')
                if models_folder:
                    model_path = os.path.join(models_folder, f'{model_name}.pt')
                else:
                    # 回退到当前目录
                    model_path = f'{model_name}.pt'

                if os.path.exists(model_path):
                    print(f"找到本地分割模型文件: {model_path}")
                    print(f"正在加载 {model_name} 分割模型...")
                    self.models[model_name] = YOLO(model_path)
                    print(f"{model_name} 分割模型加载完成")
                else:
                    print(f"本地未找到分割模型文件: {model_path}")
                    print(f"正在下载并加载 {model_name} 分割模型...")
                    # 如果本地没有，先尝试下载到模型目录
                    if models_folder and os.path.exists(models_folder):
                        # 下载到指定的模型目录
                        self.models[model_name] = YOLO(f'{model_name}.pt')  # 先下载
                        # 然后移动到正确位置（如果需要）
                        downloaded_path = f'{model_name}.pt'
                        if os.path.exists(downloaded_path) and downloaded_path != model_path:
                            import shutil
                            shutil.move(downloaded_path, model_path)
                            print(f"分割模型文件已移动到: {model_path}")
                        self.models[model_name] = YOLO(model_path)
                    else:
                        self.models[model_name] = YOLO(f'{model_name}.pt')  # 这会自动下载
                    print(f"{model_name} 分割模型下载并加载完成")

            self.current_model = self.models[model_name]
            self.current_model_name = model_name
            return True

        except Exception as e:
            print(f"加载YOLO分割模型失败: {str(e)}")
            return False

    def segment_image_yolo(self, file=None, image_data=None, model_name='yolo11n-seg', confidence=0.5, user_query=None):
        """使用YOLO进行图像分割"""
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
                filepath = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])

            # 加载模型
            if not self.load_model(model_name):
                return {
                    'success': False,
                    'error': f'无法加载YOLO分割模型: {model_name}'
                }

            # 读取图像
            image = cv2.imread(filepath)
            if image is None:
                return {
                    'success': False,
                    'error': '无法读取图像文件'
                }

            # 如果提供了用户查询，验证内容匹配性
            if user_query and user_query.strip():
                content_match_result = self._validate_content_match(filepath, user_query)
                if not content_match_result['is_match']:
                    return {
                        'success': False,
                        'error': f'未检测到目标：{user_query}',
                        'message': f'图像中检测到的对象与您查询的"{user_query}"不匹配。{content_match_result["message"]}',
                        'suggestion': content_match_result.get('suggestion', '请检查图像内容或修改查询词汇。'),
                        'detected_objects': content_match_result.get('detected_objects', []),
                        'alternative_queries': content_match_result.get('alternative_queries', [])
                    }, 200  # 改为200状态码，让前端正确处理内容不匹配

            # 进行分割
            # 如果用户指定了查询对象，先进行内容匹配验证
            if user_query and user_query.strip():
                content_validation = self._validate_content_match(filepath, user_query.strip())
                if not content_validation['is_match']:
                    return {
                        'success': False,
                        'error': f'未检测到目标：{user_query.strip()}',
                        'message': content_validation['message'],
                        'suggestion': content_validation.get('suggestion', '请检查图像内容或修改查询词汇'),
                        'detected_objects': content_validation.get('detected_objects', []),
                        'alternative_queries': content_validation.get('alternative_queries', []),
                        'content_mismatch': True,
                        'user_query': user_query.strip()
                    }, 200  # 改为200状态码，让前端正确处理内容不匹配

            results = self.current_model(image, conf=confidence)

            # 处理分割结果
            segmented_objects = []
            segment_images = []

            for result in results:
                if result.masks is not None:
                    masks = result.masks.data.cpu().numpy()
                    boxes = result.boxes.xyxy.cpu().numpy()
                    classes = result.boxes.cls.cpu().numpy()
                    confidences = result.boxes.conf.cpu().numpy()

                    height, width = image.shape[:2]

                    for i, (mask, box, cls, conf) in enumerate(zip(masks, boxes, classes, confidences)):
                        # 获取类别名称
                        class_name = self.current_model.names[int(cls)]

                        # 如果有用户查询，只处理匹配的对象
                        if user_query and user_query.strip():
                            if not self._is_target_object(class_name, user_query):
                                continue

                        # 调整掩码大小到原图尺寸
                        mask_resized = cv2.resize(mask, (width, height))
                        mask_binary = (mask_resized > 0.5).astype(np.uint8) * 255

                        # 使用精确轮廓分割
                        segmented_image = self._create_precise_segment(image, mask_binary, box)

                        # 获取边界框
                        x1, y1, x2, y2 = box.astype(int)

                        # 裁剪分割区域（保持完整对象）
                        padding = 10
                        x1_crop = max(0, x1 - padding)
                        y1_crop = max(0, y1 - padding)
                        x2_crop = min(width, x2 + padding)
                        y2_crop = min(height, y2 + padding)

                        cropped_segment = segmented_image[y1_crop:y2_crop, x1_crop:x2_crop]

                        # 保存分割图像
                        timestamp = int(time.time())
                        seg_filename = f"yolo_segment_{class_name}_{i}_{timestamp}.png"
                        seg_filepath = os.path.join(current_app.config['GENERATED_FOLDER'], seg_filename)
                        cv2.imwrite(seg_filepath, cropped_segment)

                        segment_images.append(seg_filepath)

                        # 归一化坐标
                        ymin = y1 / height
                        xmin = x1 / width
                        ymax = y2 / height
                        xmax = x2 / width

                        segmented_objects.append({
                            'label': f'{class_name}_{i+1}',
                            'description': f'YOLO分割的{class_name}对象',
                            'confidence': float(conf),
                            'bbox': [ymin, xmin, ymax, xmax],
                            'segment_image': seg_filepath,
                            'method': f'YOLO {model_name}',
                            'class_id': int(cls),
                            'class_name': class_name
                        })

            if segmented_objects:
                return {
                    'success': True,
                    'original_image': filepath,
                    'segmented_objects': segmented_objects,
                    'segment_images': segment_images,
                    'method': f'YOLO {model_name}',
                    'total_objects': len(segmented_objects)
                }, 200
            else:
                if user_query and user_query.strip():
                    return {
                        'success': False,
                        'error': f'未检测到指定的目标对象：{user_query}',
                        'message': f'虽然图像中检测到了其他对象，但未找到与"{user_query}"匹配的对象',
                        'method': f'YOLO {model_name}'
                    }, 200
                else:
                    return {
                        'success': False,
                        'error': f'使用 YOLO {model_name} 未能分割出对象',
                        'method': f'YOLO {model_name}'
                    }, 200

        except Exception as e:
            error_msg = f'YOLO 分割失败: {str(e)}'
            print(f"YOLO 分割错误: {e}")
            return {'success': False, 'error': error_msg}, 500

    def _create_precise_segment(self, image, mask_binary, box):
        """创建精确的轮廓分割图像"""
        # 找到掩码的轮廓
        contours, _ = cv2.findContours(mask_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            # 如果没有找到轮廓，使用原始掩码
            result = image.copy()
            result[mask_binary == 0] = [255, 255, 255]
            return result

        # 找到最大的轮廓
        largest_contour = max(contours, key=cv2.contourArea)

        # 创建精确的轮廓掩码
        precise_mask = np.zeros(mask_binary.shape, dtype=np.uint8)
        cv2.fillPoly(precise_mask, [largest_contour], 255)

        # 应用精确掩码到原图像
        result = image.copy()
        result[precise_mask == 0] = [255, 255, 255]  # 白色背景

        return result

    def _is_target_object(self, class_name, user_query):
        """检查检测到的对象是否与用户查询匹配"""
        # 使用与检测服务相同的同义词映射
        synonym_map = self._get_synonym_map()

        user_query_lower = user_query.lower().strip()
        class_name_lower = class_name.lower()

        # 直接匹配
        if user_query_lower == class_name_lower:
            return True

        # 同义词匹配
        for key, synonyms in synonym_map.items():
            if key == class_name_lower and user_query_lower in synonyms:
                return True
            if user_query_lower == key and class_name_lower in synonyms:
                return True

        # 部分匹配（严格条件）
        if len(user_query_lower) > 3:
            if (user_query_lower in class_name_lower and len(user_query_lower) / len(class_name_lower) > 0.6) or \
               (class_name_lower in user_query_lower and len(class_name_lower) / len(user_query_lower) > 0.6):
                return True

        return False

    def _get_synonym_map(self):
        """获取同义词映射表（与检测服务保持一致）"""
        return {
            # 动物类
            'cat': ['kitten', 'feline', '猫', '小猫', 'kitty', '猫咪', '喵', '猫猫'],
            'dog': ['puppy', 'canine', '狗', '小狗', 'doggy', '狗狗', '犬', '汪'],
            'bird': ['飞鸟', '鸟类', 'avian', '鸟儿', '小鸟'],
            'horse': ['马', 'equine', 'pony', '马匹', '小马'],
            'cow': ['cattle', '牛', 'bull', '奶牛', '母牛'],
            'sheep': ['羊', 'lamb', '绵羊', '小羊'],
            'elephant': ['大象', '象'],
            'bear': ['熊', '狗熊', '黑熊', '棕熊'],
            'zebra': ['斑马'],
            'giraffe': ['长颈鹿'],
            'lion': ['狮子', '雄狮', '母狮'],
            'tiger': ['老虎', '虎'],
            'monkey': ['猴子', '猴'],
            'rabbit': ['兔子', '小兔', '兔'],

            # 交通工具
            'car': ['automobile', 'vehicle', '汽车', '车辆', '轿车', '小车'],
            'truck': ['lorry', '卡车', '货车', '大车'],
            'bus': ['coach', '公交车', '巴士', '客车'],
            'motorcycle': ['motorbike', '摩托车', '机车', '摩托'],
            'bicycle': ['bike', '自行车', '单车', '脚踏车'],
            'train': ['火车', 'locomotive', '列车'],
            'airplane': ['plane', '飞机', 'aircraft', '客机'],
            'boat': ['ship', '船', '轮船', '小船'],

            # 人物
            'person': ['people', 'human', '人', '人类', 'man', 'woman', 'individual', '人物'],
            'child': ['kid', '孩子', '儿童', '小孩'],
            'baby': ['infant', '婴儿', '宝宝', '小宝宝'],

            # 物品
            'phone': ['mobile', 'cellphone', '手机', '电话', 'smartphone', '移动电话'],
            'laptop': ['computer', '笔记本', '电脑', 'notebook', '笔记本电脑'],
            'book': ['书', '书籍', '图书'],
            'bottle': ['瓶子', 'container', '水瓶'],
            'cup': ['mug', '杯子', '茶杯', '水杯'],
            'clock': ['时钟', '钟表', 'watch', '手表'],
            'tv': ['television', '电视', 'monitor', '电视机'],
            'remote': ['遥控器', 'controller', '遥控'],

            # 食物
            'apple': ['苹果'],
            'banana': ['香蕉'],
            'orange': ['橙子', '橘子', '桔子'],
            'pizza': ['比萨', '披萨'],
            'cake': ['蛋糕'],
            'sandwich': ['三明治'],
            'donut': ['甜甜圈', '油炸圈饼'],

            # 家具
            'chair': ['椅子', '座椅'],
            'couch': ['sofa', '沙发'],
            'bed': ['床', '床铺'],
            'dining table': ['table', '桌子', '餐桌', '饭桌'],
            'toilet': ['厕所', '马桶', '卫生间'],

            # 运动用品
            'sports ball': ['ball', '球', '运动球'],
            'tennis racket': ['tennis', '网球拍', '球拍'],
            'baseball bat': ['棒球棒', '球棒'],
            'baseball glove': ['棒球手套', '手套'],
            'skateboard': ['滑板'],
            'surfboard': ['冲浪板'],
            'ski': ['滑雪板'],

            # 厨房用品
            'knife': ['刀', '小刀', '菜刀'],
            'spoon': ['勺子', '汤匙', '勺'],
            'fork': ['叉子', '餐叉'],
            'bowl': ['碗', '饭碗'],
            'wine glass': ['酒杯', '红酒杯', '玻璃杯'],
            'refrigerator': ['冰箱', 'fridge'],
            'microwave': ['微波炉'],
            'oven': ['烤箱'],
            'toaster': ['烤面包机'],

            # 电子设备
            'keyboard': ['键盘'],
            'mouse': ['鼠标'],
            'cell phone': ['phone', '手机', 'mobile', '移动电话'],

            # 植物和自然
            'flower': ['花', '花朵', '鲜花'],
            'tree': ['树', '树木', '大树'],
            'grass': ['草', '草地', '草坪'],

            # 建筑和结构
            'building': ['建筑', '房子', '楼房', '大楼'],
            'house': ['房子', '住宅', '房屋'],
            'bridge': ['桥', '大桥', '桥梁'],
        }

    def get_available_models(self):
        """获取可用的YOLO分割模型列表"""
        return {
            'yolo11n-seg': {
                'name': 'YOLOv11 Nano Segmentation',
                'description': '最快速度，较小精度',
                'size': '~7MB'
            },
            'yolo11s-seg': {
                'name': 'YOLOv11 Small Segmentation',
                'description': '平衡速度和精度',
                'size': '~25MB'
            },
            'yolo11m-seg': {
                'name': 'YOLOv11 Medium Segmentation',
                'description': '中等速度，较高精度',
                'size': '~52MB'
            },
            'yolo11l-seg': {
                'name': 'YOLOv11 Large Segmentation',
                'description': '较慢速度，高精度',
                'size': '~147MB'
            },
            'yolo11x-seg': {
                'name': 'YOLOv11 Extra Large Segmentation',
                'description': '最高精度，最慢速度',
                'size': '~221MB'
            }
        }

    def compare_with_opencv(self, image_path, opencv_result, yolo_model='yolo11n-seg', confidence=0.5):
        """与OpenCV分割结果进行对比"""
        try:
            # 获取YOLO分割结果
            yolo_result = self.segment_image_yolo(
                file=None,
                image_data=None,
                model_name=yolo_model,
                confidence=confidence
            )

            # 需要传入图像路径，所以创建一个临时文件对象
            class TempFile:
                def __init__(self, path):
                    self.filename = os.path.basename(path)
                    self._path = path

                def save(self, path):
                    import shutil
                    shutil.copy2(self._path, path)
                    return path

            temp_file = TempFile(image_path)
            yolo_result = self.segment_image_yolo(
                file=temp_file,
                model_name=yolo_model,
                confidence=confidence
            )

            # 构建对比结果
            comparison_result = {
                'success': True,
                'yolo_result': yolo_result[0] if isinstance(yolo_result, tuple) else yolo_result,
                'opencv_result': opencv_result,
                'comparison': {
                    'yolo_count': yolo_result[0].get('total_objects', 0) if isinstance(yolo_result, tuple) and yolo_result[0].get('success') else 0,
                    'opencv_count': len(opencv_result.get('segmented_objects', [])) if opencv_result.get('success') else 0,
                    'yolo_model': yolo_model,
                    'opencv_method': opencv_result.get('method', 'OpenCV')
                }
            }

            return comparison_result

        except Exception as e:
            print(f"YOLO分割对比错误: {str(e)}")
            return {
                'success': False,
                'error': f'YOLO分割对比失败: {str(e)}'
            }

    def _validate_content_match(self, image_path, user_query):
        """验证用户查询内容与图像内容的匹配性"""
        try:
            # 首先进行快速检测，获取图像中的对象
            if not self.load_model('yolo11n-seg'):  # 使用最快的模型进行检测
                return {
                    'is_match': True,  # 如果无法加载模型，允许继续
                    'message': '无法验证内容匹配性，将继续处理'
                }

            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                return {
                    'is_match': True,
                    'message': '无法读取图像，将继续处理'
                }

            # 进行快速检测
            results = self.current_model(image, conf=0.3)  # 使用较低的置信度进行检测

            detected_objects = []
            for result in results:
                if result.boxes is not None:
                    classes = result.boxes.cls.cpu().numpy()
                    confidences = result.boxes.conf.cpu().numpy()

                    for cls, conf in zip(classes, confidences):
                        class_name = self.current_model.names[int(cls)]
                        detected_objects.append({
                            'class_name': class_name,
                            'confidence': float(conf)
                        })

            if not detected_objects:
                return {
                    'is_match': False,
                    'message': '图像中未检测到任何对象',
                    'suggestion': '请上传包含明确对象的图像',
                    'detected_objects': []
                }

            # 分析用户查询与检测到的对象的匹配性
            user_query_lower = user_query.lower()
            detected_classes = [obj['class_name'].lower() for obj in detected_objects]

            # 创建类别映射（英文到中文，以及常见的同义词）
            class_mapping = {
                'person': ['人', '人物', '人类', '男人', '女人', '小孩', '儿童'],
                'dog': ['狗', '小狗', '犬', '宠物狗'],
                'cat': ['猫', '小猫', '猫咪', '宠物猫'],
                'car': ['汽车', '车', '轿车', '小车'],
                'truck': ['卡车', '货车', '大车'],
                'bird': ['鸟', '小鸟', '鸟类'],
                'horse': ['马', '马匹'],
                'cow': ['牛', '奶牛', '母牛'],
                'sheep': ['羊', '绵羊'],
                'bicycle': ['自行车', '单车', '脚踏车'],
                'motorcycle': ['摩托车', '机车'],
                'airplane': ['飞机', '客机'],
                'boat': ['船', '小船', '船只'],
                'bottle': ['瓶子', '水瓶'],
                'chair': ['椅子', '座椅'],
                'table': ['桌子', '餐桌'],
                'laptop': ['笔记本电脑', '电脑'],
                'phone': ['手机', '电话'],
                'book': ['书', '书本'],
                'clock': ['时钟', '钟表'],
                'flower': ['花', '花朵'],
                'tree': ['树', '树木'],
                'building': ['建筑', '房子', '楼房']
            }

            # 检查是否匹配
            is_match = False
            matched_objects = []

            # 直接匹配检测到的类别
            for detected_class in detected_classes:
                if detected_class in user_query_lower or user_query_lower in detected_class:
                    is_match = True
                    matched_objects.append(detected_class)

            # 通过映射检查匹配
            if not is_match:
                for english_class, chinese_variants in class_mapping.items():
                    if english_class in detected_classes:
                        for chinese_variant in chinese_variants:
                            if chinese_variant in user_query_lower:
                                is_match = True
                                matched_objects.append(english_class)
                                break

                    # 反向检查：用户输入英文，图像中有对应对象
                    if english_class in user_query_lower and english_class in detected_classes:
                        is_match = True
                        matched_objects.append(english_class)

            if is_match:
                return {
                    'is_match': True,
                    'message': f'检测到匹配的对象: {", ".join(matched_objects)}',
                    'detected_objects': detected_objects,
                    'matched_objects': matched_objects
                }
            else:
                detected_names = [obj['class_name'] for obj in detected_objects[:5]]  # 只显示前5个
                return {
                    'is_match': False,
                    'message': f'图像中检测到的对象({", ".join(detected_names)})与您的查询"{user_query}"不匹配',
                    'suggestion': f'图像中包含: {", ".join(detected_names)}。请修改查询词汇或上传包含"{user_query}"的图像。',
                    'detected_objects': detected_objects
                }

        except Exception as e:
            print(f"内容匹配验证错误: {str(e)}")
            # 如果验证过程出错，允许继续处理
            return {
                'is_match': True,
                'message': f'内容匹配验证出错，将继续处理: {str(e)}'
            }
