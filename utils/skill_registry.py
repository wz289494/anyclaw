"""Skills 注册表：扫描 skills/*/SKILL.md 并提取 name/description。"""

from __future__ import annotations

from typing import Any, Dict, List

import yaml

from utils.path import get_project_root


def _extract_front_matter(md_text: str) -> str:
    """从 SKILL.md 文本中提取 YAML front matter（--- ... ---）内容。"""
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
    """解析 SKILL.md 的 front matter 为字典。"""
    front_matter = _extract_front_matter(md_text)
    if not front_matter:
        return {}
    try:
        data = yaml.safe_load(front_matter) or {}
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def list_local_skills() -> List[Dict[str, str]]:
    """遍历 skills/*/SKILL.md，返回包含 name/description 的技能列表。"""
    skills_root = get_project_root() / "skills"
    if not skills_root.exists():
        return []

    skill_items: List[Dict[str, str]] = []
    for p in skills_root.iterdir():
        if not p.is_dir():
            continue
        if p.name.startswith("."):
            continue

        skill_md = p / "SKILL.md"
        if not skill_md.is_file():
            continue

        try:
            with open(skill_md, "r", encoding="utf-8", errors="replace") as f:
                md_text = f.read()
        except Exception:
            continue

        header = _parse_skill_header(md_text)
        name = str(header.get("name", "") or "").strip()
        description = str(header.get("description", "") or "").strip()
        if not name or not description:
            continue

        skill_items.append(
            {
                "name": name,
                "description": description,
                "folder": p.name,
            }
        )

    skill_items.sort(key=lambda x: x.get("name", ""))
    return skill_items

def format_skill_registry_for_prompt(skills: List[Dict[str, str]]) -> str:
    """将技能列表格式化为可直接拼接进 system prompt 的 Markdown 段落。"""
    if not skills:
        return ""
    lines = ["## 元技能", "", "除了自定义的工具，你还具备下面这些元技能：", ""]
    for s in skills:
        name = (s.get("name") or "").strip()
        desc = (s.get("description") or "").strip().replace("\n", " ")
        if not name or not desc:
            continue
        lines.append(f"- **{name}**：{desc[:400]}")
    return "\n".join(lines).strip()
