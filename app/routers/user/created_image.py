import random
from PIL import Image, ImageDraw, ImageFont

# Constants
MAX_FONT_SIZE = 150
MIN_FONT_SIZE = 10
FONT_STEP = 10
IMAGE_WIDTH = 180
IMAGE_HEIGHT = 180

def generate_random_color() -> tuple:
    """Generate a random color as a tuple of three integers"""
    return tuple(random.choices(range(256), k=3))

def get_font(size: int) -> ImageFont:
    """Get a font with the specified size"""
    try:
        return ImageFont.load_default(size=size)
    except IOError:
        return ImageFont.load_default()

def get_text_bbox(draw: ImageDraw, text: str, font: ImageFont) -> tuple:
    """Get the bounding box of the text"""
    return draw.textbbox((0, 0), text, font=font)

def generate_image_with_letter(text: str) -> None:
    """Generate an image with a single letter"""
    # Create an image with a random background color
    background_color = generate_random_color()
    image = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), background_color)
    draw = ImageDraw.Draw(image)

    # Get the first letter of the text
    first_letter = text[0].upper() if text else ''

    # Find a font size that fits the image
    font_size = MAX_FONT_SIZE
    while True:
        font = get_font(font_size)
        bbox = get_text_bbox(draw, first_letter, font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        if text_width <= IMAGE_WIDTH and text_height <= IMAGE_HEIGHT:
            break
        font_size -= FONT_STEP
        if font_size < MIN_FONT_SIZE:
            break

    # Calculate the text position for centered rendering
    text_x = (IMAGE_WIDTH - text_width) // 2
    text_y = (IMAGE_HEIGHT // text_height)# // 2 + text_height // 8 # Adjust vertical positioning

    # Draw the text on the image
    draw.text((text_x, text_y), first_letter, fill="black", font=font)

    # Save the image as a PNG file
    image.save("app/routers/user/image/output.png")

# Example usage
# generate_image_with_letter("ello")