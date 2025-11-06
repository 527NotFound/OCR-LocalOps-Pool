# workers/worker_core.py
from PIL import Image
import pytesseract
import cv2
import numpy as np
import io

# Tesseract 경로 설정 (필요 시)
# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract' 

def preprocess_standard(image_bytes: bytes) -> Image.Image:
    """기본 이미지 전처리 (바이트 -> PIL Image)"""
    return Image.open(io.BytesIO(image_bytes))

def preprocess_complex(image_bytes: bytes) -> Image.Image:
    """Worker C를 위한 복잡한 전처리: 기울기 보정, 노이즈 제거 등"""
    image_np = np.array(Image.open(io.BytesIO(image_bytes)).convert('RGB'))
    image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    
    # 1. Grayscale 변환
    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    
    # 2. 노이즈 제거 (가우시안 블러)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 3. 임계값(Threshold) 적용 (이진화)
    # OTSU 방식을 적용하여 최적의 임계값을 자동으로 찾음
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 처리된 이미지를 PIL Image로 변환하여 반환
    return Image.fromarray(cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB))


def run_ocr(pil_image: Image.Image, lang_code: str, config: str = '') -> str:
    """Tesseract OCR 엔진을 실행합니다."""
    # lang_code는 Tesseract가 설치된 언어 팩에 따라 달라집니다.
    return pytesseract.image_to_string(pil_image, lang=lang_code, config=config)