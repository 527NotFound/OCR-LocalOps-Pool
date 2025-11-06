# app/main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from starlette.requests import Request
from starlette.responses import JSONResponse
import httpx
import os

app = FastAPI(
    title="OCR LocalOps Pool Router/API Gateway", 
    description="Intelligently routes OCR requests to the appropriate Worker Pool (A, B, or C)."
)

# ----------------------------------------------------
# 🔍 K8s Service 환경 변수 (Kubernetes 내부 DNS 사용)
# K3s/MicroK8s에서 배포 시, Service Name으로 접근 가능
# ----------------------------------------------------
WORKER_A_SERVICE = os.getenv("WORKER_A_SERVICE_URL", "http://worker-a-fast-service.ocr-dev")
WORKER_B_SERVICE = os.getenv("WORKER_B_SERVICE_URL", "http://worker-b-multi-service.ocr-dev")
WORKER_C_SERVICE = os.getenv("WORKER_C_SERVICE_URL", "http://worker-c-prep-service.ocr-dev")

@app.get("/status")
async def get_router_status():
    """라우터 및 워커 서비스의 상태를 확인합니다."""
    # 실제 구현 시, 각 워커의 /health 엔드포인트에 요청을 보내 상태를 취합합니다.
    return {"status": "Router Operational", "workers_configured": ["A", "B", "C"]}

@app.post("/ocr/process")
async def route_ocr_request(
    file: UploadFile = File(..., description="OCR 처리를 위한 이미지 파일"),
    language: str = Form("ENG", description="요청 언어 (ENG, KOR, JPN 등)"),
    quality: str = Form("HIGH", description="이미지 품질 힌트 (HIGH, LOW)")
):
    """
    들어온 OCR 요청을 분석하여 가장 적절한 워커풀로 라우팅합니다.
    """
    
    # 1. 🎯 지능형 워커 선택 로직
    # 요청 메타데이터(언어, 품질)를 기반으로 대상 워커 서비스를 결정합니다.
    
    target_worker_url = None
    worker_id = None
    
    # CASE 1: 특수 전처리 요구 (저품질 이미지) -> Worker C (OpenCV 특화)
    if quality.upper() == "LOW":
        target_worker_url = WORKER_C_SERVICE
        worker_id = "C (Pre-processing)"
        
    # CASE 2: 다국어 요구 (KOR, JPN) -> Worker B (다국어 팩)
    elif language.upper() in ["KOR", "JPN"]:
        target_worker_url = WORKER_B_SERVICE
        worker_id = "B (Multi-language)"
        
    # CASE 3: 기본 또는 고품질/영어 요청 -> Worker A (경량/고속)
    else: # Default to ENG and HIGH quality
        target_worker_url = WORKER_A_SERVICE
        worker_id = "A (Fast/Standard)"

    print(f"Routing request (Lang: {language}, Quality: {quality}) to Worker {worker_id}")

    # 2. 🚀 요청 프록시 (비동기 HTTP 클라이언트 사용)
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 워커에게 전달할 파일 및 폼 데이터 준비
            files = {'file': (file.filename, file.file, file.content_type)}
            data = {'language': language, 'quality': quality}
            
            # **워커의 내부 OCR 엔드포인트**로 요청 전달
            response = await client.post(
                f"{target_worker_url}/ocr/internal_process", 
                files=files, 
                data=data
            )
            
            # 3. 📝 결과 처리 및 응답 반환
            response.raise_for_status() # HTTP 상태 코드가 4xx 또는 5xx일 경우 예외 발생
            
            ocr_result = response.json()
            ocr_result["routed_by"] = f"Router to Worker {worker_id}"
            
            return JSONResponse(content=ocr_result, status_code=status.HTTP_200_OK)

        except httpx.HTTPStatusError as e:
            # 워커에서 발생한 에러를 클라이언트에게 전달
            print(f"Worker {worker_id} failed: {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code, 
                detail=f"OCR Worker Error ({worker_id}): {e.response.text}"
            )
        except Exception as e:
            # 기타 네트워크 또는 I/O 에러 처리
            print(f"Routing/Network Error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail=f"Could not connect to OCR Worker {worker_id}. Service may be down."
            )