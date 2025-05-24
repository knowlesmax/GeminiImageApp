# Gemini 图像处理应用

基于 Google Gemini AI 模型的综合图像处理应用。这是一个 Flask 网络应用，提供多种 AI 驱动的图像处理功能，包括图像问答、生成、编辑、目标检测和图像分割。

## 🌟 主要功能

### 🤖 图像问答
- 上传图像并用中文提问
- 获得关于图像内容的智能回答
- 由 Gemini 2.0 Flash 视觉模型驱动

### 🎨 图像生成
- 根据中文文本描述生成图像
- 自动翻译为英文以获得更好的结果
- 支持多种模型选择：
  - **Imagen 3** (推荐) - 高质量照片级图像
  - **Gemini 2.0 Flash** (实验性) - 快速创意生成
- **新功能：动态模型选择** - 从 API 获取可用模型列表

### ✏️ 图像编辑
- 高级图像编辑功能（即将推出）
- AI 驱动的修改和增强

### 🎯 目标检测
- 检测图像中的特定对象
- 生成带置信度分数的边界框
- 支持中文自定义对象查询
- **新功能：汇总检测** - 将所有检测到的对象汇总到一张图片中，使用不同颜色标识

### 🔍 图像分割
- 精确的像素级对象分割
- 多对象实例检测
- 详细的分割掩码和覆盖层
- **已修复配额问题** - 使用 gemini-2.0-flash 模型避免 429 错误

## 🛠️ 技术栈

### 后端
- **Flask 3.0+** - Web 框架
- **google-genai 1.16.1** - Google Gemini AI SDK（最新版本）
- **Pillow (PIL)** - 图像处理
- **Python 3.8+** - 运行环境

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **TailwindCSS** - 实用优先的 CSS 框架
- **Font Awesome** - 图标库
- **响应式设计** - 移动端友好界面
- **中文界面** - 所有前端文本均为中文

### AI 模型
- **gemini-2.0-flash** - 主要视觉和分析模型
- **imagen-3.0-generate-002** - 高质量图像生成
- **gemini-2.0-flash-exp-image-generation** - 实验性图像生成

## 📦 快速开始

### 1. 克隆和设置

```bash
git clone <repository-url>
cd GeminiImageApp
```

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置环境

在根目录创建 `.env` 文件：
```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
```

