"""清理工具：清除 memory 和 sandbox 中的内容。"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Confirm

from utils.path import get_stm_dir, get_sandbox_dir

console = Console()


def _is_protected_session_file(item_name: str, exclude_task_id: Optional[str]) -> bool:
    """判断 memory/STM 下文件是否属于需要保留的当前会话。"""
    if not exclude_task_id:
        return False
    if item_name == f"{exclude_task_id}.json":
        return True
    # 兼容传入短 task_id 的情况：保护前缀匹配到的会话文件
    return item_name.endswith(".json") and item_name[:-5].startswith(exclude_task_id)


def _is_protected_sandbox_item(item_name: str, exclude_task_id: Optional[str]) -> bool:
    """判断 sandbox 下条目是否属于需要保留的当前会话。"""
    if not exclude_task_id:
        return False
    if item_name == exclude_task_id:
        return True
    # 兼容传入短 task_id 的情况：保护前缀匹配到的任务目录/文件
    return item_name.startswith(exclude_task_id)


def clear_memory_and_sandbox(exclude_task_id: Optional[str] = None) -> None:
    """
    清除 memory/STM 下的所有内容以及 sandbox 除测试外的所有文件夹
    """
    stm_dir = get_stm_dir()
    sandbox_dir = get_sandbox_dir()
    
    cleared_items = []
    
    # 清除 memory/STM 下的所有内容（可排除当前会话）
    if stm_dir.exists():
        for item in stm_dir.iterdir():
            if _is_protected_session_file(item.name, exclude_task_id):
                continue
            if item.is_file():
                item.unlink()
                cleared_items.append(f"文件: {item.name}")
            elif item.is_dir():
                shutil.rmtree(item)
                cleared_items.append(f"文件夹: {item.name}")
    
    # 清除 sandbox 除测试和当前会话外的所有条目（文件/文件夹）
    if sandbox_dir.exists():
        for item in sandbox_dir.iterdir():
            if item.name == "测试":
                continue
            if _is_protected_sandbox_item(item.name, exclude_task_id):
                continue
            if item.is_dir():
                shutil.rmtree(item)
                cleared_items.append(f"sandbox/{item.name}")
            elif item.is_file():
                item.unlink()
                cleared_items.append(f"sandbox/{item.name}")
    
    if cleared_items:
        console.print(f"[green]已清除 {len(cleared_items)} 项：[/green]")
        for item in cleared_items[:10]:  # 只显示前10项
            console.print(f"  - {item}")
        if len(cleared_items) > 10:
            console.print(f"  ... 还有 {len(cleared_items) - 10} 项")
    else:
        console.print("[yellow]没有需要清除的内容[/yellow]")


def confirm_and_clear(exclude_task_id: Optional[str] = None) -> None:
    """确认后清除 memory 和 sandbox。"""
    console.print("[yellow]警告：此操作将清除以下内容：[/yellow]")
    console.print("  - memory/STM 下的所有文件和文件夹")
    console.print("  - sandbox 下除'测试'外的所有文件夹")
    console.print()
    
    if exclude_task_id:
        console.print(f"  - 当前会话将保留: {exclude_task_id}")
        console.print("  - 当前会话对应的 sandbox 目录将保留")
        console.print()

    if Confirm.ask("[bold red]确定要执行清除操作吗？[/bold red]", default=False):
        clear_memory_and_sandbox(exclude_task_id=exclude_task_id)
    else:
        console.print("[cyan]已取消清除操作[/cyan]")
