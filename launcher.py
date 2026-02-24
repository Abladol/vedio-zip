from __future__ import annotations

import socket
import sys
import threading
import time
import traceback
import webbrowser

import uvicorn

from app_logging import get_log_file_path, get_logger, setup_logging
from server import app


def _find_available_port(host: str, start_port: int = 8765, max_tries: int = 50) -> int:
    for port in range(start_port, start_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if sock.connect_ex((host, port)) != 0:
                return port
    raise RuntimeError("未找到可用端口，请关闭占用端口的程序后重试。")


def _wait_and_open_browser(url: str, host: str, port: int, logger_name: str = "vediozip.launcher") -> None:
    logger = get_logger(logger_name)
    for _ in range(60):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex((host, port)) == 0:
                logger.info("Open browser: %s", url)
                webbrowser.open(url)
                return
        time.sleep(0.2)
    logger.warning("Browser auto-open timeout. URL=%s", url)


def _install_global_exception_hooks(logger_name: str = "vediozip.launcher") -> None:
    logger = get_logger(logger_name)

    def _sys_hook(exc_type, exc_value, exc_tb) -> None:
        logger.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_tb))

    def _thread_hook(args: threading.ExceptHookArgs) -> None:
        logger.error(
            "Unhandled thread exception in %s",
            args.thread.name if args.thread else "unknown-thread",
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    sys.excepthook = _sys_hook
    threading.excepthook = _thread_hook


def main() -> None:
    log_file = setup_logging()
    logger = get_logger("vediozip.launcher")
    _install_global_exception_hooks()

    host = "127.0.0.1"
    port = _find_available_port(host=host)
    url = f"http://{host}:{port}"

    logger.info("Launcher start. host=%s port=%s log_file=%s", host, port, log_file)
    threading.Thread(target=_wait_and_open_browser, args=(url, host, port), daemon=True).start()

    try:
        # Windowed executable may not have usable stdio streams.
        # Disable uvicorn default log config to avoid formatter/isatty errors.
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="warning",
            log_config=None,
            access_log=False,
        )
    except Exception:
        logger.error("Launcher crashed.\n%s", traceback.format_exc())
        logger.error("See log file for details: %s", get_log_file_path())
        raise


if __name__ == "__main__":
    main()
