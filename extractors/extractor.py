import os
import json
import logging
from pptx import Presentation
from extractors.shape_extractors.text_shape_extractor import TextShapeExtractor
from extractors.shape_extractors.table_shape_extractor import TableShapeExtractor
from extractors.shape_extractors.picture_shape_extractor import PictureShapeExtractor

class Extractor:
    def __init__(self, pptx_path):
        self.pptx_path = pptx_path
        self.extractors = [
            TextShapeExtractor(),
            TableShapeExtractor(),
            PictureShapeExtractor()
        ]

    def extract_info(self, output_dir):
        prs = Presentation(self.pptx_path)
        slide_info = []

        for slide in prs.slides:
            slide_data = {"shapes": []}
            for shape in slide.shapes:
                for extractor in self.extractors:
                    if extractor.can_extract(shape):
                        shape_data = extractor.extract(shape)
                        slide_data["shapes"].append(shape_data)
                        break
            slide_info.append(slide_data)

        os.makedirs(output_dir, exist_ok=True)  # Create the output directory if it doesn't exist
        output_path = os.path.join(output_dir, f"{os.path.basename(self.pptx_path).split('.')[0]}_info.json")
        with open(output_path, "w") as f:
            json.dump(slide_info, f, indent=2)

        return output_path