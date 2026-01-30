import base64
from recreator.shape_recreators.base_shape_recreator import BaseShapeRecreator
from pptx.util import Inches, Emu
from io import BytesIO

class PictureShapeRecreator(BaseShapeRecreator):
    def can_recreate(self, shape_data):
        return shape_data["type"] == "picture"

    def apply_to_shape(self, shape, shape_data):
        # python-pptx doesn't provide a stable public API for replacing an image in-place.
        # If we matched an existing picture shape on the template slide, keep it as-is to
        # preserve its original image/style and avoid duplicating it.
        return True

    def recreate(self, slide, shape_data):
        left = Emu(int(shape_data["left"])) if isinstance(shape_data.get("left"), (int, float)) else shape_data.get("left", Inches(1))
        top = Emu(int(shape_data["top"])) if isinstance(shape_data.get("top"), (int, float)) else shape_data.get("top", Inches(1))
        width = Emu(int(shape_data["width"])) if isinstance(shape_data.get("width"), (int, float)) else shape_data.get("width", Inches(1))
        height = Emu(int(shape_data["height"])) if isinstance(shape_data.get("height"), (int, float)) else shape_data.get("height", Inches(1))
        base64_image = shape_data["image_data"]
        image_data = base64.b64decode(base64_image)
        pic = BytesIO(image_data)
        slide.shapes.add_picture(pic, left, top, width, height)
