# OCR-LocalOps-Pool

로컬 환경(Kali Linux VM)에서 Jenkins CI/CD와 Kubernetes(K3s)를 활용하여 OCR 워커풀을 자동 빌드/배포하는 파이프라인 프로젝트입니다.

## 프로젝트 개요

이미지에서 텍스트를 추출하는 OCR 서비스를 **3종의 특화 워커**로 분리하고, FastAPI 라우터가 요청 조건(언어, 이미지 품질)에 따라 적절한 워커로 자동 라우팅하는 구조입니다.

### 워커 구성

| 워커 | 역할 | 라우팅 조건 |
|------|------|-------------|
| **Worker A** | 경량/고속 OCR | 영어 + 고품질 이미지 (기본) |
| **Worker B** | 다국어 OCR | 한국어, 일본어 요청 |
| **Worker C** | 전처리 특화 OCR | 저품질 이미지 (노이즈 제거, 이진화 등) |

### 인프라 흐름

사용자 (React UI) → FastAPI Router → Worker A / B / C (Tesseract OCR)
↑
Jenkins CI/CD → Docker Build → K3s 배포 (HPA 오토스케일링)



## 기술 스택

- **Backend:** FastAPI, Tesseract, OpenCV, Pillow
- **Frontend:** React (워커 상태 대시보드 + OCR 테스트 UI)
- **Infra:** Docker, K3s, Kubernetes HPA, Jenkins, Nginx
- **환경:** Kali Linux VM, 로컬 Docker Registry

## 디렉토리 구조

```md
OCR-LocalOps-Pool/
├── Jenkinsfile                   # CI/CD 파이프라인 정의
├── app/                          # FastAPI 라우터 (API Gateway)
│   ├── main.py                   # 요청 조건 기반 워커 라우팅 로직
│   └── requirements.txt
├── worker-app/                   # OCR 워커 공통 코드
│   ├── main.py                   # 워커 FastAPI 엔드포인트
│   ├── worker_core.py            # OCR 핵심 로직 (전처리 + Tesseract)
│   └── requirements.txt
├── workers/                      # 워커별 Dockerfile
│   ├── Dockerfile.workerA        # 경량 워커
│   ├── Dockerfile.workerB        # 다국어 워커
│   └── Dockerfile.workerC        # 전처리 특화 워커
├── k8s/                          # Kubernetes 배포 매니페스트
│   ├── base/                     # 네임스페이스, HPA 설정
│   ├── deployment/               # 라우터 + 워커 Deployment
│   └── service/                  # ClusterIP / NodePort Service
├── frontend/                     # React 대시보드 / 테스트 UI
│   ├── src/App.js
│   ├── package.json
│   └── Dockerfile.fe
└── scripts/                      # 환경 설정 스크립트
    ├── setup_k3s.sh              # K3s 설치
    └── setup_registry.sh         # 로컬 Docker Registry 설정
