#!/bin/bash
# UTM 가상환경(Kali Linux)에서 실행

echo "--- 🐳 Local Docker Registry 설정 시작 ---"

# 1. Docker 설치 확인 (설치되어 있지 않다면 먼저 설치해야 함)
if ! command -v docker &> /dev/null
then
    echo "Docker가 설치되어 있지 않습니다. 먼저 Docker를 설치해주세요."
    exit 1
fi

# 2. Local Registry 컨테이너 실행 (포트 5000)
# K8s와 Jenkins가 이 VM의 5000 포트로 이미지에 접근합니다.
docker run -d -p 5000:5000 --restart=always --name local-registry registry:2

echo "Local Registry가 localhost:5000에서 실행 중입니다."

# 3. K3s에 Insecure Registry 설정 추가 (선택 사항이지만 권장)
# K3s가 HTTPS가 아닌 로컬 HTTP 레지스트리에서 이미지를 가져올 수 있도록 허용
VM_IP=$(hostname -I | awk '{print $1}')
echo "VM IP: $VM_IP"

# K3s 설정을 위한 파일 생성 및 서비스 재시작
K3S_CONFIG_FILE="/etc/rancher/k3s/registries.yaml"
sudo mkdir -p /etc/rancher/k3s
echo "mirrors:
  \"$VM_IP:5000\":
    endpoint:
      - \"http://$VM_IP:5000\"" | sudo tee $K3S_CONFIG_FILE

echo "K3s Insecure Registry 설정 완료. K3s를 재시작합니다."
sudo systemctl restart k3s

echo "--- ✅ Local Registry 설정 완료 ---"