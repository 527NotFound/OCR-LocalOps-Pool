# 디렉토리 구조

```md
OCR-LocalOps-Pool/
├── .gitignore
├── Jenkinsfile                   # 메인 CI/CD 파이프라인 정의
├── README.md                     # 프로젝트 설명 및 환경 설정 가이드
├── app/                          # FastAPI 백엔드 (API Gateway/Router)
│   ├── main.py                   # FastAPI Router 앱 (요청 라우팅)
│   └── requirements.txt          # FastAPI 및 HTTPX 의존성
├── worker-app/                   # OCR 워커들의 공통 애플리케이션 코드
│   ├── main.py                   # OCR Worker 공통 앱 (FastAPI 내부 프로세스)
│   ├── worker_core.py            # OCR 핵심 로직 (Tesseract, OpenCV 함수)
│   └── requirements.txt          # 워커 이미지의 Python 의존성
├── workers/                      # OCR 워커별 Dockerfile 및 설정
│   ├── Dockerfile.workerA        # 경량 워커 A Dockerfile
│   ├── Dockerfile.workerB        # 다국어 워커 B Dockerfile
│   └── Dockerfile.workerC        # 특수 전처리 워커 C Dockerfile
├── k8s/                          # Kubernetes 배포 파일 (YAML)
│   ├── base/                     
│   │   ├── ocr-namespace.yaml    
│   │   └── hpa-config.yaml       
│   ├── deployment/
│   │   ├── router-deployment.yaml
│   │   ├── worker-a-deployment.yaml 
│   │   ├── worker-b-deployment.yaml 
│   │   └── worker-c-deployment.yaml 
│   └── service/
│       ├── router-service.yaml
│       ├── worker-a-service.yaml    
│       ├── router-service.yaml      
│       └── worker-b-service.yaml    
├── frontend/                     # React 프론트엔드 (대시보드/테스트 UI)
│   ├── src/
│   │   └── App.js
│   ├── package.json
│   └── Dockerfile.fe             
└── scripts/                      # 환경 설정을 위한 스크립트
    ├── setup_k3s.sh              # Kali Linux VM에서 K3s 설치 스크립트
    └── setup_registry.sh         # Local Docker Registry 설정 스크립트
```
