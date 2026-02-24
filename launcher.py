from __future__ import annotations

import socket
import threading
import time
import webbrowser

import uvicorn

from server import app


def _find_available_port(host: str, start_port: int = 8765, max_tries: int = 50) -> int:
    for port in range(start_port, start_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if sock.connect_ex((host, port)) != 0:
                return port
    raise RuntimeError("未找到可用端口，请关闭占用端口的程序后重试。")


def _wait_and_open_browser(url: str, host: str, port: int) -> None:
    for _ in range(60):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex((host, port)) == 0:
                webbrowser.open(url)
                return
        time.sleep(0.2)


def main() -> None:
    host = "127.0.0.1"
    port = _find_available_port(host=host)
    url = f"http://{host}:{port}"

    threading.Thread(target=_wait_and_open_browser, args=(url, host, port), daemon=True).start()
    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":
    main()
