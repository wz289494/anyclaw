"""CLI 显示相关的辅助函数：使用 Rich 进行美化输出。"""

from __future__ import annotations

from typing import Any
from datetime import datetime
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.syntax import Syntax
import json
import re

# 创建全局 Console 实例
console = Console()


def _safe_for_console(text: str) -> str:
    if not text:
        return ""
    text = text.replace("•", "-").replace("👇", "↓")
    encoding = getattr(getattr(console, "file", None), "encoding", None) or "utf-8"
    try:
        return text.encode(encoding, errors="replace").decode(encoding, errors="replace")
    except Exception:
        return text.encode("utf-8", errors="replace").decode("utf-8", errors="replace")

def print_icon() -> None:
    """打印 ANYCLAW 项目的 ASCII 图标（使用 Rich）"""
    logo_text = Text()

    # A
    logo_text.append("   █████╗   ", style="magenta")
    # N
    logo_text.append("███╗  ██╗", style="yellow")
    logo_text.append("  ")
    # Y
    logo_text.append("██╗   ██╗", style="green")
    logo_text.append("  ")
    # C
    logo_text.append(" ██████╗ ", style="cyan")
    logo_text.append("  ")
    # L
    logo_text.append("██╗      ", style="blue")
    logo_text.append("  ")
    # A
    logo_text.append(" █████╗ ", style="red")
    logo_text.append("  ")
    # W
    logo_text.append("██╗    ██╗", style="magenta")
    logo_text.append("\n")

    # 第二行
    logo_text.append("  ██╔══██╗  ", style="magenta")
    logo_text.append("████╗ ██║", style="yellow")
    logo_text.append("  ")
    logo_text.append("╚██╗ ██╔╝", style="green")
    logo_text.append("  ")
    logo_text.append("██╔════╝ ", style="cyan")
    logo_text.append("  ")
    logo_text.append("██║      ", style="blue")
    logo_text.append("  ")
    logo_text.append("██╔══██╗", style="red")
    logo_text.append("  ")
    logo_text.append("██║    ██║", style="magenta")
    logo_text.append("\n")

    # 第三行
    logo_text.append("  ███████║  ", style="magenta")
    logo_text.append("██╔██╗██║", style="yellow")
    logo_text.append("  ")
    logo_text.append(" ╚████╔╝ ", style="green")
    logo_text.append("  ")
    logo_text.append("██║      ", style="cyan")
    logo_text.append("  ")
    logo_text.append("██║      ", style="blue")
    logo_text.append("  ")
    logo_text.append("███████║", style="red")
    logo_text.append("  ")
    logo_text.append("██║ █╗ ██║", style="magenta")
    logo_text.append("\n")

    # 第四行
    logo_text.append("  ██╔══██║  ", style="magenta")
    logo_text.append("██║╚████║", style="yellow")
    logo_text.append("  ")
    logo_text.append("  ╚██╔╝  ", style="green")
    logo_text.append("  ")
    logo_text.append("██║      ", style="cyan")
    logo_text.append("  ")
    logo_text.append("██║      ", style="blue")
    logo_text.append("  ")
    logo_text.append("██╔══██║", style="red")
    logo_text.append("  ")
    logo_text.append("██║███╗██║", style="magenta")
    logo_text.append("\n")

    # 第五行
    logo_text.append("  ██║  ██║  ", style="magenta")
    logo_text.append("██║ ╚███║", style="yellow")
    logo_text.append("  ")
    logo_text.append("   ██║   ", style="green")
    logo_text.append("  ")
    logo_text.append("╚██████╗ ", style="cyan")
    logo_text.append("  ")
    logo_text.append("███████╗ ", style="blue")
    logo_text.append("  ")
    logo_text.append("██║  ██║", style="red")
    logo_text.append("  ")
    logo_text.append("╚███╔███╔╝", style="magenta")
    logo_text.append("\n")

    # 第六行
    logo_text.append("  ╚═╝  ╚═╝  ", style="magenta")
    logo_text.append("╚═╝  ╚══╝", style="yellow")
    logo_text.append("  ")
    logo_text.append("   ╚═╝   ", style="green")
    logo_text.append("  ")
    logo_text.append(" ╚═════╝ ", style="cyan")
    logo_text.append("  ")
    logo_text.append("╚══════╝ ", style="blue")
    logo_text.append("  ")
    logo_text.append("╚═╝  ╚═╝", style="red")
    logo_text.append("  ")
    logo_text.append(" ╚══╝╚══╝ ", style="magenta")

    console.print(logo_text)
    

