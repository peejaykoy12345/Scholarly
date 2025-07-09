import os
from fitz import open as fitz_open
from paddleocr import PaddleOCR
from PIL import Image, ImageFilter, ImageOps
from random import randint

ocr = PaddleOCR(use_angle_cls=True, lang='en')


supported_image_files = {'png', 'jpg', 'jpeg'}

def preprocess_image(image_path):
    image = Image.open(image_path)
    """.convert("L")
    image = ImageOps.invert(image)
    image = image.point(lambda x: 0 if x < 140 else 255)  
    image = image.filter(ImageFilter.SHARPEN)
    image = image.resize((image.width * 2, image.height * 2))"""
    return image.convert("RGB")  


def is_supported_image_file(path: str) -> bool:
    ext = os.path.splitext(path)[1].lower().lstrip('.')
    return ext in supported_image_files

def extract_handwritten_text(image_path):
    results = ocr.ocr(image_path, cls=True)
    extracted_text = []

    for line in results[0]:
        text = line[1][0]
        extracted_text.append(text)

    return "\n".join(extracted_text)

def extract_pdf_text(pdf_path: str) -> str:
    doc = fitz_open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    print(text)
    return text.strip() if text else "No text found."

def extract_text(path: str) -> str:
    if path.lower().endswith('.pdf'):
        return extract_pdf_text(path)
    elif is_supported_image_file(path):
        return extract_handwritten_text(path)
    else:
        return "❌ Unsupported file type."
