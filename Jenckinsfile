// Jenkinsfile (Declarative Pipeline)
pipeline {
    agent any // Jenkins 워커 노드에서 실행

    environment {
        // 💡 로컬 레지스트리 주소 (UTM VM IP 주소로 대체 필요)
        REGISTRY = '192.168.1.100:5000'
        NAMESPACE = 'ocr-dev'
    }

    stages {
        stage('Build Frontend Image') {
            steps {
                script {
                    echo "Building Frontend Image..."
                    def feImage = "${REGISTRY}/ocr-frontend:latest"
                    dir('frontend') {
                        // frontend/Dockerfile.fe 빌드
                        sh "docker build -t ${feImage} -f Dockerfile.fe ."
                        sh "docker push ${feImage}"
                    }
                }
            }
        }
        
        stage('Build Router Image') {
            steps {
                script {
                    echo "Building Router Image..."
                    def routerImage = "${REGISTRY}/ocr-router:latest"
                    dir('app') {
                        // Router용 Dockerfile이 없으므로, 기본 Python 이미지 사용
                        sh "docker build -t ${routerImage} -f Dockerfile ."
                    }
                    sh "docker push ${routerImage}"
                }
            }
        }

        stage('Build Worker Images') {
            steps {
                script {
                    // Worker A (Lightweight)
                    sh "docker build -t ${REGISTRY}/ocr-worker-a:latest -f workers/Dockerfile.workerA ."
                    sh "docker push ${REGISTRY}/ocr-worker-a:latest"
                    
                    // Worker B (Multi-language)
                    sh "docker build -t ${REGISTRY}/ocr-worker-b:latest -f workers/Dockerfile.workerB ."
                    sh "docker push ${REGISTRY}/ocr-worker-b:latest"
                    
                    // Worker C (Pre-processing/HPA)
                    sh "docker build -t ${REGISTRY}/ocr-worker-c:latest -f workers/Dockerfile.workerC ."
                    sh "docker push ${REGISTRY}/ocr-worker-c:latest"
                }
            }
        }

        stage('Deploy to K3s (Apply YAMLs)') {
            steps {
                // K3s (kubectl)이 Jenkins 워커 노드에 설정되어 있어야 함
                // 1. 네임스페이스 생성 (이미 스크립트에서 했지만, idempotent하게 다시 실행)
                sh "kubectl apply -f k8s/base/ocr-namespace.yaml"
                
                // 2. Worker Services (ClusterIP) 배포 (Router가 의존하므로 먼저 실행)
                sh "kubectl apply -f k8s/service/worker-a-service.yaml"
                sh "kubectl apply -f k8s/service/worker-b-service.yaml"
                sh "kubectl apply -f k8s/service/worker-c-service.yaml"
                
                // 3. Router Service (NodePort) 배포
                sh "kubectl apply -f k8s/service/router-service.yaml"
                
                // 4. Deployment (Pod) 배포
                sh "kubectl apply -f k8s/deployment/worker-a-deployment.yaml"
                sh "kubectl apply -f k8s/deployment/worker-b-deployment.yaml"
                sh "kubectl apply -f k8s/deployment/worker-c-deployment.yaml"
                sh "kubectl apply -f k8s/deployment/router-deployment.yaml"
                
                // 5. HPA 및 Frontend 배포 (Frontend Deployment/Service YAML 추가 가정)
                sh "kubectl apply -f k8s/base/hpa-config.yaml"
                // sh "kubectl apply -f k8s/deployment/frontend-deployment.yaml"
                // sh "kubectl apply -f k8s/service/frontend-service.yaml"
                
                echo "Deployment Complete. Check K3s cluster for running services."
            }
        }
    }
}