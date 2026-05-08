"""CLI 主入口：交互式命令行界面。"""

from __future__ import annotations

import sys
from multiprocessing import Process
from cli.display import print_icon, print_welcome, console
from cli.interactive import run_session_loop
from utils.session_manager import get_session_manager
from utils.ltm_manager import run_ltm_monitor


_ltm_process: Process | None = None


def _start_ltm_monitor() -> None:
    """启动长期记忆监控子进程（仅启动一次）。"""
    global _ltm_process
    if _ltm_process and _ltm_process.is_alive():
        return
    _ltm_process = Process(target=run_ltm_monitor, daemon=True)
    _ltm_process.start()


def interactive() -> None:
    """进入交互式模式（默认直接进入最近会话）。"""
    # 显示图标和欢迎语，直接进入对话
    print_icon()
    print_welcome()
    _start_ltm_monitor()

    # 默认读取最近一条会话；若无会话则创建新会话。
    try:
        session_manager = get_session_manager()
        sessions = session_manager.list_sessions(limit=1)
        latest_task_id = sessions[0].get("task_id") if sessions else None
        run_session_loop(task_id=latest_task_id)
    except KeyboardInterrupt:
        console.print(f"\n\n[cyan]感谢使用 [bold magenta]AnyClaw[/bold magenta]，再见！[/cyan]\n")
        sys.exit(0)
    except EOFError:
        console.print(f"\n\n[cyan]感谢使用 [bold magenta]AnyClaw[/bold magenta]，再见！[/cyan]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]❌[/red] [red]发生错误:[/red] [white]{str(e)}[/white]\n")
        import traceback
        traceback.print_exc()


def main() -> None:
    """主函数：启动交互式模式。"""
    interactive()


if __name__ == "__main__":
    main()
