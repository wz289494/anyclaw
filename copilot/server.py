from __future__ import annotations

import argparse
import json
import threading
import time
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen


ROOT_DIR = Path(__file__).resolve().parent


class CopilotHandler(SimpleHTTPRequestHandler):
    """Serve static copilot assets and expose runtime config."""

    def __init__(self, *args, api_base: str, directory: str, **kwargs):
        self.api_base = api_base.rstrip("/")
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:
        if self.path == "/config.json":
            payload = json.dumps({"apiBase": self.api_base}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        super().do_GET()

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def _api_health_url(api_base: str) -> str:
    return f"{api_base.rstrip('/')}/api/tools"


def _can_auto_start_api(api_base: str) -> bool:
    parsed = urlparse(api_base)
    return parsed.scheme in {"http", "https"} and parsed.hostname in {"127.0.0.1", "localhost", "0.0.0.0"}


def _is_api_ready(api_base: str, timeout: float = 1.0) -> bool:
    try:
        with urlopen(_api_health_url(api_base), timeout=timeout) as response:
            return 200 <= response.status < 500
    except (URLError, OSError, ValueError):
        return False


def _start_local_api(api_base: str) -> threading.Thread | None:
    if not _can_auto_start_api(api_base):
        return None
    parsed = urlparse(api_base)
    api_host = parsed.hostname or "127.0.0.1"
    api_port = parsed.port or 7000
    if api_host == "localhost":
        api_host = "127.0.0.1"
    print(f"未检测到 API，正在自动启动: {api_base}")
    try:
        from api.server import run_api_server
    except Exception as exc:
        raise RuntimeError(
            f"API 自动启动失败：{exc}。请先激活项目环境并安装依赖，例如执行 `pip install -r requirements.txt`。"
        ) from exc

    thread = threading.Thread(
        target=run_api_server,
        kwargs={"host": api_host, "port": api_port},
        daemon=True,
        name="anyclaw-local-api",
    )
    thread.start()
    return thread


def _ensure_api_running(api_base: str, auto_start: bool) -> threading.Thread | None:
    if _is_api_ready(api_base):
        print(f"API 已就绪: {api_base}")
        return None
    if not auto_start:
        return None
    thread = _start_local_api(api_base)
    if thread is None:
        return None
    for _ in range(30):
        if _is_api_ready(api_base):
            print(f"API 自动启动完成: {api_base}")
            return thread
        time.sleep(0.5)
    raise RuntimeError("API 自动启动超时，请检查模型配置或端口占用")


def run_copilot_server(
    host: str = "127.0.0.1",
    port: int = 7001,
    api_base: str = "http://127.0.0.1:7000",
    open_browser: bool = True,
    auto_start_api: bool = True,
) -> None:
    _ensure_api_running(api_base, auto_start=auto_start_api)
    handler = partial(CopilotHandler, api_base=api_base, directory=str(ROOT_DIR))
    server = ThreadingHTTPServer((host, port), handler)
    url = f"http://{host}:{port}"
    print(f"Copilot 已启动: {url}")
    print(f"API 地址: {api_base}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="AnyClaw browser copilot")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7001)
    parser.add_argument("--api-base", default="http://127.0.0.1:7000")
    parser.add_argument("--no-open", action="store_true", help="Do not open a browser tab")
    parser.add_argument("--no-api-autostart", action="store_true", help="Do not auto-start local API")
    args = parser.parse_args()
    run_copilot_server(
        host=args.host,
        port=args.port,
        api_base=args.api_base,
        open_browser=not args.no_open,
        auto_start_api=not args.no_api_autostart,
    )


if __name__ == "__main__":
    main()
