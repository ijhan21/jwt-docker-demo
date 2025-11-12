# Backend API (FastAPI)

JWT 인증 기반 메모 CRUD를 제공하는 FastAPI 백엔드입니다.

## 기능

- JWT 토큰 검증 (DRF에서 발급한 토큰 사용)
- 메모 CRUD (생성, 조회, 수정, 삭제)
- 사용자별 메모 분리
- 페이지네이션 지원

## 기술 스택

- FastAPI (최신 lifespan 문법 적용)
- SQLAlchemy 2.0
- PostgreSQL
- PyJWT
- python-dotenv
- Pydantic v2

## API 엔드포인트

모든 엔드포인트는 `Authorization: Bearer <token>` 헤더가 필요합니다.

### 1. 메모 생성
```
POST /api/memos
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "title": "첫 번째 메모",
  "content": "메모 내용입니다."
}
```

**응답:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "첫 번째 메모",
  "content": "메모 내용입니다.",
  "created_at": "2024-01-01T12:00:00+09:00",
  "updated_at": null
}
```

### 2. 메모 목록 조회
```
GET /api/memos?skip=0&limit=10
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**응답:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "첫 번째 메모",
    "content": "메모 내용입니다.",
    "created_at": "2024-01-01T12:00:00+09:00",
    "updated_at": null
  }
]
```

### 3. 특정 메모 조회
```
GET /api/memos/{memo_id}
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### 4. 메모 수정
```
PUT /api/memos/{memo_id}
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "title": "수정된 제목",
  "content": "수정된 내용"
}
```

### 5. 메모 삭제
```
DELETE /api/memos/{memo_id}
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
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
JWT_SECRET_KEY=your-secret-key  # DRF와 동일한 키 사용!
JWT_ALGORITHM=HS256
```

### 4. 개발 서버 실행
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

서버가 `http://localhost:8001`에서 실행됩니다.

### 5. API 문서 확인
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Docker로 실행

루트 디렉토리에서:
```bash
docker-compose up backend-api
```

## 프로젝트 구조

```
backend-api/
├── main.py          # FastAPI 앱 (lifespan, 라우트)
├── models.py        # SQLAlchemy 모델
├── schemas.py       # Pydantic 스키마
├── database.py      # DB 연결 설정
├── auth.py          # JWT 검증 로직
├── requirements.txt # Python 의존성
├── Dockerfile       # Docker 이미지 설정
└── README.md        # 이 파일
```

## 주요 특징

### 1. Lifespan 이벤트 (최신 문법)
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    Base.metadata.create_all(bind=engine)
    yield
    # 종료 시 실행
    print("Shutting down...")
```

### 2. JWT 검증
- DRF에서 발급한 JWT 토큰을 검증
- `JWT_SECRET_KEY`와 `JWT_ALGORITHM`이 DRF와 동일해야 함
- Bearer 토큰 스키마 사용

### 3. 의존성 주입
```python
def create_memo(
    memo: MemoCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # user_id는 JWT에서 자동 추출
    # db는 자동으로 세션 생성/종료
    ...
```

### 4. Pydantic v2 스키마
- 타입 안정성
- 자동 검증
- API 문서 자동 생성

## JWT 토큰 사용 방법

1. DRF 백엔드에서 로그인하여 토큰 받기:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123!"}'
```

2. 받은 `access` 토큰을 FastAPI에서 사용:
```bash
curl -X POST http://localhost:8001/api/memos \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "메모", "content": "내용"}'
```

## 주의사항

1. **JWT Secret Key**: DRF와 FastAPI가 같은 `JWT_SECRET_KEY`를 사용해야 합니다.

2. **CORS**: 프로덕션에서는 `allow_origins`를 특정 도메인으로 제한하세요.

3. **데이터베이스**: PostgreSQL이 실행 중이어야 합니다.

4. **User ID**: FastAPI는 별도의 User 테이블을 가지지 않고, DRF의 User ID만 참조합니다.

## 테스트 시나리오

1. DRF에서 회원가입/로그인
2. access 토큰 복사
3. FastAPI의 `/docs`에서 "Authorize" 버튼 클릭
4. `Bearer <token>` 형식으로 입력
5. 메모 CRUD 테스트
