import os
import numpy as np
from PIL import Image, ImageDraw

os.makedirs("data", exist_ok=True)

def create_sample_bmp(filename, text):
    img = Image.new("L", (100, 100), color=255)
    draw = ImageDraw.Draw(img)
    
    if text == "1":
        draw.line([(50, 10), (50, 90)], fill=0, width=12)
    elif text == "0":
        draw.rectangle([(20, 20), (80, 80)], outline=0, width=12)
    elif text == "2":
        draw.line([(20, 20), (80, 20)], fill=0, width=10)
        draw.line([(80, 20), (20, 80)], fill=0, width=10)
        draw.line([(20, 80), (80, 80)], fill=0, width=10)
        
    img.save(f"data/{filename}.bmp")

create_sample_bmp("digit_0", "0")
create_sample_bmp("digit_1", "1")
create_sample_bmp("digit_2", "2")

print("Тестові .bmp файли успішно створені в папці data/")