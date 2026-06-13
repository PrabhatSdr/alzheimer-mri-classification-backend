from PIL import Image

img = Image.new("RGB", (300, 300), color=(100, 150, 200))
img.save("test.jpg")

print("Image created successfully")