def print_welcome() -> None:
    """打印欢迎信息和可用命令（使用 Rich）"""
    console.print("[bold white]欢迎使用 AnyClaw - Agent智能助手[/bold white]")
    console.print()
    console.print("[yellow]可用命令：[/yellow]")
    console.print("  [cyan]/new[/cyan]     - 开启新的会话")
    console.print("  [cyan]/memory[/cyan]  - 查看并恢复之前的会话")
    console.print("  [cyan]/models[/cyan]  - 查看所有模型配置")
    console.print("  [cyan]/tools[/cyan]   - 查看所有可用工具")
    console.print("  [cyan]/skills[/cyan]  - 查看所有可用 skills")
    console.print("  [cyan]/clear[/cyan]   - 清除 memory 和 sandbox")
    console.print("  [cyan]/exit[/cyan]    - 退出程序")
    console.print()


def print_token_usage(step_name: str, prompt_tokens: int, completion_tokens: int, total_tokens: int) -> None:
    """
    打印 token 使用信息
    
    Args:
        step_name: 步骤名称
        prompt_tokens: Prompt tokens
        completion_tokens: Completion tokens
        total_tokens: 总 tokens
    """
    console.print(
        f"[dim]Token 使用 ({step_name}): "
        f"Prompt={prompt_tokens}, "
        f"Completion={completion_tokens}, "
        f"Total={total_tokens}[/dim]"
    )


def format_timestamp() -> str:
    """返回格式化的时间戳"""
    return datetime.now().strftime("%H:%M:%S")


def print_status(message: str, status_type: str = "info") -> None:
    """
    打印状态信息（使用 Rich）
    
    Args:
        message: 状态消息
        status_type: 状态类型 ('info', 'success', 'warning', 'error', 'tool')
    """
    timestamp = format_timestamp()
    
    styles = {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red",
        "tool": "magenta",
    }
    
    style = styles.get(status_type, "white")
    console.print(f"[dim][{timestamp}][/dim] [{style}]{message}[/{style}]")


def print_tool_call(tool_name: str, args: dict[str, Any] | None = None) -> None:
    """
    打印工具调用信息（使用 Rich）
    
    Args:
        tool_name: 工具名称
        args: 工具参数
    """
    timestamp = format_timestamp()
    console.print(f"\n[dim][{timestamp}][/dim] [bold magenta]正在调用工具:[/bold magenta] [cyan]{tool_name}[/cyan]")
    if args:
        # 对每个参数值进行截断，确保所有参数都能显示
        MAX_VALUE_LENGTH = 150 
        truncated_args = {}
        for key, value in args.items():
            if isinstance(value, str):
                if len(value) > MAX_VALUE_LENGTH:
                    truncated_args[key] = value[:MAX_VALUE_LENGTH] + "..."
                else:
                    truncated_args[key] = value
            elif isinstance(value, (dict, list)):
                # 对于复杂类型，转换为字符串后截断（保持为字符串格式，避免 JSON 解析错误）
                value_str = json.dumps(value, ensure_ascii=False)
                if len(value_str) > MAX_VALUE_LENGTH:
                    # 直接使用字符串，避免 JSON 解析错误
                    truncated_args[key] = f"<{type(value).__name__}> {value_str[:MAX_VALUE_LENGTH]}..."
                else:
                    truncated_args[key] = value
            else:
                truncated_args[key] = value
        
        # 格式化参数，使用代码高亮
        args_str = json.dumps(truncated_args, ensure_ascii=False, indent=2)
        console.print(Syntax(args_str, "json", theme="monokai", line_numbers=False, word_wrap=True))

def print_agent_message(message_type: str, content: str) -> None:
    """
    打印 Agent 消息（使用 Rich Panel）
    
    Args:
        message_type: 消息类型（如 'AIMessage', 'HumanMessage'）
        content: 消息内容
    """
    timestamp = format_timestamp()
    if message_type == "AIMessage":
        panel = Panel(
            Markdown(_safe_for_console(content)),
            title=f"[bold blue]Agent 回复[/bold blue] [dim]({timestamp})[/dim]",
            border_style="blue",
            padding=(1, 2)
        )
        console.print()
        console.print(panel)
        console.print()
    elif message_type == "HumanMessage":
        console.print(f"[dim][{timestamp}][/dim] [yellow]用户输入:[/yellow] [white]{content}[/white]")


def print_separator() -> None:
    """打印分隔线（使用 Rich）"""
    console.print(f"\n[cyan]{'─' * 60}[/cyan]\n")
