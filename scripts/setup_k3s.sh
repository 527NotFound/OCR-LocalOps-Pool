#!/bin/bash
# UTM 가상환경(Kali Linux)에서 실행

echo "--- 🚀 K3s (Lightweight Kubernetes) 설치 시작 ---"

# 1. K3s 설치 (단일 노드 클러스터)
# K3s는 기본적으로 systemd 서비스를 등록하고 실행합니다.
curl -sfL https://get.k3s.io | sh - 

# 2. kubectl 명령어 사용을 위한 환경 설정
echo "KUBECONFIG 환경 변수 설정"
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# 3. Kubeconfig 파일을 현재 사용자 홈 디렉토리로 복사 및 권한 설정
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config

# 4. 설치 확인
echo "--- ✅ K3s 설치 완료. 클러스터 상태 확인 ---"
kubectl get nodes
kubectl version --short

# 5. Jenkins가 사용할 Namespace 미리 생성
kubectl create namespace ocr-dev

echo "K8s 환경 설정 완료. kubectl 명령어를 사용할 수 있습니다."