from __future__ import annotations

import base64
import io
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

import streamlit as st

from extractors.extractor import Extractor
from recreator.recreator import Recreator
from utils.info_json_validator import validate_info_json


_FAVICON_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAACCklEQVR4nO2bu0rEQBSGz/zEym6x"
    "0EZsBMFmsbO32IcQ0m63jY+hhZ3YSMDHsNZOthEEOxst9g0sVhYZWNZcZpIzmTM5+zULuUzm/3KS"
    "TLKJ2R0dLUkxIOWAlANSDkg5IOVknI3tH55RX3x/vrK0Y7peBvsMHUKGaSugLPji6536Yu/ghEWEa"
    "SNgPXyfoV1k+EowPgKkBecQgaGE3+yX67kJXTYiEd/+wWUha1N6eIvtp0sVYGjhfSWAlIMh7n2fKg"
    "ApJwvZeD5/q5xXjE9JAqZqINSl/OuCxxBhB0hlg6OMc0M+wTfXiVURiBmec/2oAnKmzseQAGmd7lt"
    "CRsK5u5r/mza9HsuogDzQ3rLtloWvm94GkFCaQnJJgMRj9fzxx2k5DgkgYbiG55IAUg5IOSDlgJQD"
    "EsbL5Y7X8l0HRWi7Ysi7N1cJHCNCkFCqwt1MHmrn9yqgCFQFtt0mCSpuhqYbEo4ns7/fpxl9XNzKe"
    "CSWtxgWPy/uiZsqIXWPxMCxYSkPOKOeBItEJYCzsZWE1EQgRKMpichCNh5Cwursb+G4CoAShSN8sg"
    "K4wje+I5T6v8NNY4BkK4ATkHJQN9OWTdlLiUMo/xXbCqAGUq0Cl73vXAGpSXAN3+oQkC7Bt39wXXD"
    "dplQJbd4VNtu3xUfb7wWWXcpO7RcjZaj8Zih1QMoBKQekHMTuQGx+AdpL17Ar1SfWAAAAAElFTkSu"
    "QmCC"
)


def _load_page_icon():
    try:
        from PIL import Image

        raw = base64.b64decode(_FAVICON_PNG_BASE64)
        return Image.open(io.BytesIO(raw))
    except Exception:
        # Fallback to default Streamlit favicon
        return None


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _svg_data_uri(path: Path) -> str | None:
    try:
        svg = _read_text(path)
    except Exception:
        return None
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


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


