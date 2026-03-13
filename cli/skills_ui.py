"""Skills 列表显示：扫描 skills/*/SKILL.md 并展示 name 与 description。"""

from __future__ import annotations

from typing import Dict, List

from rich.console import Console
from rich.table import Table

from utils.prompt_loader import list_local_skills


console = Console()


def show_skills_list() -> None:
    """显示当前仓库 skills 目录下可用的 skills（name/description）。"""
    skill_items: List[Dict[str, str]] = list_local_skills()
    if not skill_items:
        console.print("[yellow]未找到可用的 skills（缺少或无法解析 SKILL.md）。[/yellow]")
        return

    table = Table(
        title="[bold cyan]Skills 列表[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
        border_style="cyan",
        row_styles=["", "dim"],
    )
    table.add_column("Name", style="green", width=22, no_wrap=True)
    table.add_column("Description", style="white", width=70)
    table.add_column("目录", style="dim", width=26, no_wrap=True)

    for item in skill_items:
        table.add_row(
            item.get("name", ""),
            item.get("description", ""),
            f"skills/{item.get('folder', '')}",
        )

    console.print()
    console.print(table)
    console.print()
