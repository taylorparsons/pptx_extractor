import xml.etree.ElementTree as ET

from extractors.shape_extractors.base_shape_extractor import BaseShapeExtractor


class DiagramShapeExtractor(BaseShapeExtractor):
    """
    Extracts SmartArt/diagram text from <dgm:relIds> relationships.

    Note: python-pptx does not provide a public API for SmartArt editing/recreation.
    This extractor focuses on pulling the user-visible text from the diagram data part.
    """

    _R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    _A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"

    def can_extract(self, shape):
        try:
            relids = shape._element.xpath('.//*[local-name()="relIds"]')
        except Exception:
            return False

        if not relids:
            return False

        dm_rid = relids[0].get(f"{{{self._R_NS}}}dm")
        return bool(dm_rid)

    def extract(self, shape):
        relids = shape._element.xpath('.//*[local-name()="relIds"]')
        rel = relids[0]

        rel_ids = {
            "dm": rel.get(f"{{{self._R_NS}}}dm"),
            "lo": rel.get(f"{{{self._R_NS}}}lo"),
            "qs": rel.get(f"{{{self._R_NS}}}qs"),
            "cs": rel.get(f"{{{self._R_NS}}}cs"),
        }

        texts = []
        dm_rid = rel_ids.get("dm")
        if dm_rid:
            try:
                part = shape.part.related_part(dm_rid)
                root = ET.fromstring(part.blob)
                for node in root.findall(f".//{{{self._A_NS}}}t"):
                    if node.text:
                        t = node.text.strip()
                        if t:
                            texts.append(t)
            except Exception:
                texts = []

        return {
            "type": "diagram",
            "rel_ids": rel_ids,
            "texts": texts,
        }

