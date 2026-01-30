from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class ValidationError:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


def _is_hex6(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    candidate = value.strip().lstrip("#")
    if len(candidate) != 6:
        return False
    return all(c in "0123456789abcdefABCDEF" for c in candidate)


def _add_type_error(errors: list[ValidationError], path: str, expected: str, value: Any) -> None:
    errors.append(ValidationError(path, f"Expected {expected}, got {type(value).__name__}"))


def _expect_dict(errors: list[ValidationError], path: str, value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        _add_type_error(errors, path, "object", value)
        return None
    return value


def _expect_list(errors: list[ValidationError], path: str, value: Any) -> list[Any] | None:
    if not isinstance(value, list):
        _add_type_error(errors, path, "array", value)
        return None
    return value


def _expect_str(errors: list[ValidationError], path: str, value: Any) -> str | None:
    if not isinstance(value, str):
        _add_type_error(errors, path, "string", value)
        return None
    return value


def _expect_int(errors: list[ValidationError], path: str, value: Any) -> int | None:
    if not isinstance(value, int):
        _add_type_error(errors, path, "integer", value)
        return None
    return value


def _expect_bool(errors: list[ValidationError], path: str, value: Any) -> bool | None:
    if not isinstance(value, bool):
        _add_type_error(errors, path, "boolean", value)
        return None
    return value


def _expect_number(errors: list[ValidationError], path: str, value: Any) -> float | int | None:
    if not isinstance(value, (int, float)):
        _add_type_error(errors, path, "number", value)
        return None
    return value


def _validate_optional(
    errors: list[ValidationError],
    path: str,
    value: Any,
    validator,
) -> None:
    if value is None:
        return
    validator(errors, path, value)


def _validate_optional_int(errors: list[ValidationError], path: str, value: Any) -> None:
    if value is None:
        return
    _expect_int(errors, path, value)


def _validate_optional_bool(errors: list[ValidationError], path: str, value: Any) -> None:
    if value is None:
        return
    _expect_bool(errors, path, value)


def _validate_color(errors: list[ValidationError], path: str, value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, str) or not _is_hex6(value):
        errors.append(ValidationError(path, "Expected a 6-digit hex color like 'RRGGBB'"))


def _validate_text_shape(errors: list[ValidationError], path: str, shape: dict[str, Any]) -> None:
    tf = _expect_dict(errors, f"{path}.text_frame", shape.get("text_frame"))
    if tf is not None:
        _validate_optional_int(errors, f"{path}.text_frame.vertical_anchor", tf.get("vertical_anchor"))
        _validate_optional_bool(errors, f"{path}.text_frame.word_wrap", tf.get("word_wrap"))
        _validate_optional_int(errors, f"{path}.text_frame.margin_left", tf.get("margin_left"))
        _validate_optional_int(errors, f"{path}.text_frame.margin_right", tf.get("margin_right"))
        _validate_optional_int(errors, f"{path}.text_frame.margin_top", tf.get("margin_top"))
        _validate_optional_int(errors, f"{path}.text_frame.margin_bottom", tf.get("margin_bottom"))

    paragraphs = _expect_list(errors, f"{path}.paragraphs", shape.get("paragraphs"))
    if paragraphs is None:
        return

    for pi, paragraph in enumerate(paragraphs):
        p_path = f"{path}.paragraphs[{pi}]"
        p_obj = _expect_dict(errors, p_path, paragraph)
        if p_obj is None:
            continue

        _validate_optional_int(errors, f"{p_path}.alignment", p_obj.get("alignment"))
        _validate_optional_int(errors, f"{p_path}.level", p_obj.get("level"))
        _validate_optional(errors, f"{p_path}.line_spacing", p_obj.get("line_spacing"), _expect_number)
        _validate_optional(errors, f"{p_path}.space_before", p_obj.get("space_before"), _expect_number)
        _validate_optional(errors, f"{p_path}.space_after", p_obj.get("space_after"), _expect_number)

        font = p_obj.get("font")
        if font is not None:
            font_obj = _expect_dict(errors, f"{p_path}.font", font)
            if font_obj is not None:
                if font_obj.get("name") is not None:
                    _expect_str(errors, f"{p_path}.font.name", font_obj.get("name"))
                _validate_optional(errors, f"{p_path}.font.size", font_obj.get("size"), _expect_number)
                _validate_optional_bool(errors, f"{p_path}.font.bold", font_obj.get("bold"))
                _validate_optional_bool(errors, f"{p_path}.font.italic", font_obj.get("italic"))
                _validate_optional_bool(errors, f"{p_path}.font.underline", font_obj.get("underline"))
                _validate_color(errors, f"{p_path}.font.color", font_obj.get("color"))

        runs = _expect_list(errors, f"{p_path}.runs", p_obj.get("runs"))
        if runs is None:
            continue

        for ri, run in enumerate(runs):
            r_path = f"{p_path}.runs[{ri}]"
            r_obj = _expect_dict(errors, r_path, run)
            if r_obj is None:
                continue
            _expect_str(errors, f"{r_path}.text", r_obj.get("text"))
            if r_obj.get("font") is not None:
                _expect_str(errors, f"{r_path}.font", r_obj.get("font"))
            _validate_optional(errors, f"{r_path}.size", r_obj.get("size"), _expect_number)
            _validate_optional_bool(errors, f"{r_path}.bold", r_obj.get("bold"))
            _validate_optional_bool(errors, f"{r_path}.italic", r_obj.get("italic"))
            _validate_optional_bool(errors, f"{r_path}.underline", r_obj.get("underline"))
            _validate_color(errors, f"{r_path}.color", r_obj.get("color"))


def _validate_table_shape(errors: list[ValidationError], path: str, shape: dict[str, Any]) -> None:
    col_widths = _expect_list(errors, f"{path}.col_widths", shape.get("col_widths"))
    if col_widths is not None:
        for ci, w in enumerate(col_widths):
            if w is not None:
                _expect_int(errors, f"{path}.col_widths[{ci}]", w)

    row_heights = _expect_list(errors, f"{path}.row_heights", shape.get("row_heights"))
    if row_heights is not None:
        for ri, h in enumerate(row_heights):
            if h is not None:
                _expect_int(errors, f"{path}.row_heights[{ri}]", h)

    rows = _expect_list(errors, f"{path}.rows", shape.get("rows"))
    if rows is None:
        return

    for ri, row in enumerate(rows):
        row_list = _expect_list(errors, f"{path}.rows[{ri}]", row)
        if row_list is None:
            continue
        for ci, cell in enumerate(row_list):
            c_path = f"{path}.rows[{ri}][{ci}]"
            cell_obj = _expect_dict(errors, c_path, cell)
            if cell_obj is None:
                continue
            _expect_str(errors, f"{c_path}.text", cell_obj.get("text"))
            _expect_int(errors, f"{c_path}.row_span", cell_obj.get("row_span"))
            _expect_int(errors, f"{c_path}.col_span", cell_obj.get("col_span"))


def _validate_picture_shape(errors: list[ValidationError], path: str, shape: dict[str, Any]) -> None:
    image_data = _expect_str(errors, f"{path}.image_data", shape.get("image_data"))
    if image_data is None:
        return
    try:
        base64.b64decode(image_data, validate=True)
    except Exception:
        errors.append(ValidationError(f"{path}.image_data", "Invalid base64 string"))


def _validate_diagram_shape(errors: list[ValidationError], path: str, shape: dict[str, Any]) -> None:
    rel_ids = shape.get("rel_ids")
    if rel_ids is not None:
        rel_obj = _expect_dict(errors, f"{path}.rel_ids", rel_ids)
        if rel_obj is not None:
            for key in ("dm", "lo", "qs", "cs"):
                if rel_obj.get(key) is not None:
                    _expect_str(errors, f"{path}.rel_ids.{key}", rel_obj.get(key))

    texts = _expect_list(errors, f"{path}.texts", shape.get("texts"))
    if texts is None:
        return
    for ti, t in enumerate(texts):
        _expect_str(errors, f"{path}.texts[{ti}]", t)


def validate_info_json(data: Any) -> list[ValidationError]:
    """
    Validate an extracted PPTX info JSON (v2).

    Returns a list of ValidationError items. Empty list means "valid enough to recreate".
    """
    errors: list[ValidationError] = []

    root = _expect_dict(errors, "$", data)
    if root is None:
        return errors

    version = root.get("version")
    if version is None:
        errors.append(ValidationError("$.version", "Missing required field"))
    else:
        _expect_int(errors, "$.version", version)
        if isinstance(version, int) and version != 2:
            errors.append(ValidationError("$.version", f"Unsupported version {version} (expected 2)"))

    presentation = _expect_dict(errors, "$.presentation", root.get("presentation"))
    if presentation is not None:
        _expect_int(errors, "$.presentation.slide_width", presentation.get("slide_width"))
        _expect_int(errors, "$.presentation.slide_height", presentation.get("slide_height"))

    source = root.get("source_pptx")
    if source is not None:
        source_obj = _expect_dict(errors, "$.source_pptx", source)
        if source_obj is not None:
            if source_obj.get("path") is not None:
                _expect_str(errors, "$.source_pptx.path", source_obj.get("path"))
            if source_obj.get("basename") is not None:
                _expect_str(errors, "$.source_pptx.basename", source_obj.get("basename"))

    slides = _expect_list(errors, "$.slides", root.get("slides"))
    if slides is None:
        return errors

    slide_indices: list[int] = []
    for si, slide in enumerate(slides):
        s_path = f"$.slides[{si}]"
        slide_obj = _expect_dict(errors, s_path, slide)
        if slide_obj is None:
            continue

        idx = slide_obj.get("slide_index")
        idx_val = _expect_int(errors, f"{s_path}.slide_index", idx)
        if isinstance(idx_val, int):
            slide_indices.append(idx_val)

        shapes = _expect_list(errors, f"{s_path}.shapes", slide_obj.get("shapes"))
        if shapes is None:
            continue

        for shi, shape in enumerate(shapes):
            sh_path = f"{s_path}.shapes[{shi}]"
            sh_obj = _expect_dict(errors, sh_path, shape)
            if sh_obj is None:
                continue

            shape_type = _expect_str(errors, f"{sh_path}.type", sh_obj.get("type"))
            if shape_type is None:
                continue

            # Common optional fields used during recreation.
            for key in ("z_order", "left", "top", "width", "height"):
                if key in sh_obj and sh_obj[key] is not None:
                    _expect_int(errors, f"{sh_path}.{key}", sh_obj[key])
            if "rotation" in sh_obj and sh_obj["rotation"] is not None:
                _expect_number(errors, f"{sh_path}.rotation", sh_obj["rotation"])

            if shape_type == "text":
                _validate_text_shape(errors, sh_path, sh_obj)
            elif shape_type == "table":
                _validate_table_shape(errors, sh_path, sh_obj)
            elif shape_type == "picture":
                _validate_picture_shape(errors, sh_path, sh_obj)
            elif shape_type == "diagram":
                _validate_diagram_shape(errors, sh_path, sh_obj)
            else:
                errors.append(
                    ValidationError(
                        f"{sh_path}.type",
                        f"Unsupported shape type {shape_type!r} (expected one of: text, table, picture, diagram)",
                    )
                )

    # Help users catch “missing slide” problems quickly.
    if slide_indices:
        unique = sorted(set(slide_indices))
        expected = list(range(len(slides)))
        if unique != expected:
            errors.append(
                ValidationError(
                    "$.slides[*].slide_index",
                    f"slide_index values should be 0..{len(slides)-1}; got {unique}",
                )
            )

    return errors
