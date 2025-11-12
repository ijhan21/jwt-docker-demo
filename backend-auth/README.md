# Backend Auth (Django REST Framework)

JWT 인증을 담당하는 Django REST Framework 백엔드입니다.

## 기능

- 회원가입 (username, password, email)
- 로그인 (JWT 토큰 발급)
- 토큰 갱신
- 사용자 정보 조회

## 기술 스택

- Django 4.2
- Django REST Framework
- djangorestframework-simplejwt
- PostgreSQL
- python-dotenv

## API 엔드포인트

### 1. 회원가입
```
POST /api/auth/register/
Content-Type: application/json

{
  "username": "testuser",
  "password": "testpass123!",
  "password2": "testpass123!",
  "email": "test@example.com"
}
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
```
POST /api/auth/login/
Content-Type: application/json

{
  "username": "testuser",
  "password": "testpass123!"
}
```

**응답:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. 토큰 갱신
```
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**응답:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 4. 사용자 정보 조회
```
GET /api/auth/me/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**응답:**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com"
}
```

## 로컬 개발 환경 설정

### 1. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정
루트 디렉토리의 `.env` 파일을 참조하거나, 다음 변수들을 설정하세요:
```
POSTGRES_DB=jwtdemo
POSTGRES_USER=jwtuser
POSTGRES_PASSWORD=jwtpassword123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
JWT_SECRET_KEY=your-secret-key
DJANGO_SECRET_KEY=your-django-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

### 4. 데이터베이스 마이그레이션
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 개발 서버 실행
```bash
python manage.py runserver 0.0.0.0:8000
```

서버가 `http://localhost:8000`에서 실행됩니다.

## Docker로 실행

루트 디렉토리에서:
```bash
docker-compose up backend-auth
```

## 프로젝트 구조

```
backend-auth/
├── config/              # Django 설정
│   ├── settings.py      # 프로젝트 설정 (DB, JWT 등)
│   ├── urls.py          # 메인 URL 라우팅
│   └── wsgi.py          # WSGI 설정
├── authentication/      # 인증 앱
│   ├── models.py        # 데이터 모델
│   ├── serializers.py   # DRF 시리얼라이저
│   ├── views.py         # API 뷰
│   └── urls.py          # 인증 URL 라우팅
├── manage.py            # Django 관리 스크립트
├── requirements.txt     # Python 의존성
├── Dockerfile           # Docker 이미지 설정
└── entrypoint.sh        # 컨테이너 시작 스크립트
```

## JWT 토큰 정보

- **알고리즘**: HS256
- **액세스 토큰 유효기간**: 60분 (환경변수로 설정 가능)
- **리프레시 토큰 유효기간**: 1일
- **헤더 형식**: `Authorization: Bearer <token>`

## 주의사항

1. **프로덕션 환경에서는 반드시 다음을 변경하세요:**
   - `JWT_SECRET_KEY`: 강력한 시크릿 키로 변경
   - `DJANGO_SECRET_KEY`: 강력한 시크릿 키로 변경
   - `DJANGO_DEBUG=False`: 디버그 모드 비활성화
   - CORS 설정: 특정 도메인만 허용하도록 변경

2. **FastAPI와 JWT 공유:**
   - FastAPI에서도 같은 `JWT_SECRET_KEY`와 `JWT_ALGORITHM`을 사용해야 토큰 검증이 가능합니다.

3. **데이터베이스:**
   - PostgreSQL이 실행 중이어야 합니다.
   - Docker Compose를 사용하면 자동으로 설정됩니다.
