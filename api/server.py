from __future__ import annotations

import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Optional

import yaml
from agent.reactagent import AGENT_TOOLS, stream
from cli.tools_ui import _extract_description
from model.factory import list_thinking_models
from utils.path import ensure_task_dirs, get_config_path
from utils.prompt_loader import list_local_skills
from utils.session_manager import get_session_manager
from utils.message_utils import messages_from_session_data
from cli.clear_utils import clear_memory_and_sandbox


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _text_response(handler: BaseHTTPRequestHandler, status: int, text: str) -> None:
    data = (text or "").encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "text/markdown; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _read_body(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    try:
        data = json.loads(raw.decode("utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _normalize_task_id(value: Any) -> str:
    raw = str(value or "").strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1].strip()
    return raw


def _markdown_tools() -> str:
    lines = ["# Tools", ""]
    for tool in AGENT_TOOLS:
        tool_name = tool.name if hasattr(tool, "name") else str(tool)
        desc = ""
        if hasattr(tool, "description"):
            desc = tool.description or ""
        elif hasattr(tool, "__doc__") and tool.__doc__:
            desc = _extract_description(tool.__doc__)
        desc = desc.strip().replace("\n", " ")
        lines.append(f"- **{tool_name}**：{desc or '无描述'}")
    return "\n".join(lines).strip()


def _markdown_skills() -> str:
    items = list_local_skills()
    if not items:
        return "# Skills\n\n未找到可用的 skills"
    lines = ["# Skills", "", "| Name | Description | Folder |", "|---|---|---|"]
    for item in items:
        name = item.get("name", "")
        desc = item.get("description", "").replace("\n", " ")
        folder = item.get("folder", "")
        lines.append(f"| {name} | {desc} | skills/{folder} |")
    return "\n".join(lines).strip()


def _markdown_models() -> str:
    cfg_path = get_config_path("model.yaml")
    if not cfg_path.exists():
        return "# Models\n\n模型配置文件不存在"
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    except Exception:
        return "# Models\n\n无法读取模型配置文件"
    model_descriptions = {
        "main": "主流程模型：作为 ReAct Agent 的底座",
        "text_generation": "文本生成模型：用于文本生成任务",
        "element_extraction": "元素提取模型：用于从文本中提取结构化信息",
        "code_generation": "代码生成模型：用于代码生成任务",
    }
    lines = ["# Models", "", "| 场景 | 用途 | Provider | Model |", "|---|---|---|---|"]
    for scene, info in config.items():
        if not isinstance(info, dict):
            continue
        provider = info.get("provider", "")
        model = info.get("model", "")
        purpose = model_descriptions.get(scene, "自定义模型场景")
        lines.append(f"| {scene} | {purpose} | {provider} | {model} |")
    thinking = list_thinking_models()
    if thinking:
        lines.append("")
        lines.append("## Thinking Models")
        for m in thinking:
            lines.append(f"- {m}")
    return "\n".join(lines).strip()


def _list_task_ids() -> List[str]:
    session_manager = get_session_manager()
    sessions = session_manager.list_sessions(limit=10000)
    return [s.get("task_id", "") for s in sessions if s.get("task_id")]


def _create_session() -> str:
    session_manager = get_session_manager()
    task_id = session_manager.create_session("新会话")
    ensure_task_dirs(task_id)
    return task_id


def _run_agent_stream(task_id: str, query: str, handler: BaseHTTPRequestHandler) -> None:
    session_manager = get_session_manager()
    session_manager.add_message(task_id, "user", query)
    session_data = session_manager.load_session(task_id)
    previous_messages = messages_from_session_data(session_data) if session_data else []
    handler.send_response(200)
    handler.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    final_text = ""
    for item in stream(query, task_id=task_id, previous_messages=previous_messages):
        if not isinstance(item, dict):
            continue
        event_type = item.get("type", "")
        payload: Dict[str, Any] = {"type": event_type}
        if event_type == "token":
            payload["content"] = item.get("content", "")
            final_text = item.get("accumulated", final_text)
        elif event_type == "tool_call":
            payload["tool_name"] = item.get("tool_name", "")
            payload["args"] = item.get("args", {})
        elif event_type == "tool_result":
            payload["tool_name"] = item.get("tool_name", "")
            payload["result"] = item.get("result", "")
            run_id = item.get("run_id", "")
            session_manager.add_message(task_id, "tool", payload["result"], tool_name=payload["tool_name"], tool_call_id=run_id)
        elif event_type == "message":
            msg = item.get("message")
            content = getattr(msg, "content", "") if msg else ""
            final_text = content or final_text
        elif event_type == "state_update":
            payload["state"] = item.get("state", {})
        data = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
        try:
            handler.wfile.write(data)
            handler.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            return
    session_manager.add_message(task_id, "assistant", final_text)
    done = json.dumps({"type": "final", "content": final_text, "task_id": task_id}, ensure_ascii=False).encode("utf-8")
    try:
        handler.wfile.write(done + b"\n")
        handler.wfile.flush()
    except (BrokenPipeError, ConnectionResetError):
        return


class ApiHandler(BaseHTTPRequestHandler):
    def _route(self) -> tuple[str, Dict[str, str]]:
        parsed = urllib.parse.urlparse(self.path)
        params = dict(urllib.parse.parse_qsl(parsed.query))
        return parsed.path, params

    def do_GET(self) -> None:
        path, params = self._route()
        if path == "/api/tools" or params.get("type") == "tools":
            md = _markdown_tools()
            _text_response(self, 200, md)
            return
        if path == "/api/models" or params.get("type") == "models":
            md = _markdown_models()
            _text_response(self, 200, md)
            return
        if path == "/api/skills" or params.get("type") == "skills":
            md = _markdown_skills()
            _text_response(self, 200, md)
            return
        if path == "/api/memory" or params.get("type") == "memory":
            task_ids = _list_task_ids()
            _json_response(self, 200, {"type": "memory", "task_ids": task_ids})
            return
        if path == "/api/session":
            task_id = _normalize_task_id(params.get("task_id"))
            if not task_id:
                _json_response(self, 400, {"error": "task_id is required"})
                return
            session_manager = get_session_manager()
            session_data = session_manager.load_session(task_id)
            if not session_data:
                _json_response(self, 404, {"error": "task_id not found", "task_id": task_id})
                return
            _json_response(self, 200, {"task_id": task_id, "messages": session_data.get("messages", [])})
            return
        _json_response(self, 404, {"error": "not_found"})

    def do_POST(self) -> None:
        path, params = self._route()
        body = _read_body(self)
        req_type = body.get("type") or params.get("type")
        if path == "/api/new" or req_type == "new":
            task_id = _create_session()
            _json_response(self, 200, {"type": "new", "task_id": task_id})
            return
        if path == "/api/clear" or req_type == "clear":
            clear_memory_and_sandbox()
            _json_response(self, 200, {"type": "clear", "success": True})
            return
        if path == "/api/agent" or req_type == "agent":
            task_id = _normalize_task_id(body.get("task_id") or body.get("taskid"))
            query = body.get("query") or body.get("prompt") or ""
            if not task_id or not query:
                _json_response(self, 400, {"error": "task_id and query are required"})
                return
            session_manager = get_session_manager()
            if not session_manager.load_session(task_id):
                _json_response(self, 404, {"error": "task_id not found", "task_id": task_id})
                return
            _run_agent_stream(task_id, str(query), self)
            return
        _json_response(self, 404, {"error": "not_found"})

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def run_api_server(host: str = "0.0.0.0", port: int = 7000) -> None:
    server = ThreadingHTTPServer((host, port), ApiHandler)
    try:
        server.serve_forever()
    finally:
        server.server_close()
