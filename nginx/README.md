# Nginx 리버스 프록시 설정

Nginx를 사용하여 프론트엔드와 백엔드 서비스를 하나의 도메인으로 통합하는 리버스 프록시 설정입니다.

## 구성

### 기본 구조

```
Nginx (80/443)
├── / → Frontend (React)
├── /api/auth/ → Backend Auth (DRF:8000)
└── /api/memos → Backend API (FastAPI:8001)
```

### 포트 매핑

- **외부**: 80 (HTTP), 443 (HTTPS)
- **내부**:
  - Frontend: 80
  - Backend Auth (DRF): 8000
  - Backend API (FastAPI): 8001

## Docker Compose로 실행

루트 디렉토리에서:

```bash
docker-compose up -d
```

모든 서비스가 시작되면 `http://localhost`로 접속 가능합니다.

## EC2에서 실제 운영 환경 설정

### 1. 기본 설정 (HTTP만 사용)

Docker Compose로 실행:

```bash
# 프로젝트 클론
git clone <repository-url>
cd jwt-docker-demo

# .env 파일 수정 (필요시)
nano .env

# Docker Compose 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

브라우저에서 `http://<EC2-Public-IP>`로 접속

### 2. HTTPS 설정 (Let's Encrypt)

#### 2.1. Certbot 설치

```bash
# EC2 Ubuntu 기준
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

#### 2.2. SSL 인증서 발급

```bash
# 도메인이 EC2 IP를 가리키고 있어야 함
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com
```

인증서는 다음 경로에 저장됩니다:
- Certificate: `/etc/letsencrypt/live/your-domain.com/fullchain.pem`
- Private Key: `/etc/letsencrypt/live/your-domain.com/privkey.pem`

#### 2.3. Nginx 설정에 SSL 추가

`nginx/nginx.conf` 파일에서 HTTPS 섹션의 주석을 해제하고 도메인을 수정:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # location 블록들...
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

#### 2.4. Docker Compose에 SSL 볼륨 마운트 추가

`docker-compose.yml`의 nginx 섹션에 추가:

```yaml
nginx:
  volumes:
    - /etc/letsencrypt:/etc/letsencrypt:ro
```

#### 2.5. 서비스 재시작

```bash
docker-compose down
docker-compose up -d
```

#### 2.6. 자동 갱신 설정

```bash
# crontab 편집
sudo crontab -e

# 매일 새벽 2시에 갱신 시도 (성공 시 nginx 재시작)
0 2 * * * certbot renew --quiet && docker-compose -f /path/to/jwt-docker-demo/docker-compose.yml restart nginx
```

### 3. 프론트엔드 환경변수 수정 (중요!)

프로덕션 환경에서는 `frontend/.env` 파일을 수정해야 합니다:

```bash
# HTTP 사용 시
VITE_API_AUTH_URL=http://your-domain.com/api/auth
VITE_API_MEMOS_URL=http://your-domain.com/api/memos

# HTTPS 사용 시
VITE_API_AUTH_URL=https://your-domain.com/api/auth
VITE_API_MEMOS_URL=https://your-domain.com/api/memos
```

**중요**: 환경변수 수정 후 프론트엔드를 다시 빌드해야 합니다!

```bash
docker-compose build frontend
docker-compose up -d frontend
```

### 4. 보안 설정

#### 4.1. 방화벽 설정 (UFW)

```bash
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS
sudo ufw enable
sudo ufw status
```

#### 4.2. .env 파일 보안

```bash
# .env 파일 권한 제한
chmod 600 .env

# 프로덕션에서는 강력한 비밀번호로 변경!
nano .env
```

변경해야 할 값들:
- `POSTGRES_PASSWORD`: 강력한 비밀번호
- `JWT_SECRET_KEY`: 랜덤 문자열 (최소 32자)
- `DJANGO_SECRET_KEY`: 랜덤 문자열
- `DJANGO_DEBUG=False`: 디버그 모드 비활성화

#### 4.3. CORS 설정 변경

**DRF (backend-auth/config/settings.py)**:
```python
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://your-domain.com",
    "http://your-domain.com",
]
```

**FastAPI (backend-api/main.py)**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

변경 후 재빌드:
```bash
docker-compose build backend-auth backend-api
docker-compose up -d
```

### 5. 모니터링

#### 로그 확인
```bash
# 모든 서비스 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f nginx
docker-compose logs -f backend-auth
docker-compose logs -f backend-api
docker-compose logs -f frontend

