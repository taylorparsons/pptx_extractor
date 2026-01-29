import os
import json
import logging
from pptx import Presentation
from recreator.shape_recreators.text_shape_recreator import TextShapeRecreator
from recreator.shape_recreators.table_shape_recreator import TableShapeRecreator
from recreator.shape_recreators.picture_shape_recreator import PictureShapeRecreator
from pptx.dml.color import RGBColor

class Recreator:
    def __init__(self, info_path):
        self.info_path = info_path
        self.recreators = [
            TextShapeRecreator(),
            TableShapeRecreator(),
            PictureShapeRecreator()
        ]

    def recreate_pptx(self, output_dir):
        with open(self.info_path, "r") as f:
            slide_info = json.load(f)

        prs = Presentation()

        for slide_data in slide_info:
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = RGBColor(255, 255, 255)

            shapes_data = sorted(slide_data["shapes"], key=lambda x: x.get("z_order", 0))
            for shape_data in shapes_data:
                for recreator in self.recreators:
                    if recreator.can_recreate(shape_data):
                        recreator.recreate(slide, shape_data)
                        break

        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"recreated_{os.path.basename(self.info_path).split('_')[0]}.pptx")
        prs.save(output_path)

        return output_path
