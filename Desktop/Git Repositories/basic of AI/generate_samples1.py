import os
from PIL import Image, ImageDraw

os.makedirs("data/class_1", exist_ok=True)
os.makedirs("data/class_0", exist_ok=True)

# Варіанти для Класу 1 (вертикальні смуги різної товщини)
img1 = Image.new("L", (100, 100), color=255)
ImageDraw.Draw(img1).line([(50, 10), (50, 90)], fill=0, width=8)
img1.save("data/class_1/sample_1.bmp")

img2 = Image.new("L", (100, 100), color=255)
ImageDraw.Draw(img2).line([(45, 10), (45, 90)], fill=0, width=16)
img2.save("data/class_1/sample_2.bmp")

# Варіанти для Класу 0 (квадрати/овали різного розміру)
img3 = Image.new("L", (100, 100), color=255)
ImageDraw.Draw(img3).rectangle([(20, 20), (80, 80)], outline=0, width=10)
img3.save("data/class_0/sample_1.bmp")

img4 = Image.new("L", (100, 100), color=255)
ImageDraw.Draw(img4).rectangle([(30, 30), (70, 70)], outline=0, width=14)
img4.save("data/class_0/sample_2.bmp")

print("Зразки для навчання створено в папках data/class_0/ та data/class_1/")