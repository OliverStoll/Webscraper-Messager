from PIL import Image
import base64
from io import BytesIO


def check_if_icon_green(base64_str, threshold):
    img = Image.open(BytesIO(base64.b64decode(base64_str)))
    total_green_values = 0
    for pixel in img.getdata():
        total_green_values += pixel[1] - (pixel[0] + pixel[2]) // 2
    is_green = total_green_values > threshold
    return is_green