从 [Google AI Studio](https://ai.google.dev/) 获取您的 API 密钥。

### 4. 运行应用

```bash
cd backend
python run.py
```

在浏览器中访问 `http://localhost:5000` 开始使用！

## 📁 项目结构

```
GeminiImageApp/
├── backend/                    # 后端代码
│   ├── app/                   # Flask应用核心
│   │   ├── __init__.py       # 应用工厂
│   │   ├── config.py         # 配置管理
│   │   ├── models/           # 数据模型
│   │   ├── services/         # 业务逻辑服务
│   │   │   ├── image_qa_service.py
│   │   │   ├── image_generation_service.py
│   │   │   ├── image_editing_service.py
│   │   │   ├── object_detection_service.py
│   │   │   ├── image_segmentation_service.py
│   │   │   ├── video_generation_service.py
│   │   │   ├── opencv_service.py
│   │   │   ├── yolo_detection_service.py
│   │   │   └── yolo_segmentation_service.py
│   │   ├── api/              # API路由
│   │   │   ├── __init__.py
│   │   │   ├── image_qa.py
│   │   │   ├── image_generation.py
│   │   │   ├── image_editing.py
│   │   │   ├── object_detection.py
│   │   │   ├── image_segmentation.py
│   │   │   └── video_generation.py
│   │   ├── main/             # 主路由
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   └── utils/            # 工具函数
│   │       ├── __init__.py
│   │       └── helpers.py
│   ├── tests/                # 测试文件
│   ├── requirements.txt      # Python依赖
│   └── run.py               # 应用启动文件
├── frontend/                 # 前端代码
│   ├── src/                 # Vue.js源码
│   │   ├── components/      # 可复用组件
│   │   │   ├── common/      # 通用组件
│   │   │   └── ui/          # UI组件
│   │   ├── pages/           # 页面组件
│   │   │   ├── Home.vue
│   │   │   ├── ImageQA.vue
│   │   │   ├── ImageGeneration.vue
│   │   │   ├── ImageEditing.vue
│   │   │   ├── ObjectDetection.vue
│   │   │   ├── ImageSegmentation.vue
│   │   │   ├── VideoGeneration.vue
│   │   │   └── Settings.vue
│   │   ├── services/        # API服务
│   │   │   └── api.js
│   │   ├── utils/           # 工具函数
│   │   ├── assets/          # 静态资源
│   │   │   ├── css/
│   │   │   │   ├── style.css
│   │   │   │   ├── themes.css
│   │   │   │   └── components/
│   │   │   ├── js/
│   │   │   │   ├── app.js
│   │   │   │   ├── main.js
│   │   │   │   ├── theme.js
│   │   │   │   ├── utils.js
│   │   │   │   ├── components/
│   │   │   │   └── pages/
│   │   │   ├── images/
│   │   │   └── fonts/
│   │   ├── router/          # 路由配置
│   │   │   └── index.js
│   │   ├── App.vue          # 根组件
│   │   └── main.js          # 入口文件
│   └── public/              # 公共文件
├── storage/                 # 文件存储
│   ├── uploads/             # 上传文件
│   ├── generated/           # 生成文件
│   └── models/              # AI模型文件
│       ├── yolo11*.pt       # YOLO模型
│       └── ...
├── templates/               # HTML模板（兼容性）
│   ├── base.html
│   └── index.html
├── docs/                    # 文档
├── scripts/                 # 脚本文件
├── README.md
└── doc.md
```

## API Endpoints

- `GET /` - Main dashboard
- `POST /image_qa` - Image question answering
- `POST /image_generation` - Generate images
- `POST /image_editing` - Edit images
- `POST /bounding_boxes` - Object detection
- `POST /image_segmentation` - Image segmentation
- `GET /api/features` - List all features

## Supported Models

### Vision & Analysis
- **gemini-2.0-flash** - Fast, versatile vision model
- **gemini-2.5-pro-exp-03-25** - Advanced segmentation model

### Image Generation
- **gemini-2.0-flash-exp-image-generation** - Creative image generation
- **imagen-3.0-generate-002** - High-quality photorealistic images

## Usage Examples

### Image Question Answering
1. Upload an image
2. Ask questions like:
   - "What objects can you see in this image?"
   - "Describe the colors and mood"
   - "Count the number of people"

### Image Generation
1. Enter a detailed prompt
2. Choose between Gemini or Imagen models
3. Examples:
   - "A majestic mountain landscape at sunset"
   - "A cute robot cat in a futuristic city"

### Image Editing
1. Upload an image to edit
2. Provide editing instructions:
   - "Add a stylish hat to the person"
   - "Change the background to a sunset"

### Object Detection
1. Upload an image
2. Specify what to detect (person, car, cat, etc.)
3. Get bounding box coordinates

### Image Segmentation
1. Upload an image
2. Specify what to segment
3. Get pixel-perfect masks with labels

## Configuration

Edit `config.py` or use environment variables:

```python
GEMINI_API_KEY = "your-api-key"
UPLOAD_FOLDER = "uploads"
GENERATED_FOLDER = "generated"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

## Requirements

- Python 3.8+
- Flask 3.0+
- google-genai 0.8+
- Pillow (PIL)
- Other dependencies in `requirements.txt`

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your `GEMINI_API_KEY` is set correctly
2. **File Upload Issues**: Check file size (max 16MB) and format
3. **Model Errors**: Some models may have usage limits or availability restrictions

### Error Handling

The app includes comprehensive error handling:
- File validation
- API error responses
- User-friendly error messages
- Fallback for failed operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with Google's Gemini API
- Based on official Gemini documentation examples
- Uses Bootstrap for responsive UI
- Font Awesome for icons
