from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

import streamlit as st

from extractors.extractor import Extractor
from recreator.recreator import Recreator
from utils.info_json_validator import validate_info_json


def _ensure_writable_dir(path_str: str) -> Path:
    path = Path(path_str).expanduser()
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception:
        path = Path("output").resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    test_file = path / ".write_test"
    try:
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
    except Exception:
        path = Path("output").resolve()
        path.mkdir(parents=True, exist_ok=True)
    return path


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _json_summary(data: Any) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    if not isinstance(data, dict):
        return summary
    summary["version"] = data.get("version")
    slides = data.get("slides") or []
    summary["slide_count"] = len(slides) if isinstance(slides, list) else None
    type_counts: Counter[str] = Counter()
    if isinstance(slides, list):
        for slide in slides:
            if not isinstance(slide, dict):
                continue
            for shape in slide.get("shapes") or []:
                if isinstance(shape, dict) and isinstance(shape.get("type"), str):
                    type_counts[shape["type"]] += 1
    summary["shape_type_counts"] = dict(type_counts)
    return summary


def _filtered_json(data: Any, keep_slides: list[int], keep_types: list[str], reindex_slides: bool) -> Any:
    if not isinstance(data, dict):
        return data
    slides = data.get("slides") or []
    if not isinstance(slides, list):
        return data

    keep_slides_set = set(keep_slides)
    keep_types_set = set(keep_types)

    new_slides = []
    for slide in slides:
        if not isinstance(slide, dict):
            continue
        slide_index = slide.get("slide_index")
        if isinstance(slide_index, int) and slide_index not in keep_slides_set:
            continue
        shapes = slide.get("shapes") or []
        if isinstance(shapes, list) and keep_types_set:
            shapes = [
                shape
                for shape in shapes
                if isinstance(shape, dict) and (shape.get("type") in keep_types_set)
            ]
        new_slide = dict(slide)
        new_slide["shapes"] = shapes
        new_slides.append(new_slide)

    if reindex_slides:
        for i, slide in enumerate(new_slides):
            old = slide.get("slide_index")
            slide["original_slide_index"] = old
            slide["slide_index"] = i

    out = dict(data)
    out["slides"] = new_slides
    return out


def _run_extract(pptx_path: str, output_dir: str) -> Path:
    out_dir = _ensure_writable_dir(output_dir)
    extractor = Extractor(pptx_path)
    out_path = Path(extractor.extract_info(str(out_dir)))
    return out_path


def _run_recreate(pptx_path: str, output_dir: str, info_path: str, output_pptx: str | None) -> Path:
    out_dir = _ensure_writable_dir(output_dir)
    template = pptx_path if os.path.isfile(pptx_path) else None
    recreator = Recreator(info_path, template_pptx_path=template)

    out_path = None
    if output_pptx:
        candidate = os.path.expanduser(output_pptx)
        out_path = candidate
        if os.path.basename(candidate) == candidate:
            out_path = str(out_dir / candidate)
        if out_path and not out_path.lower().endswith(".pptx"):
            out_path = f"{out_path}.pptx"

    created = Path(recreator.recreate_pptx(str(out_dir), output_path=out_path))
    return created


st.set_page_config(page_title="pptx_extractor UI", layout="wide")

st.title("pptx_extractor — Web UI")
st.caption("Run extract/recreate, filter JSON, and validate edits before recreating.")

tabs = st.tabs(["Extract", "Validate / Filter JSON", "Recreate"])


with tabs[0]:
    st.subheader("Extract PPTX → *_info.json")
    pptx_path = st.text_input("PPTX path", value="")
    output_dir = st.text_input("Output directory", value=str(Path("output").resolve()))
    col1, col2 = st.columns([1, 2])
    with col1:
        run_extract = st.button("Run extract", type="primary")
    with col2:
        st.write("Tip: Use a writable directory. If not writable, this UI falls back to `./output`.")

    if run_extract:
        if not pptx_path:
            st.error("Please enter a PPTX path.")
        elif not os.path.isfile(pptx_path):
            st.error(f"PPTX file not found: {pptx_path}")
        else:
            try:
                out_json = _run_extract(pptx_path, output_dir)
                st.success(f"Extracted JSON: {out_json}")
                st.session_state["last_info_path"] = str(out_json)
                data = _load_json(out_json)
                st.json(_json_summary(data))
            except Exception as e:
                st.exception(e)


