# JWT Docker Demo

Docker Compose를 사용한 JWT 인증 기반 풀스택 애플리케이션 데모입니다.

## 프로젝트 개요

이 프로젝트는 마이크로서비스 아키텍처를 활용한 간단한 메모 관리 애플리케이션입니다.

### 주요 기능

- **사용자 인증**: JWT 토큰 기반 회원가입/로그인
- **메모 관리**: 개인 메모 생성, 조회, 수정, 삭제 (CRUD)
- **보안**: JWT 토큰 검증, 사용자별 데이터 분리
- **확장성**: 마이크로서비스 구조로 각 기능 분리

### 기술 스택

| 계층 | 기술 | 역할 |
|------|------|------|
| **Frontend** | React 18 + Vite | 사용자 인터페이스 |
| **인증 API** | Django REST Framework | JWT 발급 및 사용자 관리 |
| **메모 API** | FastAPI | 메모 CRUD 및 JWT 검증 |
| **Database** | PostgreSQL 15 | 데이터 저장 |
| **Reverse Proxy** | Nginx | 라우팅 및 로드밸런싱 |
| **Orchestration** | Docker Compose | 컨테이너 관리 |

### 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                        Nginx (:80)                          │
│                     Reverse Proxy                           │
└──────┬──────────────────┬─────────────────┬────────────────┘
       │                  │                 │
       ▼                  ▼                 ▼
  ┌─────────┐      ┌────────────┐    ┌─────────────┐
  │ React   │      │ DRF        │    │ FastAPI     │
  │ (Vite)  │      │ Auth API   │    │ Memo API    │
  │  :80    │      │  :8000     │    │  :8001      │
  └─────────┘      └─────┬──────┘    └──────┬──────┘
                         │                  │
                         └──────┬───────────┘
                                ▼
                         ┌─────────────┐
                         │ PostgreSQL  │
                         │   :5432     │
                         └─────────────┘
```

### API 흐름

```
1. 회원가입/로그인
   Frontend → DRF → PostgreSQL
   DRF → JWT 토큰 발급 → Frontend (localStorage 저장)

2. 메모 CRUD
   Frontend (JWT 포함) → FastAPI → JWT 검증 → PostgreSQL
   FastAPI → 응답 → Frontend
```

## 프로젝트 구조

```
jwt-docker-demo/
├── docker-compose.yml          # Docker Compose 설정
├── .env                        # 환경변수 설정
├── .gitignore                  # Git 제외 파일
├── README.md                   # 이 파일
│
├── backend-auth/               # Django REST Framework (인증)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── entrypoint.sh
│   ├── manage.py
│   ├── config/                 # Django 설정
│   │   ├── settings.py         # 프로젝트 설정
│   │   ├── urls.py             # URL 라우팅
│   │   └── wsgi.py
│   ├── authentication/         # 인증 앱
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── README.md
│
├── backend-api/                # FastAPI (메모 CRUD)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                 # FastAPI 앱 (lifespan)
│   ├── models.py               # SQLAlchemy 모델
│   ├── schemas.py              # Pydantic 스키마
│   ├── database.py             # DB 연결
│   ├── auth.py                 # JWT 검증
│   └── README.md
│
├── frontend/                   # React + Vite
│   ├── Dockerfile              # 멀티 스테이지 빌드
│   ├── package.json
│   ├── vite.config.js
│   ├── nginx.conf              # 프론트엔드 Nginx 설정
│   ├── index.html
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── api.js              # Axios API 클라이언트
│   │   └── components/
│   │       ├── Login.jsx
│   │       ├── Register.jsx
│   │       └── Memos.jsx
│   └── README.md
│
└── nginx/                      # Nginx 리버스 프록시
    ├── Dockerfile
    ├── nginx.conf              # Nginx 설정
    └── README.md

```

## 빠른 시작

### 사전 요구사항

- Docker 20.10 이상
- Docker Compose 2.0 이상

### 1. 프로젝트 클론

```bash
git clone <repository-url>
cd jwt-docker-demo
```

### 2. 환경변수 확인

`.env` 파일을 확인하고 필요시 수정:

```env
# 데이터베이스
POSTGRES_DB=jwtdemo
POSTGRES_USER=jwtuser
POSTGRES_PASSWORD=jwtpassword123

# JWT 설정 (DRF와 FastAPI가 공유)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-12345
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Django
DJANGO_SECRET_KEY=django-insecure-change-this-in-production-67890
DJANGO_DEBUG=True
```

**⚠️ 주의**: 프로덕션 환경에서는 반드시 시크릿 키를 변경하세요!

### 3. Docker Compose 실행

```bash
# 백그라운드에서 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 4. 서비스 확인

