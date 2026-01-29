import base64
from extractors.shape_extractors.base_shape_extractor import BaseShapeExtractor
from pptx.enum.shapes import MSO_SHAPE_TYPE
from io import BytesIO

class PictureShapeExtractor(BaseShapeExtractor):
    def can_extract(self, shape):
        return shape.shape_type == MSO_SHAPE_TYPE.PICTURE

    def extract(self, shape):
        pic = shape
        image_data = BytesIO(pic.image.blob)
        base64_image = base64.b64encode(image_data.getvalue()).decode('utf-8')
        return {
            "type": "picture",
            "image_data": base64_image
        }