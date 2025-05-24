# AI Models Directory

This directory contains YOLO model files used for object detection and image segmentation.

## Current Models

### Object Detection Models
- `yolo11n.pt` - YOLOv11 Nano (~6MB)
- `yolo11s.pt` - YOLOv11 Small (~22MB)
- `yolo11m.pt` - YOLOv11 Medium (~50MB)
- `yolo11l.pt` - YOLOv11 Large (~144MB)

### Image Segmentation Models
- `yolo11n-seg.pt` - YOLOv11 Nano Segmentation (~7MB)
- `yolo11s-seg.pt` - YOLOv11 Small Segmentation (~25MB)
- `yolo11m-seg.pt` - YOLOv11 Medium Segmentation (~52MB)
- `yolo11l-seg.pt` - YOLOv11 Large Segmentation (~147MB)
- `yolo11x-seg.pt` - YOLOv11 Extra Large Segmentation (~221MB)

## Git Tracking

By default, these model files are **tracked by Git**. If you want to exclude them from version control (recommended for large repositories), uncomment the relevant lines in `.gitignore`:

```gitignore
# Uncomment these lines to ignore model files:
# *.pt
# *.pth
# *.onnx
```

## Auto-Download

If model files are missing, the application will automatically download them from the official YOLO repository on first use.

## Storage Requirements

Total size of all models: ~500MB

Consider using Git LFS (Large File Storage) for these files if working in a team environment.
