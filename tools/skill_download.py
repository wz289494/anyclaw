"""技能下载工具：通过 Playwright 在网页中查找下载入口并自动解压到 skills 目录。"""

from __future__ import annotations

import json
import zipfile
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool

from utils.path import get_project_root


def _safe_extract_zip(zip_path: Path, target_dir: Path) -> list[str]:
    """安全解压 zip，防止路径穿越。返回解压出的顶层条目列表。"""
    extracted_top: set[str] = set()
    target_root = target_dir.resolve()

    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            member_path = Path(member.filename)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise ValueError(f"不安全的压缩包路径: {member.filename}")

            dest = (target_dir / member.filename).resolve()
            if not str(dest).startswith(str(target_root)):
                raise ValueError(f"检测到路径穿越风险: {member.filename}")

            zf.extract(member, target_dir)
            if member_path.parts:
                extracted_top.add(member_path.parts[0])

    return sorted(extracted_top)


def _unique_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


@tool
def skill_download(url: str) -> str:
    """
    工具名称：skill_download
    描述：打开指定网址，自动识别下载入口（按钮/链接/zip地址），下载压缩包到 skills 目录并解压。

    参数：
    - url: 目标网页地址

    返回：JSON 字符串，包含是否成功、下载文件、识别策略、解压结果等。
    """
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "message": f"缺少 Playwright 依赖，请先安装 playwright: {e}",
                "data": None,
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
        )

    project_root = get_project_root()
    skills_dir = project_root / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    download_file: Path | None = None
    extracted_items: list[str] = []
    matched_strategy = ""
    final_download_url = ""
    candidate_links: list[str] = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()

            page.goto(url, wait_until="networkidle", timeout=60000)

            # 采集候选链接（用于后续 fallback 和调试）
            links = page.eval_on_selector_all(
                "a[href]",
                """
                (nodes) => nodes
                  .map(n => n.href || "")
                  .filter(Boolean)
                """,
            )
            candidate_links = _unique_keep_order([str(x).strip() for x in links])

            # 策略1：强匹配你给出的按钮文案
            strategy_selectors = [
                ('button:has-text("wget skill.zip")', "button_wget_skill_zip"),
                ('a:has-text("wget skill.zip")', "link_wget_skill_zip"),
                ('button:has-text("download")', "button_download_text"),
                ('a:has-text("download")', "link_download_text"),
                ('a[href$=".zip"]', "anchor_zip_href"),
            ]

            used_click_selector = ""
            for sel, name in strategy_selectors:
                loc = page.locator(sel)
                if loc.count() > 0:
                    used_click_selector = sel
                    matched_strategy = name
                    break

            if used_click_selector:
                with page.expect_download(timeout=60000) as dl_info:
                    page.locator(used_click_selector).first.click()
                download = dl_info.value
                final_download_url = download.url or ""
                suggested_name = download.suggested_filename or "skill.zip"
                download_file = skills_dir / suggested_name
                download.save_as(str(download_file))
            else:
                # 策略2：从页面中找 zip 链接，直接访问触发下载
                zip_links = [
                    x for x in candidate_links
                    if ".zip" in x.lower() or "archive" in x.lower() or "release" in x.lower()
                ]
                zip_links = _unique_keep_order(zip_links)

                if not zip_links:
                    raise RuntimeError("未找到可点击下载按钮，也未发现 zip 候选链接")

                matched_strategy = "direct_open_zip_candidate"
                final_download_url = zip_links[0]

                with page.expect_download(timeout=60000) as dl_info:
                    page.goto(final_download_url, wait_until="domcontentloaded", timeout=60000)
                download = dl_info.value
                suggested_name = download.suggested_filename or "skill.zip"
                download_file = skills_dir / suggested_name
                download.save_as(str(download_file))

            if download_file.suffix.lower() != ".zip":
                # 有些站点可能不给后缀，但内容仍是 zip；做一次宽松处理
                try:
                    with zipfile.ZipFile(download_file, "r"):
                        pass
                except Exception:
                    raise RuntimeError(f"下载文件不是有效 zip: {download_file.name}")

            extracted_items = _safe_extract_zip(download_file, skills_dir)
            download_file.unlink(missing_ok=True)

            context.close()
            browser.close()

    except Exception as e:
        if download_file and download_file.exists():
            download_file.unlink(missing_ok=True)
        return json.dumps(
            {
                "success": False,
                "message": f"下载或解压失败: {e}",
                "data": {
                    "url": url,
                    "matched_strategy": matched_strategy,
                    "final_download_url": final_download_url,
                    "candidate_links_count": len(candidate_links),
                    "candidate_links_preview": candidate_links[:10],
                },
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
        )

    return json.dumps(
        {
            "success": True,
            "message": "技能下载并解压完成",
            "data": {
                "url": url,
                "download_dir": str(skills_dir),
                "matched_strategy": matched_strategy,
                "final_download_url": final_download_url,
                "candidate_links_count": len(candidate_links),
                "extracted_top_items": extracted_items,
            },
            "timestamp": datetime.now().isoformat(),
        },
        ensure_ascii=False,
    )
