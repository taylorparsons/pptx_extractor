from recreator.shape_recreators.base_shape_recreator import BaseShapeRecreator
from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_VERTICAL_ANCHOR

class TextShapeRecreator(BaseShapeRecreator):
    def can_recreate(self, shape_data):
        return shape_data["type"] == "text"

    def _normalize_rgb(self, color):
        if not color:
            return None

        if isinstance(color, str):
            candidate = color.strip().lstrip("#").upper()
            if len(candidate) == 6 and all(c in "0123456789ABCDEF" for c in candidate):
                return candidate
            return None

        if isinstance(color, (bytes, bytearray)) and len(color) == 3:
            return color.hex().upper()

        if isinstance(color, (list, tuple)) and len(color) == 3:
            try:
                r, g, b = (int(color[0]), int(color[1]), int(color[2]))
            except (TypeError, ValueError):
                return None
            if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                return f"{r:02X}{g:02X}{b:02X}"
            return None

        candidate = str(color).strip().lstrip("#").upper()
        if len(candidate) == 6 and all(c in "0123456789ABCDEF" for c in candidate):
            return candidate
        return None

    def recreate(self, slide, shape_data):
        left = shape_data.get("left", Inches(1))
        top = shape_data.get("top", Inches(1))
        width = shape_data.get("width", Inches(5))
        height = shape_data.get("height", Inches(1))

        text_box = slide.shapes.add_textbox(left, top, width, height)
        text_frame = text_box.text_frame
        text_frame.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE

        for paragraph_data in shape_data["paragraphs"]:
            paragraph = text_frame.add_paragraph()
            paragraph.alignment = PP_ALIGN.LEFT
            paragraph.line_spacing = Pt(12)
            for run_data in paragraph_data["runs"]:
                run = paragraph.add_run()
                run.text = run_data.get("text") or ""

                font_name = run_data.get("font")
                if font_name:
                    run.font.name = font_name

                font_size = run_data.get("size")
                if font_size is not None:
                    try:
                        run.font.size = Pt(float(font_size))
                    except (TypeError, ValueError):
                        pass

                run.font.bold = run_data.get("bold")
                run.font.italic = run_data.get("italic")
                run.font.underline = run_data.get("underline")

                rgb = self._normalize_rgb(run_data.get("color"))
                if rgb:
                    run.font.color.rgb = RGBColor.from_string(rgb)
