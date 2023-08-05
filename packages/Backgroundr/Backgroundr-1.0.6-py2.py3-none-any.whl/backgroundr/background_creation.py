from PIL import Image, ImageFont, ImageDraw


def create_background(size, color):
    image = Image.new('RGB', size, color)
    return image


def add_text(image, text, font_path, size=32):
    font = ImageFont.truetype(font_path, size)
    draw = ImageDraw.Draw(image)
    coordinates = get_center_coordinates(image, font, text)
    draw.text(coordinates, text, font=font)


def get_center_coordinates(image, font, text):
    image_width = image.size[0]
    image_height = image.size[1]
    text_width = font.getsize(text)[0]
    text_height = font.getsize(text)[1]
    return (image_width / 2) - (text_width / 2), (image_height / 2) - (text_height / 2)