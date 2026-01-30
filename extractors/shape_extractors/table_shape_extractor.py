from extractors.shape_extractors.base_shape_extractor import BaseShapeExtractor

class TableShapeExtractor(BaseShapeExtractor):
    def can_extract(self, shape):
        return shape.has_table

    def extract(self, shape):
        table = shape.table
        rows = []

        col_widths = []
        for col in table.columns:
            width = getattr(col, "width", None)
            col_widths.append(int(width) if width is not None else None)

        row_heights = []
        for row in table.rows:
            height = getattr(row, "height", None)
            row_heights.append(int(height) if height is not None else None)

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
            "col_widths": col_widths,
            "row_heights": row_heights,
            "rows": rows
        }
