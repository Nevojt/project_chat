from PIL import Image, ImageDraw, ImageFont
import random

def generate_image_with_letter(text):
    # Розміри зображення
    width, height = 30, 35

    # Створення зображення з випадковим кольором фону
    background_color = tuple(random.choices(range(256), k=3))
    image = Image.new('RGB', (width, height), background_color)
    
    # Малювання
    draw = ImageDraw.Draw(image)
    
    # Визначення шрифта та розміру тексту
    # Збільшуємо розмір шрифту до максимально можливого
    font_size = 150
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    
    while True:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
            bbox = draw.textbbox((0, 0), text[0].upper(), font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            if text_width <= width and text_height <= height:
                break
            font_size -= 10
        except OSError:
            font = ImageFont.load_default()
            break
    
    # Отримання першої літери рядка у верхньому регістрі
    first_letter = text[0].upper() if text else ''
    
    # Отримання розмірів тексту
    bbox = draw.textbbox((0, 0), first_letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Розрахунок позиції тексту для центрованого відображення
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    
    # Випадковий колір тексту
    text_color = tuple(random.choices(range(256), k=3))
    
    # Малювання тексту на зображенні
    draw.text((text_x, text_y), first_letter, fill=text_color, font=font)
    
    # Збереження зображення у форматі PNG
    image.save("output.png")

# Приклад використання функції
generate_image_with_letter("hello")