with tabs[1]:
    st.subheader("Validate and filter an extracted JSON")

    default_info = st.session_state.get("last_info_path", "")
    info_path = st.text_input("Info JSON path", value=default_info)

    colA, colB, colC = st.columns([1, 1, 2])
    with colA:
        validate_now = st.button("Validate JSON")
    with colB:
        load_now = st.button("Load JSON")
    with colC:
        st.write("Validation is fast even for large JSON. Editing inline is only enabled for smaller files.")

    data: Any | None = None
    info_file = Path(info_path).expanduser() if info_path else None
    if load_now and info_file:
        if not info_file.exists() or info_file.is_dir():
            st.error("Please provide an existing JSON file path (not a directory).")
        else:
            try:
                data = _load_json(info_file)
                st.session_state["loaded_json_data"] = data
                st.session_state["loaded_json_path"] = str(info_file)
                st.success("Loaded JSON.")
                st.json(_json_summary(data))
            except Exception as e:
                st.exception(e)

    if validate_now and info_file:
        if not info_file.exists() or info_file.is_dir():
            st.error("Please provide an existing JSON file path (not a directory).")
        else:
            try:
                data = _load_json(info_file)
                errors = validate_info_json(data)
                if not errors:
                    st.success("OK: JSON matches expected schema (v2) enough to recreate.")
                else:
                    st.error(f"Found {len(errors)} issue(s).")
                    st.code("\n".join(str(e) for e in errors))
            except Exception as e:
                st.exception(e)

    data = st.session_state.get("loaded_json_data")
    if isinstance(data, dict) and isinstance(data.get("slides"), list):
        st.divider()
        st.markdown("### Filter controls")

        slides = data["slides"]
        indices = []
        for s in slides:
            if isinstance(s, dict) and isinstance(s.get("slide_index"), int):
                indices.append(s["slide_index"])
        indices = sorted(set(indices))
        if not indices:
            st.info("No `slide_index` values found; extract again with the latest code.")
        else:
            keep_slides = st.multiselect("Slides to keep", options=indices, default=indices)

            type_counts = _json_summary(data).get("shape_type_counts") or {}
            type_options = sorted(type_counts.keys())
            default_types = type_options
            keep_types = st.multiselect("Shape types to keep", options=type_options, default=default_types)
            reindex_slides = st.checkbox("Reindex slides (recommended)", value=True)

            filtered = _filtered_json(data, keep_slides=keep_slides, keep_types=keep_types, reindex_slides=reindex_slides)
            st.json(_json_summary(filtered))

            save_path_default = ""
            if "loaded_json_path" in st.session_state:
                p = Path(st.session_state["loaded_json_path"])
                save_path_default = str(p.with_name(f"filtered_{p.name}"))
            save_path = st.text_input("Save filtered JSON to", value=save_path_default)
            if st.button("Save filtered JSON", type="primary"):
                try:
                    out_path = Path(save_path).expanduser()
                    _save_json(out_path, filtered)
                    st.success(f"Saved: {out_path}")
                    st.session_state["last_info_path"] = str(out_path)
                except Exception as e:
                    st.exception(e)

        st.divider()
        st.markdown("### Optional inline editing (small JSON only)")
        try:
            if info_file and info_file.exists():
                size = info_file.stat().st_size
            else:
                size = 0
        except Exception:
            size = 0

        if info_file and size and size <= 2_000_000:
            raw = info_file.read_text(encoding="utf-8")
            edited = st.text_area("Edit JSON", value=raw, height=320)
            if st.button("Validate edited JSON"):
                try:
                    edited_data = json.loads(edited)
                    errors = validate_info_json(edited_data)
                    if not errors:
                        st.success("OK: edited JSON validates.")
                    else:
                        st.error(f"Found {len(errors)} issue(s).")
                        st.code("\n".join(str(e) for e in errors))
                except Exception as e:
                    st.exception(e)
            if st.button("Save edited JSON"):
                try:
                    json.loads(edited)  # ensure valid JSON before write
                    info_file.write_text(edited, encoding="utf-8")
                    st.success(f"Saved edits to: {info_file}")
                except Exception as e:
                    st.exception(e)
        else:
            st.info("Inline editing is disabled for large JSON files (>2MB). Use your editor + `./run.sh validate <path>`.")


with tabs[2]:
    st.subheader("Recreate PPTX from JSON")
    pptx_path = st.text_input("Template PPTX path (optional but recommended for style)", value="")
    output_dir = st.text_input("Output directory", value=str(Path("output").resolve()), key="recreate_output_dir")
    info_path = st.text_input("Info JSON path", value=st.session_state.get("last_info_path", ""), key="recreate_info_path")
    output_pptx = st.text_input("Output PPTX path or filename (optional)", value="")

    if st.button("Run recreate", type="primary"):
        if not info_path:
            st.error("Please enter an info JSON path.")
        elif not os.path.isfile(os.path.expanduser(info_path)):
            st.error(f"Info JSON not found: {info_path}")
        else:
            try:
                created = _run_recreate(
                    pptx_path=pptx_path,
                    output_dir=output_dir,
                    info_path=os.path.expanduser(info_path),
                    output_pptx=output_pptx or None,
                )
                st.success(f"Created PPTX: {created}")
            except Exception as e:
                st.exception(e)