# Nginx 액세스 로그
docker exec jwt-nginx tail -f /var/log/nginx/access.log

# Nginx 에러 로그
docker exec jwt-nginx tail -f /var/log/nginx/error.log
```

#### 서비스 상태 확인
```bash
# 실행 중인 컨테이너
docker-compose ps

# 리소스 사용량
docker stats

# 헬스 체크
curl http://localhost/health
```

### 6. 백업

#### 데이터베이스 백업
```bash
# PostgreSQL 백업
docker exec jwt-postgres pg_dump -U jwtuser jwtdemo > backup_$(date +%Y%m%d).sql

# 복원
docker exec -i jwt-postgres psql -U jwtuser jwtdemo < backup_20240101.sql
```

#### 전체 볼륨 백업
```bash
# 볼륨 백업
docker run --rm -v jwt-docker-demo_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz /data

# 복원
docker run --rm -v jwt-docker-demo_postgres_data:/data -v $(pwd):/backup ubuntu tar xzf /backup/postgres_backup.tar.gz -C /
```

## Nginx 설정 파일 설명

### Upstream 설정

```nginx
upstream backend_auth {
    server backend-auth:8000;
}

upstream backend_api {
    server backend-api:8001;
}

upstream frontend {
    server frontend:80;
}
```

Docker Compose 네트워크 내에서 서비스 이름으로 통신합니다.

### Location 블록

```nginx
# 프론트엔드: 모든 경로
location / {
    proxy_pass http://frontend;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# DRF 인증 API: /api/auth/*
location /api/auth/ {
    proxy_pass http://backend_auth/api/auth/;
    # 헤더 설정...
}

# FastAPI 메모 API: /api/memos*
location /api/memos {
    proxy_pass http://backend_api/api/memos;
    # 헤더 설정...
}
```

### Gzip 압축

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript ...;
```

응답 데이터를 압축하여 전송 속도를 향상시킵니다.

## 트러블슈팅

### 502 Bad Gateway

**원인**: 백엔드 서비스가 시작되지 않았거나 연결 불가

**해결**:
```bash
# 서비스 상태 확인
docker-compose ps

# 서비스 재시작
docker-compose restart backend-auth backend-api

# 로그 확인
docker-compose logs backend-auth backend-api
```

### CORS 에러

**원인**: 프론트엔드와 백엔드의 도메인이 다름

**해결**:
1. Nginx를 통해 같은 도메인으로 통합 (현재 구성)
2. 백엔드의 CORS 설정에 프론트엔드 도메인 추가

### SSL 인증서 갱신 실패

**원인**: 80 포트가 차단되어 있거나 도메인 DNS 설정이 잘못됨

**해결**:
```bash
# 80 포트 확인
sudo netstat -tlnp | grep :80

# DNS 확인
nslookup your-domain.com

# 수동 갱신 시도
sudo certbot renew --dry-run
```

### 프론트엔드 API 호출 실패

**원인**: 환경변수가 빌드 시점에 반영되지 않음

**해결**:
```bash
# .env 수정 후 프론트엔드 재빌드
docker-compose build frontend
docker-compose up -d frontend
```

## 성능 최적화

### Nginx 캐싱

```nginx
# 정적 파일 캐싱
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 연결 풀링

```nginx
upstream backend_auth {
    server backend-auth:8000;
    keepalive 32;
}
```

### 워커 프로세스 조정

```nginx
worker_processes auto;  # CPU 코어 수만큼 자동 설정
worker_connections 1024;  # 동시 연결 수
```

## 추가 기능

### Rate Limiting (요청 제한)

```nginx
http {
    limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;

    server {
        location /api/ {
            limit_req zone=mylimit burst=20 nodelay;
            # ...
        }
    }
}
```

### Basic Auth (관리자 페이지 보호)

```bash
# htpasswd 설치
sudo apt install apache2-utils

# 비밀번호 파일 생성
htpasswd -c /etc/nginx/.htpasswd admin
```

```nginx
location /admin/ {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://backend_auth/admin/;
}
```

## 참고 자료

- [Nginx 공식 문서](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Docker Compose Networking](https://docs.docker.com/compose/networking/)
