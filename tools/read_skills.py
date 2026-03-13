"""读取技能工具：根据 skill name 读取对应 skills/*/SKILL.md 并返回目录结构与用法。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import json
import yaml
from langchain_core.tools import tool

from utils.path import get_project_root


def _extract_front_matter(md_text: str) -> str:
    """提取 Markdown 顶部 YAML front matter（--- ... ---）内容。"""
    text = md_text or ""
    if not text.startswith("---"):
        return ""

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return ""

    return "\n".join(lines[1:end_idx]).strip()


def _parse_skill_header(md_text: str) -> Dict[str, Any]:
    """解析 SKILL.md 顶部 front matter 为字典。"""
    front_matter = _extract_front_matter(md_text)
    if not front_matter:
        return {}
    try:
        data = yaml.safe_load(front_matter) or {}
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _read_text_file(path: Path) -> str:
    """读取文本文件内容（UTF-8，失败返回空字符串）。"""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _is_ignored_entry(name: str) -> bool:
    """判断目录遍历时是否忽略该条目名。"""
    if not name:
        return True
    if name in {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}:
        return True
    if name.startswith("."):
        return True
    return False


def _collect_tree_lines(root: Path, max_entries: int = 200) -> List[str]:
    """生成 root 目录的 tree 文本行列表（限制最大条目数，路径为绝对路径）。"""
    lines: List[str] = []
    count = 0

    def walk(cur: Path, prefix: str) -> None:
        """递归遍历目录并按 tree 结构写入 lines。"""
        nonlocal count
        if count >= max_entries:
            return

        try:
            entries = sorted(cur.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except Exception:
            return

        filtered = [p for p in entries if not _is_ignored_entry(p.name)]
        for idx, p in enumerate(filtered):
            if count >= max_entries:
                break
            is_last = idx == len(filtered) - 1
            connector = "└── " if is_last else "├── "
            full_name = str(p.resolve())
            lines.append(f"{prefix}{connector}{full_name}{'/' if p.is_dir() else ''}")
            count += 1
            if p.is_dir():
                walk(p, prefix + ("    " if is_last else "│   "))

    lines.append(f"{str(root.resolve())}/")
    walk(root, "")
    if count >= max_entries:
        lines.append("└── ...")
    return lines


def _find_skill_dir_by_name(skills_root: Path, skill_name: str) -> Optional[Tuple[Path, str]]:
    """在 skills_root 下按 skill name 查找匹配目录（优先匹配 SKILL.md 的 name）。"""
    normalized = (skill_name or "").strip()
    if not normalized:
        return None

    exact_header_match: Optional[Tuple[Path, str]] = None
    folder_match: Optional[Tuple[Path, str]] = None

    for p in skills_root.iterdir():
        if not p.is_dir():
            continue
        if _is_ignored_entry(p.name):
            continue

        if p.name == normalized:
            folder_match = (p, p.name)

        skill_md = p / "SKILL.md"
        if not skill_md.is_file():
            continue

        md_text = _read_text_file(skill_md)
        header = _parse_skill_header(md_text)
        header_name = str(header.get("name", "") or "").strip()
        if header_name == normalized:
            exact_header_match = (p, p.name)
            break

    return exact_header_match or folder_match


def _collect_skill_scripts(skill_dir: Path, max_items: int = 50) -> List[Dict[str, str]]:
    """收集 skill 目录下可能的可执行脚本路径（优先 scripts/ 下的 .py，绝对路径）。"""
    items: List[Dict[str, str]] = []

    def add_file(p: Path) -> None:
        if len(items) >= max_items:
            return
        items.append(
            {
                "absolute": str(p.resolve()),
            }
        )

    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        for p in sorted(scripts_dir.rglob("*.py")):
            if p.is_file() and not _is_ignored_entry(p.name):
                add_file(p)

    if len(items) < max_items:
        for p in sorted(skill_dir.glob("*.py")):
            if p.is_file() and not _is_ignored_entry(p.name):
                add_file(p)

    return items


@tool
def read_skills(name: str) -> str:
    """
    读取指定 skill 的 SKILL.md，并返回目录结构与完整用法内容（JSON）。

    描述：读取本地 skills 目录中某个 skill 的 SKILL.md，并返回目录结构与完整用法内容。
    使用时机：当需要使用某个元技能skill，先使用该工具了解完整用法，后续根据这个用法进行具体操作。
    输入：
    - name（必填）：skill 的 name
    输出：JSON字符串，包含以下字段：
    - skill_name：输入的 name
    - skill_dir：skill 目录绝对路径
    - skill_dir_abs：skill 目录绝对路径
    - skill_md_path：SKILL.md 绝对路径
    - scripts：该 skill 下可执行脚本列表（absolute）
    - directory_structure：该目录结构（tree 形式字符串）
    - usage：SKILL.md 全文内容
    - explanation_en：英文说明文本（包含目录结构与用法提示）
    """
    skill_name = (name or "").strip()
    if not skill_name:
        return json.dumps({"error": "name 不能为空", "skill_name": name}, ensure_ascii=False)

    skills_root = get_project_root() / "skills"
    if not skills_root.exists():
        return json.dumps(
            {"error": "未找到 skills 目录", "skill_name": skill_name, "skill_dir": ""},
            ensure_ascii=False,
        )

    found = _find_skill_dir_by_name(skills_root, skill_name)
    if not found:
        return json.dumps(
            {"error": f"未找到 skill: {skill_name}", "skill_name": skill_name, "skill_dir": ""},
            ensure_ascii=False,
        )

    skill_dir, folder_name = found
    abs_dir = str(skill_dir.resolve())

    skill_md = skill_dir / "SKILL.md"
    md_text = _read_text_file(skill_md) if skill_md.is_file() else ""
    skill_md_path = str(skill_md.resolve()) if skill_md.exists() else ""

    tree_lines = _collect_tree_lines(skill_dir)
    tree_text = "\n".join(tree_lines)

    scripts = _collect_skill_scripts(skill_dir)

    explanation_en = (
        f"This is the detailed usage for '{skill_name}'. "
        f"The skill is stored in '{abs_dir}'.\n\n"
        f"Folder structure:\n{tree_text}\n\n"
        f"Usage:\nThe full content of SKILL.md is included in the 'usage' field."
    )

    return json.dumps(
        {
            "skill_name": skill_name,
            "skill_dir": abs_dir,
            "skill_dir_abs": abs_dir,
            "skill_md_path": skill_md_path,
            "scripts": scripts,
            "directory_structure": tree_text,
            "usage": md_text,
            "explanation_en": explanation_en,
        },
        ensure_ascii=False,
    )
