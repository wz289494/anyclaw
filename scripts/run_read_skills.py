"""运行 read_skills 工具并显示结果的脚本。"""

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

from tools.read_skills import read_skills
from utils.path import ensure_task_dirs
from utils.task_context import set_task_id


console = Console()


def main() -> None:
    task_id = str(uuid.uuid4())
    set_task_id(task_id)
    ensure_task_dirs(task_id)

    skill_name = sys.argv[1].strip() if len(sys.argv) > 1 else "baidu-search"

    console.print("[bold cyan]运行 read_skills 工具[/bold cyan]")
    console.print(f"[dim]skill name: {skill_name}[/dim]")
    console.print()

    result_json = read_skills.invoke({"name": skill_name})
    try:
        result = json.loads(result_json)
    except Exception:
        result = {"raw": result_json}

    result_str = json.dumps(result, ensure_ascii=False, indent=2)
    console.print(
        Panel(
            Syntax(result_str, "json", theme="monokai", line_numbers=False, word_wrap=True),
            title="[bold]read_skills 输出[/bold]",
            border_style="green",
        )
    )

    console.print()
    console.print(f"[dim]task_id: {task_id}[/dim]")
    console.print(f"[dim]sandbox: sandbox/{task_id}/[/dim]")


if __name__ == "__main__":
    main()
