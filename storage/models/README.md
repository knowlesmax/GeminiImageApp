# AI 模型目录

此目录包含用于目标检测和图像分割的 YOLO 模型文件。

## 🤖 当前支持的模型

### 🎯 目标检测模型
- `yolo11n.pt` - YOLOv11 Nano (~6MB) - 最快速度
- `yolo11s.pt` - YOLOv11 Small (~22MB) - 平衡性能
- `yolo11m.pt` - YOLOv11 Medium (~50MB) - 推荐使用
- `yolo11l.pt` - YOLOv11 Large (~144MB) - 高精度

### 🔍 图像分割模型
- `yolo11n-seg.pt` - YOLOv11 Nano 分割 (~7MB) - 最快速度
- `yolo11s-seg.pt` - YOLOv11 Small 分割 (~25MB) - 平衡性能
- `yolo11m-seg.pt` - YOLOv11 Medium 分割 (~52MB) - 推荐使用
- `yolo11l-seg.pt` - YOLOv11 Large 分割 (~147MB) - 高精度
- `yolo11x-seg.pt` - YOLOv11 Extra Large 分割 (~221MB) - 最高精度

## 📦 Git 版本控制

这些模型文件已从 Git 跟踪中**排除**，以保持仓库大小合理。`.gitignore` 文件包含：

```gitignore
# AI 模型文件被忽略
*.pt
*.pth
*.onnx
yolo*.pt
```

这意味着模型文件不会上传到您的 Git 仓库中。

## 🚀 自动下载

如果模型文件缺失，应用程序将在首次使用时自动从官方 YOLO 仓库下载它们。

### 下载过程
1. 应用启动时检测模型文件
2. 如果文件不存在，自动从 Ultralytics 官方源下载
3. 下载的模型保存到 `storage/models/` 目录
4. 后续使用直接加载本地模型

## 💾 存储要求

- **所有模型总大小**: 约 500MB
- **推荐可用空间**: 1GB+
- **网络要求**: 首次下载需要稳定网络连接

## ⚙️ 模型选择建议

### 🏃‍♂️ 追求速度
- 检测: `yolo11n.pt`
- 分割: `yolo11n-seg.pt`

### ⚖️ 平衡性能
- 检测: `yolo11s.pt` 或 `yolo11m.pt`
- 分割: `yolo11s-seg.pt` 或 `yolo11m-seg.pt`

### 🎯 追求精度
- 检测: `yolo11l.pt`
- 分割: `yolo11l-seg.pt` 或 `yolo11x-seg.pt`

## 🔧 故障排除

### 模型下载失败
```bash
# 手动删除损坏的模型文件
rm storage/models/yolo11n.pt

# 重启应用，会自动重新下载
python backend/run.py
```

### 磁盘空间不足
```bash
# 只保留必要的模型
rm storage/models/yolo11l*.pt
rm storage/models/yolo11x*.pt
```

### 网络连接问题
- 确保网络连接稳定
- 如在中国大陆，可能需要配置代理
- 可以手动从 [Ultralytics 官网](https://github.com/ultralytics/assets/releases) 下载模型文件
