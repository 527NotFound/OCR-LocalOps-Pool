# worker-app/main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from starlette.responses import JSONResponse
from .worker_core import preprocess_standard, preprocess_complex, run_ocr # worker_core.py 참조
import os

# 환경 변수 로드 (K8s Deployment YAML에서 설정)
WORKER_ID = os.getenv("WORKER_ID", "UNKNOWN")
TESSERACT_LANGS = os.getenv("TESSERACT_LANGS", "eng")
PREPROCESS_MODE = os.getenv("PREPROCESS_MODE", "STANDARD") 

app = FastAPI(title=f"OCR Worker {WORKER_ID} Service")

@app.get("/health")
async def health_check():
    """워커의 상태를 확인합니다."""
    return {"status": "OK", "worker_id": WORKER_ID, "langs": TESSERACT_LANGS, "mode": PREPROCESS_MODE}

@app.post("/ocr/internal_process")
async def process_ocr(
    file: UploadFile = File(...),
    language: str = Form("ENG"),
    quality: str = Form("HIGH")
):
    """
    라우터에서 전달된 OCR 요청을 처리합니다.
    (이전 대화에서 설계된 worker_core.py의 함수들을 사용)
    """
    try:
        image_bytes = await file.read()
        
        # 1. 전처리 모드 선택
        if PREPROCESS_MODE == "COMPLEX":
            pil_image = preprocess_complex(image_bytes)
        else:
            pil_image = preprocess_standard(image_bytes)
        
        # 2. OCR 실행
        lang_code = language.lower()
        ocr_text = run_ocr(pil_image, lang_code) # run_ocr 함수는 Tesseract 설정에 따라 처리
        
        # 3. 결과 반환
        return {
            "worker_id": WORKER_ID,
            "preprocess_mode": PREPROCESS_MODE,
            "detected_text": ocr_text.strip()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Internal OCR processing failed: {e}"
        )