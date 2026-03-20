"""命令行执行工具：在受限白名单内执行命令并返回输出。"""

from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from utils.path import ensure_task_dirs, get_project_root
from utils.task_context import get_task_id


_ALLOWED_BINARIES: set[str] = {
    "python3",
    "python",
    "ls",
    "pwd",
    "cat",
    "echo",
    "find",
    "grep",
    "head",
    "tail",
    "wc",
    "cd",
}


def _normalize_cwd(argv: List[str]) -> Path:
    if not argv:
        return get_project_root()
    if argv[0] not in {"python3", "python"}:
        return get_project_root()
    if len(argv) < 2:
        return get_project_root()
    script = argv[1]
    task_id = get_task_id()
    if task_id and script.endswith(".py") and ("/" not in script and "\\" not in script):
        project_root = get_project_root().resolve()
        sandbox_dir = (project_root / "sandbox" / task_id).resolve()
        if (sandbox_dir / script).is_file():
            return sandbox_dir
    if task_id and not Path(script).is_absolute():
        parts = Path(script).parts
        if len(parts) >= 2 and parts[0] == "sandbox" and parts[1] == task_id:
            return get_project_root()
    try:
        p = Path(script)
    except Exception:
        return get_project_root()
    project_root = get_project_root().resolve()
    full = p.resolve() if p.is_absolute() else (project_root / p).resolve()
    task_id = task_id or get_task_id()
    if not task_id:
        return get_project_root()
    ensure_task_dirs(task_id)
    sandbox_dir = (project_root / "sandbox" / task_id).resolve()
    try:
        full.relative_to(sandbox_dir)
        return sandbox_dir
    except Exception:
        return get_project_root()


def _truncate(text: str, limit: int) -> tuple[str, bool]:
    """截断输出文本以避免返回过大。"""
    if limit <= 0:
        return "", True
    if not text:
        return "", False
    if len(text) <= limit:
        return text, False
    return text[:limit], True


def _is_allowed_python_invocation(argv: List[str]) -> bool:
    """限制 python 仅允许运行仓库内 scripts/skills 或当前任务 sandbox 下的 .py 文件。"""
    if not argv:
        return False
    if len(argv) < 2:
        return False

    if argv[1] in {"-c", "-m"}:
        return False

    script = argv[1]
    if not script.endswith(".py"):
        return False
    task_id = get_task_id()
    if task_id and ("/" not in script and "\\" not in script):
        project_root = get_project_root().resolve()
        sandbox_dir = (project_root / "sandbox" / task_id).resolve()
        if (sandbox_dir / script).is_file():
            return True

    try:
        p = Path(script)
    except Exception:
        return False

    project_root = get_project_root().resolve()
    full = p.resolve() if p.is_absolute() else (project_root / p).resolve()

    try:
        rel = full.relative_to(project_root)
    except Exception:
        return False

    parts = rel.parts
    if not parts:
        return False
    if parts[0] in {"skills", "scripts"}:
        return full.is_file()
    if parts[0] == "sandbox":
        task_id = get_task_id()
        if not task_id:
            return False
        if len(parts) < 2 or parts[1] != task_id:
            return False
        return full.is_file()

    return False


def _validate_command(argv: List[str]) -> Optional[str]:
    """校验命令是否允许执行，返回错误信息或 None。"""
    if not argv:
        return "命令为空"

    program = (argv[0] or "").strip()
    if not program:
        return "命令为空"

    if program not in _ALLOWED_BINARIES:
        allowed = ", ".join(sorted(_ALLOWED_BINARIES))
        return f"不允许执行该命令: {program}. 允许的命令: {allowed}"

    if program in {"python3", "python"} and not _is_allowed_python_invocation(argv):
        return "python 仅允许运行仓库内 skills/、scripts/ 或 sandbox/<task_id>/ 下的 .py 文件（支持相对路径或仓库内绝对路径），且不允许 -c / -m"

    return None


@tool
def cli_runner(command: str, timeout_sec: int = 600, max_output_chars: int = 50000, stdin: Optional[str] = None) -> str:
    """
    描述：受限命令行执行工具，输入命令字符串，输出为命令行 stdout/stderr（JSON）。
    使用时机：当需要运行某个 skill 的脚本、列目录、查看文件内容等时调用。
    输入：
    - command（必填）：要执行的命令字符串（例如 "ls -la" 或 "python3 skills/baidu-search/scripts/search.py '{...}'"）。
    - timeout_sec（可选）：超时时间（秒），默认 60。
    - max_output_chars（可选）：最大输出字符数，默认 12000（超过会截断）。
    - stdin（可选）：标准输入内容（不支持管道/重定向时可用该字段喂给程序）。
    输出：JSON字符串，包含以下字段：
    - command：原始命令
    - argv：解析后的参数数组
    - cwd：执行目录
    - exit_code：退出码
    - stdout：标准输出（可能截断）
    - stderr：标准错误（可能截断）
    - output：stdout+stderr 合并输出（可能截断）
    - truncated：是否发生截断
    """
    raw = (command or "").strip()
    if not raw:
        return json.dumps({"error": "command 不能为空", "command": command}, ensure_ascii=False)

    if any(x in raw for x in ["|", "&&", "||", ";", ">", "<", "`", "$("]):
        return json.dumps(
            {
                "error": "不支持 shell 管道/重定向/复合命令，请改用单条命令；如需输入内容请使用 stdin 参数",
                "command": raw,
            },
            ensure_ascii=False,
        )

    try:
        argv = shlex.split(raw)
    except Exception as e:
        return json.dumps({"error": f"命令解析失败: {e}", "command": raw}, ensure_ascii=False)

    error = _validate_command(argv)
    if error:
        return json.dumps({"error": error, "command": raw, "argv": argv}, ensure_ascii=False)

    cwd = _normalize_cwd(argv)
    try:
        proc = subprocess.run(
            argv,
            cwd=str(cwd),
            capture_output=True,
            input=stdin,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=max(1, int(timeout_sec)),
        )
    except subprocess.TimeoutExpired:
        return json.dumps(
            {"error": "命令执行超时", "command": raw, "argv": argv, "cwd": str(cwd)},
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps(
            {"error": f"命令执行失败: {e}", "command": raw, "argv": argv, "cwd": str(cwd)},
            ensure_ascii=False,
        )

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    combined = (stdout + ("\n" if stdout and stderr else "") + stderr).strip("\n")

    stdout_t, t1 = _truncate(stdout, max_output_chars)
    stderr_t, t2 = _truncate(stderr, max_output_chars)
    combined_t, t3 = _truncate(combined, max_output_chars)

    return json.dumps(
        {
            "command": raw,
            "argv": argv,
            "cwd": str(cwd),
            "exit_code": int(proc.returncode),
            "stdout": stdout_t,
            "stderr": stderr_t,
            "output": combined_t,
            "truncated": bool(t1 or t2 or t3),
        },
        ensure_ascii=False,
    )
