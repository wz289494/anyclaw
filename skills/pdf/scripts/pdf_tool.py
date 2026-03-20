import json
import sys
from pathlib import Path


def _err(message: str, **extra):
    payload = {"success": False, "error": message}
    payload.update(extra)
    print(json.dumps(payload, ensure_ascii=False))


def _ok(**data):
    payload = {"success": True}
    payload.update(data)
    print(json.dumps(payload, ensure_ascii=False))


def _load_json_arg() -> dict:
    if len(sys.argv) < 2:
        return {}
    raw = sys.argv[1]
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def _action_info(input_path: str) -> None:
    try:
        from pypdf import PdfReader
    except Exception as e:
        _err("missing_dependency", detail=str(e))
        return
    p = Path(input_path)
    if not p.is_file():
        _err("input_not_found", input=input_path)
        return
    try:
        reader = PdfReader(str(p))
        meta = reader.metadata
        _ok(
            action="info",
            input=str(p),
            pages=len(reader.pages),
            metadata={
                "title": getattr(meta, "title", None),
                "author": getattr(meta, "author", None),
                "subject": getattr(meta, "subject", None),
                "creator": getattr(meta, "creator", None),
                "producer": getattr(meta, "producer", None),
            },
        )
    except Exception as e:
        _err("failed_to_read_pdf", detail=str(e), input=str(p))


def _action_extract_text(input_path: str, output_path: str, method: str = "pypdf") -> None:
    p = Path(input_path)
    if not p.is_file():
        _err("input_not_found", input=input_path)
        return
    out = Path(output_path)
    _ensure_parent(out)

    if method == "pdfplumber":
        try:
            import pdfplumber
        except Exception as e:
            _err("missing_dependency", detail=str(e))
            return
        try:
            texts = []
            with pdfplumber.open(str(p)) as pdf:
                for page in pdf.pages:
                    texts.append(page.extract_text() or "")
            out.write_text("\n".join(texts), encoding="utf-8", errors="replace")
            _ok(action="extract_text", input=str(p), output=str(out), method="pdfplumber")
        except Exception as e:
            _err("failed_to_extract_text", detail=str(e), input=str(p))
        return

    try:
        from pypdf import PdfReader
    except Exception as e:
        _err("missing_dependency", detail=str(e))
        return
    try:
        reader = PdfReader(str(p))
        texts = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
        out.write_text("\n".join(texts), encoding="utf-8", errors="replace")
        _ok(action="extract_text", input=str(p), output=str(out), method="pypdf")
    except Exception as e:
        _err("failed_to_extract_text", detail=str(e), input=str(p))


def _action_merge(inputs: list[str], output_path: str) -> None:
    try:
        from pypdf import PdfReader, PdfWriter
    except Exception as e:
        _err("missing_dependency", detail=str(e))
        return
    if not inputs:
        _err("inputs_required")
        return
    out = Path(output_path)
    _ensure_parent(out)
    writer = PdfWriter()
    for ip in inputs:
        p = Path(ip)
        if not p.is_file():
            _err("input_not_found", input=str(p))
            return
        reader = PdfReader(str(p))
        for page in reader.pages:
            writer.add_page(page)
    try:
        with out.open("wb") as f:
            writer.write(f)
        _ok(action="merge", inputs=[str(Path(x)) for x in inputs], output=str(out))
    except Exception as e:
        _err("failed_to_write_pdf", detail=str(e), output=str(out))


def _action_split(input_path: str, output_dir: str) -> None:
    try:
        from pypdf import PdfReader, PdfWriter
    except Exception as e:
        _err("missing_dependency", detail=str(e))
        return
    p = Path(input_path)
    if not p.is_file():
        _err("input_not_found", input=input_path)
        return
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        reader = PdfReader(str(p))
        outputs = []
        for i, page in enumerate(reader.pages, start=1):
            w = PdfWriter()
            w.add_page(page)
            out = out_dir / f"page_{i}.pdf"
            with out.open("wb") as f:
                w.write(f)
            outputs.append(str(out))
        _ok(action="split", input=str(p), output_dir=str(out_dir), outputs=outputs)
    except Exception as e:
        _err("failed_to_split_pdf", detail=str(e), input=str(p))


def _action_rotate(input_path: str, output_path: str, degrees: int, pages: list[int] | None) -> None:
    try:
        from pypdf import PdfReader, PdfWriter
    except Exception as e:
        _err("missing_dependency", detail=str(e))
        return
    p = Path(input_path)
    if not p.is_file():
        _err("input_not_found", input=input_path)
        return
    out = Path(output_path)
    _ensure_parent(out)
    try:
        reader = PdfReader(str(p))
        writer = PdfWriter()
        page_set = set(pages or [])
        for idx, page in enumerate(reader.pages, start=1):
            if not page_set or idx in page_set:
                page.rotate(degrees)
            writer.add_page(page)
        with out.open("wb") as f:
            writer.write(f)
        _ok(action="rotate", input=str(p), output=str(out), degrees=degrees, pages=sorted(page_set) if page_set else [])
    except Exception as e:
        _err("failed_to_rotate_pdf", detail=str(e), input=str(p), output=str(out))


def main() -> None:
    payload = _load_json_arg()
    action = str(payload.get("action") or "").strip()
    if not action:
        _err("missing_action")
        return

    if action == "info":
        _action_info(str(payload.get("input") or ""))
        return

    if action == "extract_text":
        _action_extract_text(
            str(payload.get("input") or ""),
            str(payload.get("output") or ""),
            str(payload.get("method") or "pypdf"),
        )
        return

    if action == "merge":
        inputs = payload.get("inputs") or []
        if isinstance(inputs, str):
            inputs = [inputs]
        if not isinstance(inputs, list):
            inputs = []
        _action_merge([str(x) for x in inputs if str(x).strip()], str(payload.get("output") or ""))
        return

    if action == "split":
        _action_split(str(payload.get("input") or ""), str(payload.get("output_dir") or ""))
        return

    if action == "rotate":
        pages = payload.get("pages")
        if pages is None:
            pages_list = None
        elif isinstance(pages, list):
            pages_list = [int(x) for x in pages]
        else:
            pages_list = None
        _action_rotate(
            str(payload.get("input") or ""),
            str(payload.get("output") or ""),
            int(payload.get("degrees") or 90),
            pages_list,
        )
        return

    _err("unsupported_action", action=action)


if __name__ == "__main__":
    main()

