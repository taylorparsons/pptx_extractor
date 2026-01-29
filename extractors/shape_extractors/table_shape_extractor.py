from extractors.shape_extractors.base_shape_extractor import BaseShapeExtractor

class TableShapeExtractor(BaseShapeExtractor):
    def can_extract(self, shape):
        return shape.has_table

    def extract(self, shape):
        table = shape.table
        rows = []

        for row in table.rows:
            cells = []
            for cell in row.cells:
                cell_data = {
                    "text": cell.text,
                    "row_span": cell.span_height,
                    "col_span": cell.span_width
                }
                cells.append(cell_data)
            rows.append(cells)

        return {
            "type": "table",
            "rows": rows
        }