---
name: deploy
description: This skill should be used when the user asks to "배포", "deploy", "빌드 후 배포", "harbor에 올려", "이미지 푸시", "운영에 반영", or wants to build and push Docker images to Harbor registry.
version: 1.0.0
---

# 배포 스킬

`deploy.sh`를 실행해 백엔드/프론트엔드 Docker 이미지를 빌드하고 Harbor에 푸시합니다.
Watchtower가 60초 이내로 NAS에 자동 반영합니다.

## 실행 전 체크

```bash
# Docker 실행 여부 확인
docker info > /dev/null 2>&1 && echo "OK"

# Harbor 로그인 상태 확인
cat ~/.docker/config.json | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if 'harbor.chayoung.kr' in d.get('auths',{}) else '로그인 필요')"
```

로그인이 필요한 경우:
```bash
docker login harbor.chayoung.kr
```

## 배포 실행

```bash
bash deploy.sh
```

## 배포 후 확인

- Watchtower 폴링 주기: 60초
- NAS Portainer에서 컨테이너 재시작 여부 확인
- 텔레그램 알림으로 배치 정상 동작 확인