| 서비스 | URL | 설명 |
|--------|-----|------|
| **Frontend** | http://localhost | React 앱 |
| **DRF Admin** | http://localhost:8000/admin | Django 관리자 |
| **DRF API Docs** | http://localhost:8000/api/auth/ | DRF API |
| **FastAPI Docs** | http://localhost:8001/docs | Swagger UI |
| **Nginx** | http://localhost/health | 헬스 체크 |

### 5. 첫 사용자 생성 및 테스트

1. 브라우저에서 `http://localhost` 접속
2. "회원가입" 버튼 클릭
3. 사용자명, 이메일, 비밀번호 입력
4. 자동으로 로그인되며 메모 작성 화면으로 이동
5. 메모 작성, 수정, 삭제 테스트

## API 사용 예시

### 1. 회원가입

```bash
curl -X POST http://localhost/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123!",
    "password2": "testpass123!",
    "email": "test@example.com"
  }'
```

**응답:**
```json
{
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com"
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "message": "회원가입이 완료되었습니다."
}
```

### 2. 로그인

```bash
curl -X POST http://localhost/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123!"
  }'
```

**응답:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. 메모 생성

```bash
# 위에서 받은 access 토큰 사용
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

curl -X POST http://localhost/api/memos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "첫 번째 메모",
    "content": "메모 내용입니다."
  }'
```

### 4. 메모 목록 조회

```bash
curl -X GET http://localhost/api/memos \
  -H "Authorization: Bearer $TOKEN"
```

### 5. 메모 수정

```bash
curl -X PUT http://localhost/api/memos/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "수정된 제목",
    "content": "수정된 내용"
  }'
```

### 6. 메모 삭제

```bash
curl -X DELETE http://localhost/api/memos/1 \
  -H "Authorization: Bearer $TOKEN"
```

## 테스트 시나리오

### 시나리오 1: 기본 흐름

1. ✅ 회원가입
2. ✅ 로그인 (JWT 토큰 받기)
3. ✅ 메모 생성
4. ✅ 메모 목록 조회
5. ✅ 메모 수정
6. ✅ 메모 삭제
7. ✅ 로그아웃

### 시나리오 2: 인증 테스트

1. ✅ 토큰 없이 메모 API 호출 → 401 에러
2. ✅ 잘못된 토큰으로 호출 → 401 에러
3. ✅ 만료된 토큰으로 호출 → 401 에러
4. ✅ 다른 사용자의 메모 접근 → 404 에러

### 시나리오 3: 다중 사용자

1. ✅ 사용자 A 로그인 → 메모 생성
2. ✅ 사용자 B 로그인 → 메모 생성
3. ✅ 사용자 A는 자신의 메모만 조회
4. ✅ 사용자 B는 자신의 메모만 조회

## Docker Compose 명령어

```bash
# 모든 서비스 시작
docker-compose up -d

# 특정 서비스만 시작
docker-compose up -d backend-auth backend-api

# 서비스 중지
docker-compose stop

# 서비스 재시작
docker-compose restart

# 서비스 중지 및 컨테이너 삭제
docker-compose down

# 볼륨까지 삭제 (데이터 초기화)
docker-compose down -v

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend-auth

# 서비스 상태 확인
docker-compose ps

# 컨테이너 내부 접속
docker-compose exec backend-auth bash
docker-compose exec db psql -U jwtuser -d jwtdemo

# 재빌드
docker-compose build
docker-compose up -d --build
```

## 개발 환경 설정

각 서비스별로 독립적인 개발 환경을 구성할 수 있습니다.

### Backend Auth (DRF)

```bash
cd backend-auth
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000
```

상세 내용: [backend-auth/README.md](backend-auth/README.md)

### Backend API (FastAPI)

