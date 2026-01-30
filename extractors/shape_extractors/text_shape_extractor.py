from extractors.shape_extractors.base_shape_extractor import BaseShapeExtractor

class TextShapeExtractor(BaseShapeExtractor):
    def can_extract(self, shape):
        return shape.has_text_frame

    def extract(self, shape):
        text_frame = shape.text_frame
        text_frame_data = {
            "vertical_anchor": int(text_frame.vertical_anchor) if text_frame.vertical_anchor is not None else None,
            "word_wrap": text_frame.word_wrap,
            "margin_left": int(text_frame.margin_left) if text_frame.margin_left is not None else None,
            "margin_right": int(text_frame.margin_right) if text_frame.margin_right is not None else None,
            "margin_top": int(text_frame.margin_top) if text_frame.margin_top is not None else None,
            "margin_bottom": int(text_frame.margin_bottom) if text_frame.margin_bottom is not None else None,
        }
        paragraphs = []

        for paragraph in text_frame.paragraphs:
            paragraph_font = getattr(paragraph, "font", None)
            paragraph_data = {
                "runs": [],
                "alignment": int(paragraph.alignment) if paragraph.alignment is not None else None,
                "level": int(paragraph.level) if paragraph.level is not None else None,
                "line_spacing": getattr(paragraph.line_spacing, "pt", None) if paragraph.line_spacing is not None else None,
                "space_before": getattr(paragraph.space_before, "pt", None) if paragraph.space_before is not None else None,
                "space_after": getattr(paragraph.space_after, "pt", None) if paragraph.space_after is not None else None,
                "font": {
                    "name": getattr(paragraph_font, "name", None) if paragraph_font is not None else None,
                    "size": getattr(getattr(paragraph_font, "size", None), "pt", None) if paragraph_font is not None else None,
                    "bold": getattr(paragraph_font, "bold", None) if paragraph_font is not None else None,
                    "italic": getattr(paragraph_font, "italic", None) if paragraph_font is not None else None,
                    "underline": getattr(paragraph_font, "underline", None) if paragraph_font is not None else None,
                    "color": self.get_color(getattr(paragraph_font, "color", None)) if paragraph_font is not None else None,
                },
            }
            for run in paragraph.runs:
                run_data = {
                    "text": run.text,
                    "font": run.font.name,
                    "size": run.font.size.pt if run.font.size else None,
                    "bold": run.font.bold,
                    "italic": run.font.italic,
                    "underline": run.font.underline,
                    "color": self.get_color(run.font.color)
                }
                paragraph_data["runs"].append(run_data)
            paragraphs.append(paragraph_data)

        return {
            "type": "text",
            "text_frame": text_frame_data,
            "paragraphs": paragraphs
        }

    def get_color(self, color):
        rgb = getattr(color, "rgb", None)
        if not rgb:
            return None

        if isinstance(rgb, str):
            return rgb

        if isinstance(rgb, (bytes, bytearray)) and len(rgb) == 3:
            return rgb.hex().upper()

        try:
            values = list(rgb)
        except TypeError:
            values = None

        if values and len(values) == 3 and all(isinstance(v, int) for v in values):
            r, g, b = values
            if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                return f"{r:02X}{g:02X}{b:02X}"

        candidate = str(rgb).strip().lstrip("#").upper()
        if len(candidate) == 6 and all(c in "0123456789ABCDEF" for c in candidate):
            return candidate
        return None
