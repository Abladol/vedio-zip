# VedioZip

本项目是一个可在 Windows 本地运行的视频转换工具，采用前后端分离结构：
- 前端：`static/` 下的网页界面（路径选择、参数设置、进度条）
- 后端：FastAPI 服务（任务管理、转码执行、进度查询）

## 功能
- 选择单个视频文件转换
- 选择整个文件夹批量转换（递归扫描常见视频格式）
- 选择输出目录
- 自定义目标清晰度（默认 320p）
- 自定义编码参数（CRF、Preset、音频码率）
- 显示转换状态和进度条

## 项目结构
- `launcher.py`：应用入口，启动本地服务并自动打开浏览器
- `server.py`：FastAPI 接口与静态页面托管
- `video_service.py`：转换任务管理与 ffmpeg 进度解析
- `static/`：前端页面（HTML/CSS/JS）
- `build_windows.ps1`：Windows 一键打包脚本
- `run_dev.ps1`：开发环境一键运行脚本
- `convert.py`：命令行转换脚本（保留）

## 环境安装
```powershell
conda env update -n vediozip-ffmpeg -f environment.yml --prune
```

如果你还没有该环境：
```powershell
conda env create -f environment.yml
```

## 本地运行（前后端）
```powershell
.\run_dev.ps1
```

或：
```powershell
conda run -n vediozip-ffmpeg python launcher.py
```

启动后会自动打开浏览器页面。

## Windows 一键打包
```powershell
.\build_windows.ps1
```

打包后输出在 `dist/`：
- `dist/VedioZip.exe`
- `dist/ffmpeg.exe`
- `dist/ffprobe.exe`

双击 `VedioZip.exe` 即可运行。

## 接口说明（简要）
- `POST /api/pick-path`：打开系统对话框选择输入/输出路径
- `POST /api/start`：创建并启动转换任务
- `GET /api/jobs/{job_id}`：查询任务进度与状态
