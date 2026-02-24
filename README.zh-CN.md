# VedioZip

[English](README.md) | 简体中文

VedioZip 是一个开源的 Windows 本地视频转换工具，提供本地网页界面。

## 功能特性

- 支持单个视频文件转换
- 支持整个文件夹批量转换
- 可选择输出目录
- 可设置目标清晰度（例如 320p）
- 可设置输出后缀策略（默认按清晰度、无后缀、自定义后缀）
- 可设置 CRF、Preset、音频码率
- 提供实时转换进度
- 支持便携版 `.exe` 与安装版

## 快速开始

1. 创建或更新环境：

```powershell
conda env update -n vediozip-ffmpeg -f environment.yml --prune
```

2. 本地运行：

```powershell
.\run_dev.ps1
```

程序会自动打开浏览器界面。

## 下载使用

在 GitHub Releases 中下载以下任一文件：

- `VedioZip-portable-win64-<version>.zip`（便携版）
- `VedioZip-setup-win64-<version>.exe`（安装版）

## 本地打包

打包便携版：

```powershell
.\build_windows.ps1
```

输出：

- `dist/VedioZip.exe`
- `dist/ffmpeg.exe`
- `dist/ffprobe.exe`
- `dist/` 中的运行时 DLL 依赖

打包安装版（需先安装 Inno Setup）：

```powershell
choco install innosetup -y
.\build_installer.ps1 1.0.0
```

输出：

- `installer/Output/VedioZip-Setup-1.0.0.exe`

## GitHub 自动发布

推送版本标签后，GitHub Actions 会自动构建并上传发布资产：

```powershell
git tag v1.0.0
git push origin v1.0.0
```

工作流文件：

- `.github/workflows/release.yml`

## 故障排查

日志路径：

- 源码运行：`logs/vediozip.log`
- 打包运行：`dist/logs/vediozip.log`

如果转换失败，请优先查看并提供日志文件。

## 项目结构

- `launcher.py`：应用入口
- `server.py`：FastAPI 接口与静态资源托管
- `video_service.py`：转换任务逻辑
- `static/`：前端文件
- `build_windows.ps1`：便携版打包脚本
- `build_installer.ps1`：安装版打包脚本
- `installer/VedioZip.iss`：Inno Setup 配置

## 许可证

MIT