def _save_uploaded_file(uploaded_file, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(uploaded_file.name).name
    out_path = dest_dir / safe_name
    out_path.write_bytes(uploaded_file.getbuffer())
    return out_path


def _default_output_dir() -> str:
    return str(Path("output").resolve())


def _preset_dirs() -> list[tuple[str, str]]:
    home = str(Path.home())
    return [
        ("./output (repo)", _default_output_dir()),
        ("Home (~)", home),
        ("Desktop", str(Path(home) / "Desktop")),
        ("Documents", str(Path(home) / "Documents")),
        ("Downloads", str(Path(home) / "Downloads")),
    ]


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


st.set_page_config(page_title="pptx_extractor UI", layout="wide", page_icon=_load_page_icon())

assets_dir = (Path(__file__).resolve().parent.parent / "assets").resolve()
banner_path = assets_dir / "readme-banner.svg"
side_path = assets_dir / "ui-side-illustration.svg"

banner_uri = _svg_data_uri(banner_path) if banner_path.exists() else None
side_uri = _svg_data_uri(side_path) if side_path.exists() else None
if banner_uri and side_uri:
    st.markdown(
        f"""
<div style="display:flex; gap: 16px; align-items: stretch; flex-wrap: wrap;">
  <div style="flex: 3; min-width: 520px; border-radius: 14px; overflow:hidden;">
    <img alt="pptx_extractor banner" src="{banner_uri}" style="width: 100%; height: auto; display:block;" />
  </div>
  <div style="flex: 1; min-width: 320px; border-radius: 14px; overflow:hidden;">
    <img alt="pptx_extractor illustration" src="{side_uri}" style="width: 100%; height: auto; display:block;" />
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

st.title("pptx_extractor — Web UI")
st.caption("Run extract/recreate, filter JSON, and validate edits before recreating.")

tabs = st.tabs(["Extract", "Validate / Filter JSON", "Recreate"])

if "output_dir" not in st.session_state:
    st.session_state["output_dir"] = _default_output_dir()


with tabs[0]:
    st.subheader("Extract PPTX → *_info.json")
    col_up, col_path = st.columns([1, 2])
    with col_up:
        uploaded_pptx = st.file_uploader(
            "Select a PPTX file",
            type=["pptx"],
            accept_multiple_files=False,
            key="extract_pptx_uploader",
        )
    with col_path:
        pptx_path = st.text_input(
            "PPTX path",
            value=st.session_state.get("pptx_path", ""),
            key="extract_pptx_path",
        )

    preset_label_to_path = dict(_preset_dirs())
    preset = st.selectbox(
        "Output directory preset",
        options=list(preset_label_to_path.keys()),
        index=0,
        key="extract_output_preset",
    )
    if st.button("Use preset output directory", key="extract_use_preset"):
        st.session_state["output_dir"] = preset_label_to_path[preset]

    output_dir = st.text_input(
        "Output directory",
        value=st.session_state.get("output_dir", _default_output_dir()),
        key="extract_output_dir",
    )
    st.session_state["output_dir"] = output_dir

    if uploaded_pptx is not None:
        try:
            saved = _save_uploaded_file(uploaded_pptx, Path("output/uploads").resolve())
            st.session_state["pptx_path"] = str(saved)
            pptx_path = str(saved)
            st.info(f"Uploaded PPTX saved to: {saved}")
        except Exception as e:
            st.exception(e)

    col1, col2 = st.columns([1, 2])
    with col1:
        run_extract = st.button("Run extract", type="primary", key="extract_run")
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
    col_up, col_path = st.columns([1, 2])
    with col_up:
        uploaded_json = st.file_uploader(
            "Select an extracted *_info.json",
            type=["json"],
            accept_multiple_files=False,
            key="validate_json_uploader",
        )
    with col_path:
        info_path = st.text_input("Info JSON path", value=default_info, key="validate_info_path")

    if uploaded_json is not None:
        try:
            saved = _save_uploaded_file(uploaded_json, Path("output/uploads").resolve())
            st.session_state["last_info_path"] = str(saved)
            info_path = str(saved)
            st.info(f"Uploaded JSON saved to: {saved}")
        except Exception as e:
            st.exception(e)

    colA, colB, colC = st.columns([1, 1, 2])
    with colA:
        validate_now = st.button("Validate JSON", key="validate_run")
    with colB:
        load_now = st.button("Load JSON", key="validate_load")
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
            reindex_slides = st.checkbox("Reindex slides (recommended)", value=True, key="validate_reindex_slides")

            filtered = _filtered_json(data, keep_slides=keep_slides, keep_types=keep_types, reindex_slides=reindex_slides)
            st.json(_json_summary(filtered))

            save_path_default = ""
            if "loaded_json_path" in st.session_state:
                p = Path(st.session_state["loaded_json_path"])
                save_path_default = str(p.with_name(f"filtered_{p.name}"))
            save_path = st.text_input("Save filtered JSON to", value=save_path_default)
            if st.button("Save filtered JSON", type="primary", key="validate_save_filtered"):
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
            edited = st.text_area("Edit JSON", value=raw, height=320, key="validate_inline_editor")
            if st.button("Validate edited JSON", key="validate_inline_validate"):
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
            if st.button("Save edited JSON", key="validate_inline_save"):
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
    col_up1, col_path1 = st.columns([1, 2])
    with col_up1:
        uploaded_template = st.file_uploader(
            "Select a template PPTX (optional, preserves style)",
            type=["pptx"],
            accept_multiple_files=False,
            key="template_uploader",
        )
    with col_path1:
        pptx_path = st.text_input(
            "Template PPTX path (optional but recommended for style)",
            value=st.session_state.get("template_pptx_path", ""),
        )

    if uploaded_template is not None:
        try:
            saved = _save_uploaded_file(uploaded_template, Path("output/uploads").resolve())
            st.session_state["template_pptx_path"] = str(saved)
            pptx_path = str(saved)
            st.info(f"Uploaded template PPTX saved to: {saved}")
        except Exception as e:
            st.exception(e)

    preset_label_to_path = dict(_preset_dirs())
    preset = st.selectbox("Output directory preset", options=list(preset_label_to_path.keys()), index=0, key="recreate_preset")
    if st.button("Use preset output directory", key="recreate_use_preset"):
        st.session_state["output_dir"] = preset_label_to_path[preset]

    output_dir = st.text_input("Output directory", value=st.session_state.get("output_dir", _default_output_dir()), key="recreate_output_dir")
    st.session_state["output_dir"] = output_dir

    col_up2, col_path2 = st.columns([1, 2])
    with col_up2:
        uploaded_info = st.file_uploader(
            "Select an extracted *_info.json",
            type=["json"],
            accept_multiple_files=False,
            key="recreate_json_uploader",
        )
    with col_path2:
        info_path = st.text_input("Info JSON path", value=st.session_state.get("last_info_path", ""), key="recreate_info_path")

    if uploaded_info is not None:
        try:
            saved = _save_uploaded_file(uploaded_info, Path("output/uploads").resolve())
            st.session_state["last_info_path"] = str(saved)
            info_path = str(saved)
            st.info(f"Uploaded JSON saved to: {saved}")
        except Exception as e:
            st.exception(e)

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
