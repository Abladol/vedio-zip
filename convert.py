import argparse
import shutil
import sys
from pathlib import Path

import ffmpeg


class ZhArgumentParser(argparse.ArgumentParser):
    """将 argparse 默认帮助中的 usage 文案替换为中文。"""

    def format_help(self) -> str:
        return super().format_help().replace("usage: ", "用法: ", 1)

    def format_usage(self) -> str:
        return super().format_usage().replace("usage: ", "用法: ", 1)


def build_output_path(input_path: Path, height: int) -> Path:
    """根据输入文件名生成默认输出路径，例如 01_320p.mp4。"""
    suffix = f"_{height}p"
    return input_path.with_name(f"{input_path.stem}{suffix}{input_path.suffix}")


def resolve_ffmpeg_path() -> Path | None:
    """定位 ffmpeg 可执行文件，兼容 conda 环境未激活的情况。"""
    in_path = shutil.which("ffmpeg")
    if in_path:
        return Path(in_path)

    candidates = [
        Path(sys.prefix) / "Library" / "bin" / "ffmpeg.exe",
        Path(sys.prefix) / "Scripts" / "ffmpeg.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def transcode_video(
    input_path: Path,
    output_path: Path,
    height: int,
    crf: int,
    preset: str,
    audio_bitrate: str,
    ffmpeg_cmd: Path,
) -> None:
    """使用 ffmpeg-python 执行视频转码。"""
    source = ffmpeg.input(str(input_path))
    video_stream = source.video.filter("scale", -2, height)
    pipeline = ffmpeg.output(
        video_stream,
        source.audio,
        str(output_path),
        vcodec="libx264",
        crf=crf,
        preset=preset,
        acodec="aac",
        audio_bitrate=audio_bitrate,
    )
    ffmpeg.run(pipeline, overwrite_output=True, cmd=str(ffmpeg_cmd))


def main() -> int:
    parser = ZhArgumentParser(
        description="使用 ffmpeg-python 将 MP4 转为 320p（或指定高度）。",
        add_help=False,
    )
    parser._positionals.title = "位置参数"
    parser._optionals.title = "可选参数"
    parser.add_argument("-h", "--help", action="help", help="显示帮助信息并退出")
    parser.add_argument("input", help="输入 MP4 路径，例如 E:\\01.mp4")
    parser.add_argument("--height", type=int, default=320, help="目标高度")
    parser.add_argument("--output", help="输出路径（可选）")
    parser.add_argument("--crf", type=int, default=23, help="视频 CRF 质量参数")
    parser.add_argument("--preset", default="medium", help="x264 编码预设")
    parser.add_argument("--audio-bitrate", default="128k", help="音频码率")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"未找到输入文件: {input_path}", file=sys.stderr)
        return 2

    output_path = Path(args.output) if args.output else build_output_path(input_path, args.height)
    ffmpeg_cmd = resolve_ffmpeg_path()
    if ffmpeg_cmd is None:
        print("未找到 ffmpeg 可执行文件，请确认环境中已安装 ffmpeg。", file=sys.stderr)
        return 3

    print(f"开始转换: {input_path} -> {output_path}")

    try:
        transcode_video(
            input_path=input_path,
            output_path=output_path,
            height=args.height,
            crf=args.crf,
            preset=args.preset,
            audio_bitrate=args.audio_bitrate,
            ffmpeg_cmd=ffmpeg_cmd,
        )
    except FileNotFoundError as exc:
        print(f"转换失败，未找到可执行文件: {exc}", file=sys.stderr)
        return 3
    except ffmpeg.Error as exc:
        error_text = exc.stderr.decode("utf-8", errors="replace") if exc.stderr else str(exc)
        print(f"转换失败:\n{error_text}", file=sys.stderr)
        return 3

    print(f"转换完成: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
