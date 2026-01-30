from recreator.shape_recreators.base_shape_recreator import BaseShapeRecreator
from pptx.util import Inches, Emu, Pt
import re
import xml.etree.ElementTree as ET


_R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


class DiagramShapeRecreator(BaseShapeRecreator):
    def can_recreate(self, shape_data):
        return shape_data.get("type") == "diagram"

    def apply_to_shape(self, shape, shape_data):
        """
        Best-effort edit of SmartArt/diagram text in a template PPTX.

        python-pptx does not have a public SmartArt editing API, so this updates the
        underlying diagram OOXML parts by replacing <a:t> values in order.
        """
        texts = shape_data.get("texts")
        if texts is None:
            return False
        if not isinstance(texts, list):
            return False

        dm_rid = self._get_dm_rid(shape)
        if not dm_rid:
            return False

        updated = False
        try:
            dm_part = shape.part.related_part(dm_rid)
            updated = self._replace_texts_in_part(dm_part, texts) or updated

            # Keep the paired drawing part in sync when present (common naming: dataN.xml <-> drawingN.xml).
            dm_name = str(getattr(dm_part, "partname", ""))
            match = re.search(r"/ppt/diagrams/data(\d+)\.xml$", dm_name)
            if match:
                n = match.group(1)
                drawing_name = f"/ppt/diagrams/drawing{n}.xml"
                pkg = getattr(shape.part, "package", None)
                if pkg is not None and hasattr(pkg, "iter_parts"):
                    for part in pkg.iter_parts():
                        if str(getattr(part, "partname", "")) == drawing_name:
                            updated = self._replace_texts_in_part(part, texts) or updated
                            break
        except Exception:
            return updated

        return updated

    def _get_dm_rid(self, shape):
        try:
            relids = shape._element.xpath('.//*[local-name()="relIds"]')
        except Exception:
            return None
        if not relids:
            return None
        return relids[0].get(f"{{{_R_NS}}}dm")

    def _replace_texts_in_part(self, part, texts):
        try:
            blob = part.blob
        except Exception:
            return False

        try:
            root = ET.fromstring(blob)
        except Exception:
            return False

        nodes = root.findall(f".//{{{_A_NS}}}t")
        if not nodes:
            return False

        for i, node in enumerate(nodes):
            node.text = str(texts[i]) if i < len(texts) else ""

        try:
            new_blob = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        except TypeError:
            new_blob = ET.tostring(root, encoding="utf-8")

        try:
            part._blob = new_blob
            return True
        except Exception:
            return False

    def _emu_or_default(self, value, default):
        if value is None:
            return default
        if isinstance(value, (int, float)):
            try:
                return Emu(int(value))
            except (TypeError, ValueError):
                return default
        return value

    def recreate(self, slide, shape_data):
        left = self._emu_or_default(shape_data.get("left"), Inches(1))
        top = self._emu_or_default(shape_data.get("top"), Inches(1))
        width = self._emu_or_default(shape_data.get("width"), Inches(5))
        height = self._emu_or_default(shape_data.get("height"), Inches(1))

        text_box = slide.shapes.add_textbox(left, top, width, height)

        rotation = shape_data.get("rotation")
        if rotation is not None:
            try:
                text_box.rotation = float(rotation)
            except (TypeError, ValueError):
                pass

        text_frame = text_box.text_frame
        text_frame.word_wrap = True

        texts = shape_data.get("texts") or []
        if not texts:
            return

        try:
            text_frame.clear()
        except Exception:
            pass

        paragraph = text_frame.paragraphs[0]
        paragraph.text = str(texts[0])
        try:
            paragraph.font.size = Pt(12)
        except Exception:
            pass

        for text in texts[1:]:
            p = text_frame.add_paragraph()
            p.text = str(text)
            try:
                p.font.size = Pt(12)
            except Exception:
                pass