```bash
cd backend-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

상세 내용: [backend-api/README.md](backend-api/README.md)

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

상세 내용: [frontend/README.md](frontend/README.md)

## EC2 배포 가이드

EC2에서 Docker Compose로 실제 운영 환경을 구축하는 방법은 다음 문서를 참조하세요:

**[nginx/README.md](nginx/README.md)** - 상세한 배포 가이드 포함:
- HTTP/HTTPS 설정
- Let's Encrypt SSL 인증서 발급
- 방화벽 설정
- 보안 설정 (비밀번호, CORS 등)
- 모니터링 및 로그 확인
- 백업 및 복원

## 주요 특징

### 1. JWT 토큰 공유

DRF에서 발급한 JWT 토큰을 FastAPI에서도 검증할 수 있도록 **동일한 시크릿 키**를 사용합니다.

**DRF (config/settings.py)**:
```python
SIMPLE_JWT = {
    'SIGNING_KEY': os.getenv('JWT_SECRET_KEY'),
    'ALGORITHM': os.getenv('JWT_ALGORITHM', 'HS256'),
}
```

**FastAPI (auth.py)**:
```python
payload = jwt.decode(
    token,
    os.getenv('JWT_SECRET_KEY'),
    algorithms=[os.getenv('JWT_ALGORITHM')]
)
```

### 2. FastAPI Lifespan (최신 문법)

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    Base.metadata.create_all(bind=engine)
    yield
    # 종료 시 실행
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)
```

### 3. React 프로덕션 빌드

멀티 스테이지 Dockerfile로 경량 이미지 생성:

```dockerfile
# 빌드 스테이지
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 프로덕션 스테이지
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

### 4. 마이크로서비스 분리

- **인증 서비스**: 사용자 관리 및 JWT 발급에 집중
- **메모 서비스**: 비즈니스 로직에 집중, JWT 검증만 수행
- **확장성**: 각 서비스를 독립적으로 스케일링 가능

### 5. 환경변수 관리

- `.env` 파일로 중앙 관리
- `python-dotenv`로 파이썬에서 로드
- Vite 환경변수 (`VITE_` 접두사)

## 보안 고려사항

### 개발 환경 (현재 설정)

- ✅ JWT 기반 인증
- ✅ 비밀번호 해싱 (Django 기본)
- ⚠️ CORS 모든 origin 허용
- ⚠️ DEBUG 모드 활성화
- ⚠️ 약한 시크릿 키

### 프로덕션 환경에서 필수 변경사항

1. **시크릿 키 변경**
   ```bash
   # 강력한 랜덤 키 생성
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Django 설정**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com']
   CORS_ALLOWED_ORIGINS = ['https://your-domain.com']
   ```

3. **HTTPS 적용**
   - Let's Encrypt SSL 인증서 사용
   - nginx/README.md 참조

4. **데이터베이스 비밀번호 강화**

5. **Rate Limiting 적용**

6. **로그 모니터링**

## 트러블슈팅

### 포트 충돌

```bash
# 사용 중인 포트 확인
sudo lsof -i :80
sudo lsof -i :8000
sudo lsof -i :8001
sudo lsof -i :5432

# 프로세스 종료
sudo kill -9 <PID>
```

### 데이터베이스 연결 실패

```bash
# PostgreSQL 상태 확인
docker-compose ps db

# 로그 확인
docker-compose logs db

# 데이터베이스 재시작
docker-compose restart db
```

### 프론트엔드 빌드 실패

```bash
# 캐시 삭제 후 재빌드
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### JWT 토큰 검증 실패

- DRF와 FastAPI의 `JWT_SECRET_KEY`가 동일한지 확인
- `.env` 파일이 모든 서비스에서 로드되는지 확인
- 토큰 만료 시간 확인

## 성능 최적화

### 데이터베이스

- Connection Pooling 적용 (SQLAlchemy)
- 인덱스 추가 (user_id 등)
- 정기적인 VACUUM 실행

### 백엔드

- Gunicorn/Uvicorn 워커 수 조정
- 비동기 처리 활용 (FastAPI)
- 캐싱 (Redis 추가)

### 프론트엔드

- Code Splitting
- Lazy Loading
- 이미지 최적화
- CDN 사용

### Nginx

- Gzip 압축 (적용됨)
- 정적 파일 캐싱 (적용됨)
- HTTP/2 적용
- Keep-Alive 연결

## 확장 아이디어

- [ ] Redis 캐싱 추가
- [ ] WebSocket 실시간 알림 (Django Channels)
- [ ] 파일 업로드 기능 (S3)
- [ ] 이메일 인증
- [ ] OAuth 로그인 (Google, GitHub)
- [ ] 관리자 대시보드
- [ ] 모바일 앱 (React Native)
- [ ] CI/CD 파이프라인 (GitHub Actions)
- [ ] 모니터링 (Prometheus, Grafana)
- [ ] 로그 수집 (ELK Stack)

## 라이선스

MIT License

## 문의

문제가 발생하거나 질문이 있으시면 Issue를 등록해주세요.

---

**Happy Coding!** 🚀