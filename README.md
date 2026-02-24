# 320p 视频转换工具

将 720p 或更高分辨率的 MP4 视频转为 320p（等比缩放），输出文件名自动追加 `_320p`。

## 技术实现
- 使用 Python 脚本实现完整流程
- 使用 `ffmpeg-python` 作为调用接口
- 由 `ffmpeg` 完成底层编码

## 依赖
- Anaconda / Miniconda
- `python`
- `ffmpeg`
- `ffmpeg-python`

## 安装环境
```powershell
conda env create -f environment.yml
```

如果环境已存在，建议更新并清理无用包：
```powershell
conda env update -n vediozip-ffmpeg -f environment.yml --prune
```

## 使用方法
```powershell
conda run -n vediozip-ffmpeg python convert.py E:\01.mp4
```

输出示例：
`E:\01_320p.mp4`

## 可选参数
```powershell
conda run -n vediozip-ffmpeg python convert.py E:\01.mp4 --height 320 --crf 23 --preset medium --audio-bitrate 128k
```
