#!/bin/bash

# 설정
HARBOR_DOMAIN="harbor.chayoung.kr"
PROJECT_NAME="kr.chayoung"
IMAGE_NAME="stock-auto-betting"
TAG=$(date +%Y%m%d%H%M%S)

echo "🚀 배포 프로세스를 시작합니다..."

# 1. Harbor 로그인 (이미 로그인이 되어 있거나 환경 변수에 설정되어 있다고 가정)
# docker login $HARBOR_DOMAIN

# 2. Backend 빌드 및 태그 설정
echo "📦 백엔드 이미지 빌드 중 (linux/amd64)..."
docker build --platform linux/amd64 -t $HARBOR_DOMAIN/$PROJECT_NAME/$IMAGE_NAME-backend:latest ./backend
docker tag $HARBOR_DOMAIN/$PROJECT_NAME/$IMAGE_NAME-backend:latest $HARBOR_DOMAIN/$PROJECT_NAME/$IMAGE_NAME-backend:$TAG

# 3. Frontend 빌드 및 태그 설정
echo "📦 프론트엔드 이미지 빌드 중 (linux/amd64)..."
docker build --platform linux/amd64 -t $HARBOR_DOMAIN/$PROJECT_NAME/$IMAGE_NAME-frontend:latest ./frontend
docker tag $HARBOR_DOMAIN/$PROJECT_NAME/$IMAGE_NAME-frontend:latest $HARBOR_DOMAIN/$PROJECT_NAME/$IMAGE_NAME-frontend:$TAG

# 4. Harbor로 푸시
echo "⬆️ 이미지를 Harbor에 푸시 중..."
docker push $HARBOR_DOMAIN/$PROJECT_NAME/$IMAGE_NAME-backend:latest
docker push $HARBOR_DOMAIN/$PROJECT_NAME/$IMAGE_NAME-backend:$TAG
docker push $HARBOR_DOMAIN/$PROJECT_NAME/$IMAGE_NAME-frontend:latest
docker push $HARBOR_DOMAIN/$PROJECT_NAME/$IMAGE_NAME-frontend:$TAG

echo "✅ 이미지가 성공적으로 푸시되었습니다!"

# 5. NAS 배포 (Portainer Webhook 예시)
# Portainer 웹훅 URL이 있는 경우 여기서 호출하여 자동 재배포를 트리거할 수 있습니다.
# PORTAINER_WEBHOOK_URL="https://docker.chayoung.kr/api/stacks/webhooks/..."
# if [ ! -z "$PORTAINER_WEBHOOK_URL" ]; then
#   echo "🔄 Portainer 재배포 트리거 중..."
#   curl -X POST $PORTAINER_WEBHOOK_URL
# fi

echo "🎉 배포가 완료되었습니다!"
