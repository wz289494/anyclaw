"""运行 cli_runner 工具并显示结果的脚本。"""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from tools.cli_runner import cli_runner
from utils.path import ensure_task_dirs
from utils.task_context import set_task_id


console = Console()


def main() -> None:
    args = sys.argv[1:]
    use_sandbox = False
    if args and args[0].strip() == "--sandbox":
        use_sandbox = True
        args = args[1:]

    task_id = None
    if use_sandbox:
        task_id = str(uuid.uuid4())
        set_task_id(task_id)
        ensure_task_dirs(task_id)
    else:
        set_task_id(None)

    raw_command = " ".join(args).strip() if args else "ls"

    console.print("[bold cyan]运行 cli_runner 工具[/bold cyan]")
    console.print(f"[dim]command: {raw_command}[/dim]")
    console.print()

    result_json = cli_runner.invoke({"command": raw_command})
    try:
        result = json.loads(result_json)
    except Exception:
        result = {"raw": result_json}

    result_str = json.dumps(result, ensure_ascii=False, indent=2)
    console.print(
        Panel(
            Syntax(result_str, "json", theme="monokai", line_numbers=False, word_wrap=True),
            title="[bold]cli_runner 输出[/bold]",
            border_style="green",
        )
    )

    console.print()
    if task_id:
        console.print(f"[dim]task_id: {task_id}[/dim]")
        console.print(f"[dim]sandbox: sandbox/{task_id}/[/dim]")


if __name__ == "__main__":
    main()
