from extractors.shape_extractors.base_shape_extractor import BaseShapeExtractor

class TextShapeExtractor(BaseShapeExtractor):
    def can_extract(self, shape):
        return shape.has_text_frame

    def extract(self, shape):
        text_frame = shape.text_frame
        paragraphs = []

        for paragraph in text_frame.paragraphs:
            paragraph_data = {"runs": []}
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
