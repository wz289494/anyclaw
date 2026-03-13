"""CLI 主入口：交互式命令行界面。"""

from __future__ import annotations

import sys
from rich.prompt import Prompt
from cli.display import print_icon, print_welcome, console
from cli.interactive import run_session_loop
from cli.session_ui import show_session_selector
from cli.tools_ui import show_tools_list
from cli.models_ui import show_models_list
from cli.skills_ui import show_skills_list
from cli.clear_utils import confirm_and_clear


def interactive() -> None:
    """进入交互式模式（默认命令）"""
    # 显示图标和欢迎信息
    print_icon()
    print_welcome()
    
    # 主循环：处理命令
    while True:
        try:
            # 在 user 提示前添加绿色横线作为对话区隔
            console.print("[green]────────────────────────────────────────────────────────────[/green]")
            user_input = Prompt.ask("[bold cyan]user[/bold cyan]")
            
            if not user_input:
                continue
            
            # 处理系统级命令（以 / 开头）
            if user_input.strip().startswith("/"):
                # 处理 /exit 命令
                if user_input.strip() == "/exit":
                    console.print(f"\n[cyan]感谢使用 [bold magenta]AnyClaw[/bold magenta]，再见！[/cyan]\n")
                    break
                
                # 处理 /new 命令
                if user_input.strip() == "/new":
                    run_session_loop(task_id=None)
                    continue
                
                # 处理 /memory 命令（选择会话）
                if user_input.strip() == "/memory":
                    selected_task_id = show_session_selector(limit=5)
                    if selected_task_id:
                        run_session_loop(task_id=selected_task_id)
                    continue
                
                # 处理 /models 命令（显示模型配置）
                if user_input.strip() == "/models":
                    show_models_list()
                    continue
                
                # 处理 /tools 命令（显示工具列表）
                if user_input.strip() == "/tools":
                    show_tools_list()
                    continue

                # 处理 /skills 命令（显示 skills 列表）
                if user_input.strip() == "/skills":
                    show_skills_list()
                    continue
                
                # 处理 /clear 命令（清除 memory 和 sandbox）
                if user_input.strip() == "/clear":
                    confirm_and_clear()
                    continue
                
                # 处理其他未知命令
                console.print(f"[yellow]未知命令: {user_input}[/yellow]")
                console.print("[cyan]可用命令:[/cyan]")
                console.print("  [cyan]/new[/cyan]     - 开启新的会话")
                console.print("  [cyan]/memory[/cyan]  - 查看并恢复之前的会话")
                console.print("  [cyan]/models[/cyan]  - 查看所有模型配置")
                console.print("  [cyan]/tools[/cyan]   - 查看所有可用工具")
                console.print("  [cyan]/skills[/cyan]  - 查看所有可用 skills")
                console.print("  [cyan]/clear[/cyan]   - 清除 memory 和 sandbox")
                console.print("  [cyan]/exit[/cyan]    - 退出程序")
                continue
            
            # 默认行为：只提示，不创建会话
            console.print("[yellow]提示: 使用 '/new' 开启新会话，或使用 '/memory' 恢复之前的会话[/yellow]")
            
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
