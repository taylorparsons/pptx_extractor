import base64
from recreator.shape_recreators.base_shape_recreator import BaseShapeRecreator
from pptx.util import Inches
from io import BytesIO

class PictureShapeRecreator(BaseShapeRecreator):
    def can_recreate(self, shape_data):
        return shape_data["type"] == "picture"

    def recreate(self, slide, shape_data):
        left = shape_data.get("left", Inches(1))
        top = shape_data.get("top", Inches(1))
        width = shape_data.get("width", Inches(1))
        height = shape_data.get("height", Inches(1))
        base64_image = shape_data["image_data"]
        image_data = base64.b64decode(base64_image)
        pic = BytesIO(image_data)
        slide.shapes.add_picture(pic, left, top, width, height)