"""测试文件管理工具"""

import json
import sys
import uuid
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.file_manager import file_manager
from utils.task_context import set_task_id
from utils.path import ensure_task_dirs
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

def main():
    """主函数：运行 file_manager 工具并显示结果"""
    # 创建临时任务ID用于测试
    task_id = str(uuid.uuid4())
    set_task_id(task_id)
    ensure_task_dirs(task_id)
    
    console.print("[bold cyan]运行 File Manager 工具[/bold cyan]")
    console.print()
    
    # 测试用例
    test_cases = [
        # 创建文本文件
        {
            "action": "create",
            "file_path": "test.txt",
            "content": "Hello, File Manager!"
        },
        # 读取文本文件
        {
            "action": "read",
            "file_path": "test.txt"
        },
        # 更新文本文件
        {
            "action": "update",
            "file_path": "test.txt",
            "content": "Hello, Updated File Manager!"
        },
        # 读取更新后的文本文件
        {
            "action": "read",
            "file_path": "test.txt"
        },
        # 创建JSON文件
        {
            "action": "create",
            "file_path": "test.json",
            "data": {"name": "Test", "value": 123}
        },
        # 读取JSON文件
        {
            "action": "read",
            "file_path": "test.json"
        },
        # 创建DOCX文件
        {
            "action": "create",
            "file_path": "test.docx",
            "content": "Hello, DOCX File!\nThis is a test document."
        },
        # 读取DOCX文件
        {
            "action": "read",
            "file_path": "test.docx"
        },

        # 列出目录
        {
            "action": "list",
            "file_path": "."
        },
        # 删除文本文件
        {
            "action": "delete",
            "file_path": "test.txt"
        },
        # 删除JSON文件
        {
            "action": "delete",
            "file_path": "test.json"
        },
        # 删除DOCX文件
        {
            "action": "delete",
            "file_path": "test.docx"
        },

        # 列出目录（验证文件已删除）
        {
            "action": "list",
            "file_path": "."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        console.print(f"[bold yellow]测试用例 {i}:[/bold yellow]")
        console.print(f"  操作: {test_case['action']}")
        console.print(f"  文件路径: {test_case.get('file_path', 'N/A')}")
        if 'content' in test_case:
            console.print(f"  内容: {test_case['content']}")
        if 'data' in test_case:
            console.print(f"  数据: {json.dumps(test_case['data'], ensure_ascii=False)}")
        
        try:
            # 调用工具
            result_json = file_manager.invoke(test_case)
            
            # 解析结果
            result = json.loads(result_json)
            
            # 显示结果
            if result.get("success"):
                console.print(f"[green]成功: {result.get('message', '操作成功')}[/green]")
                if 'data' in result and result['data']:
                    console.print()
                    console.print(Panel(
                        Syntax(json.dumps(result['data'], ensure_ascii=False, indent=2), "json", theme="monokai", line_numbers=False),
                        title="[bold]返回数据[/bold]",
                        border_style="green"
                    ))
            else:
                console.print(f"[red]失败: {result.get('message', '操作失败')}[/red]")
            
            # 显示完整的 JSON 结果
            result_str = json.dumps(result, ensure_ascii=False, indent=2)
            console.print()
            console.print(Panel(
                Syntax(result_str, "json", theme="monokai", line_numbers=False),
                title="[bold]完整结果[/bold]",
                border_style="blue"
            ))
        
        except Exception as e:
            console.print(f"[red]执行失败: {str(e)}[/red]")
            import traceback
            traceback.print_exc()
        
        console.print()
        console.print("[dim]" + "─" * 60 + "[/dim]")
        console.print()
    
    console.print(f"[dim]任务ID: {task_id}[/dim]")
    console.print(f"[dim]操作目录: sandbox/{task_id}/[/dim]")

if __name__ == "__main__":
    main()
