# 배포 가이드

## 환경 구분

### 개발 환경 (Development)

**특징:**
- Hot Reload 활성화 (코드 변경 시 자동 재시작)
- 백엔드 포트 직접 노출 (디버깅 용이)
- Django runserver, uvicorn --reload 사용
- volumes 마운트로 실시간 코드 반영

**실행 방법:**
```bash
# .env 사용 (개발 설정)
docker-compose -f docker-compose.dev.yml up -d

# 접속
- 프론트엔드: http://localhost:3000 (Vite dev server)
- 백엔드 Auth: http://localhost:8000
- 백엔드 API: http://localhost:8001
```

### 프로덕션 환경 (Production)

**특징:**
- 프로덕션 서버 사용 (Gunicorn, Uvicorn workers)
- 단일 진입점 (nginx 80/443)
- 백엔드 포트 외부 노출 안 함
- 빌드된 이미지 사용 (volumes 없음)
- restart 정책 적용

**실행 방법:**
```bash
# .env.production을 .env로 복사하고 수정
cp .env.production .env

# 시크릿 키 변경 필수!
nano .env

# 프로덕션 실행
docker-compose up -d --build

# 접속
- 모든 서비스: http://yourdomain.com (nginx)
  - / → 프론트엔드
  - /api/auth → 백엔드 Auth
  - /api/memos → 백엔드 API
```

## 환경변수 설정

### 개발 환경 (.env)
```env
ENVIRONMENT=development
BACKEND_AUTH_PORT=8000
BACKEND_API_PORT=8001
DJANGO_DEBUG=True
CORS_ALLOWED_ORIGINS=*
```

### 프로덕션 환경 (.env.production → .env)
```env
ENVIRONMENT=production
# 백엔드 포트 노출 안 함 (주석 처리 또는 삭제)
# BACKEND_AUTH_PORT=
# BACKEND_API_PORT=
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

## 프로덕션 체크리스트

### 필수 변경사항

- [ ] `.env.production`을 `.env`로 복사
- [ ] `JWT_SECRET_KEY` 변경 (강력한 랜덤 문자열)
- [ ] `DJANGO_SECRET_KEY` 변경 (강력한 랜덤 문자열)
- [ ] `POSTGRES_PASSWORD` 변경 (강력한 비밀번호)
- [ ] `DJANGO_DEBUG=False` 설정
- [ ] `DJANGO_ALLOWED_HOSTS` 도메인 설정
- [ ] `CORS_ALLOWED_ORIGINS` 도메인만 허용
- [ ] SSL 인증서 설정 (Let's Encrypt)

### 시크릿 키 생성 방법

```bash
# JWT 및 Django 시크릿 키 생성
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 강력한 비밀번호 생성
python -c "import secrets; print(secrets.token_urlsafe(24))"
```

## 아키텍처 비교

### 개발 환경
```
브라우저 → localhost:3000 (Vite dev)
        → localhost:8000 (Django runserver)
        → localhost:8001 (FastAPI --reload)
```

### 프로덕션 시나리오 1: 단일 서버 (Docker Compose)
```
브라우저 → yourdomain.com:80/443 (nginx)
        ├─ / → frontend:80 (컨테이너)
        ├─ /api/auth → backend-auth:8000 (컨테이너)
        └─ /api/memos → backend-api:8001 (컨테이너)

모든 서비스가 같은 서버의 Docker Compose로 동작
nginx가 컨테이너 이름으로 라우팅
```

### 프로덕션 시나리오 2: 멀티 서버 MSA
```
브라우저 → yourdomain.com (로드밸런서/API Gateway)
        ├─ / → app.yourdomain.com (프론트엔드 서버)
        ├─ /api/auth → auth.yourdomain.com (인증 서버)
        └─ /api/memos → api.yourdomain.com (API 서버)

각 서비스가 독립된 서버/도메인에서 동작
nginx가 도메인/IP로 라우팅
수평 확장 및 독립 배포 가능
```

### 프로덕션 시나리오 3: 클라우드 MSA (AWS/Azure/GCP)
```
브라우저 → CloudFront/CDN → ALB/API Gateway
        ├─ / → S3/CloudFront (정적 프론트엔드)
        ├─ /api/auth → ECS/EKS auth service (10.0.1.101)
        └─ /api/memos → ECS/EKS api service (10.0.1.102)

DB: RDS PostgreSQL (db.yourdomain.com)

VPC 내부 네트워크로 통신
Service Discovery 사용
Auto Scaling 및 Load Balancing
```

## 서버 사양 권장사항

### 최소 사양
- CPU: 2 core
- RAM: 2GB
- Disk: 20GB

### 권장 사양
- CPU: 4 core
- RAM: 4GB
- Disk: 40GB
- SSD 권장

## 백업 및 복원

### 데이터베이스 백업
```bash
docker-compose exec db pg_dump -U jwt_admin jwt_demo_db > backup.sql
```

### 데이터베이스 복원
```bash
docker-compose exec -T db psql -U jwt_admin jwt_demo_db < backup.sql
```

## 모니터링

### 로그 확인
```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f nginx
docker-compose logs -f backend-auth
docker-compose logs -f backend-api
```

### 서비스 상태 확인
```bash
docker-compose ps
```

### 리소스 사용량
```bash
docker stats
```

## 트러블슈팅

### Gunicorn worker timeout
```bash
# docker-compose.yml에서 timeout 증가
command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
```

### Uvicorn worker 수 조정
```bash
# CPU 코어 수에 맞춰 조정
command: uvicorn main:app --host 0.0.0.0 --port 8001 --workers 2
```

### 메모리 부족 시
```bash
# worker 수 줄이기
--workers 2
```

## SSL/TLS 설정 (Let's Encrypt)

```bash
# Certbot 설치
docker-compose exec nginx apk add certbot certbot-nginx

# SSL 인증서 발급
docker-compose exec nginx certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 자동 갱신 (cron)
0 0 * * * docker-compose exec nginx certbot renew --quiet
```

## 업데이트 및 배포

```bash
# 1. 코드 업데이트
git pull origin main

# 2. 이미지 재빌드
docker-compose build

# 3. 무중단 재시작
docker-compose up -d

# 4. 구버전 이미지 정리
docker image prune -f
```
