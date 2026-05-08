"""LTM 管理：监控 STM 变化并更新长期记忆。"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

from langchain_core.messages import HumanMessage

from model.factory import get_text_generation_model
from utils.path import get_stm_dir, get_memory_dir, get_prompt_dir


POLL_INTERVAL_SECONDS = 2.0


def _ensure_ltm_files() -> Tuple[Path, Path]:
    memory_dir = get_memory_dir()
    ltm_dir = memory_dir / "LTM"
    ltm_dir.mkdir(parents=True, exist_ok=True)

    user_path = ltm_dir / "user.md"
    agent_path = ltm_dir / "agent.md"

    if not user_path.exists():
        user_path.write_text("# 用户长期记忆\n", encoding="utf-8")
    if not agent_path.exists():
        agent_path.write_text("# Agent长期记忆\n", encoding="utf-8")

    return user_path, agent_path


def _load_extractor_prompt() -> str:
    prompt_path = get_prompt_dir() / "ltm_extractor_prompt.txt"
    if not prompt_path.exists():
        return ""
    return prompt_path.read_text(encoding="utf-8").strip()


def _read_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    lines = [x.strip() for x in path.read_text(encoding="utf-8").splitlines()]
    return [x for x in lines if x and not x.startswith("#")]


def _write_lines(path: Path, title: str, lines: List[str]) -> None:
    uniq: List[str] = []
    seen = set()
    for item in lines:
        item = item.strip()
        if not item or item in seen:
            continue
        seen.add(item)
        uniq.append(item)

    body = "\n".join(f"- {x}" for x in uniq)
    content = f"# {title}\n"
    if body:
        content += body + "\n"
    path.write_text(content, encoding="utf-8")


def _load_stm_snapshot(stm_dir: Path) -> Dict[str, Tuple[float, int]]:
    snapshot: Dict[str, Tuple[float, int]] = {}
    if not stm_dir.exists():
        return snapshot
    for p in stm_dir.glob("*.json"):
        stat = p.stat()
        snapshot[p.name] = (stat.st_mtime, stat.st_size)
    return snapshot


def _load_stm_text(stm_file: Path) -> str:
    try:
        data = json.loads(stm_file.read_text(encoding="utf-8"))
    except Exception:
        return ""

    parts: List[str] = []
    for msg in data.get("messages", []):
        role = str(msg.get("role", "")).strip()
        content = str(msg.get("content", "") or "").strip()
        if not content:
            continue
        parts.append(f"{role}: {content}")
    return "\n".join(parts)


def _extract_memory(text: str, user_mem: List[str], agent_mem: List[str], prompt: str) -> Dict[str, List[str]]:
    if not text.strip() or not prompt.strip():
        return {"user_memory": [], "agent_memory": [], "forget_user_memory": [], "forget_agent_memory": []}

    llm = get_text_generation_model()
    query = (
        f"{prompt}\n\n"
        f"当前已有用户长期记忆:\n{json.dumps(user_mem, ensure_ascii=False)}\n\n"
        f"当前已有Agent长期记忆:\n{json.dumps(agent_mem, ensure_ascii=False)}\n\n"
        f"待分析短期对话:\n{text}\n"
    )
    resp = llm.invoke([HumanMessage(content=query)])
    content = getattr(resp, "content", "") or str(resp)

    try:
        parsed = json.loads(content)
    except Exception:
        start = content.find("{")
        end = content.rfind("}")
        if start >= 0 and end > start:
            parsed = json.loads(content[start:end + 1])
        else:
            return {"user_memory": [], "agent_memory": [], "forget_user_memory": [], "forget_agent_memory": []}

    def _norm_list(key: str) -> List[str]:
        v = parsed.get(key, [])
        if not isinstance(v, list):
            return []
        return [str(x).strip() for x in v if str(x).strip()]

    return {
        "user_memory": _norm_list("user_memory"),
        "agent_memory": _norm_list("agent_memory"),
        "forget_user_memory": _norm_list("forget_user_memory"),
        "forget_agent_memory": _norm_list("forget_agent_memory"),
    }


def _merge_memory(current: List[str], add_items: List[str], forget_items: List[str]) -> List[str]:
    result = [x for x in current if x not in set(forget_items)]
    for item in add_items:
        if item not in result:
            result.append(item)
    return result


def run_ltm_monitor() -> None:
    stm_dir = get_stm_dir()
    user_path, agent_path = _ensure_ltm_files()
    extractor_prompt = _load_extractor_prompt()
    snapshot = _load_stm_snapshot(stm_dir)

    while True:
        try:
            new_snapshot = _load_stm_snapshot(stm_dir)
            changed_files = [
                name for name, sig in new_snapshot.items()
                if name not in snapshot or snapshot[name] != sig
            ]

            if changed_files:
                user_mem = _read_lines(user_path)
                agent_mem = _read_lines(agent_path)

                for file_name in changed_files:
                    stm_file = stm_dir / file_name
                    stm_text = _load_stm_text(stm_file)
                    if not stm_text:
                        continue

                    extracted = _extract_memory(stm_text, user_mem, agent_mem, extractor_prompt)
                    user_mem = _merge_memory(
                        user_mem,
                        extracted.get("user_memory", []),
                        extracted.get("forget_user_memory", []),
                    )
                    agent_mem = _merge_memory(
                        agent_mem,
                        extracted.get("agent_memory", []),
                        extracted.get("forget_agent_memory", []),
                    )

                _write_lines(user_path, "用户长期记忆", user_mem)
                _write_lines(agent_path, "Agent长期记忆", agent_mem)

            snapshot = new_snapshot
            time.sleep(POLL_INTERVAL_SECONDS)
        except Exception:
            time.sleep(POLL_INTERVAL_SECONDS)

