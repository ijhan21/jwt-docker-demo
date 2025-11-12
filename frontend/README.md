# Frontend (React + Vite)

JWT 인증과 메모 관리 기능을 제공하는 React 프론트엔드입니다.

## 기능

- 회원가입 / 로그인
- JWT 토큰 기반 인증
- 메모 CRUD (생성, 조회, 수정, 삭제)
- 자동 토큰 관리
- 반응형 UI

## 기술 스택

- React 18
- Vite (빌드 도구)
- Axios (HTTP 클라이언트)
- CSS (순수 CSS, 심플한 스타일링)

## 프로젝트 구조

```
frontend/
├── src/
│   ├── main.jsx           # 앱 진입점
│   ├── App.jsx            # 메인 앱 컴포넌트
│   ├── App.css            # 전역 스타일
│   ├── api.js             # API 호출 함수
│   └── components/
│       ├── Login.jsx      # 로그인 컴포넌트
│       ├── Register.jsx   # 회원가입 컴포넌트
│       └── Memos.jsx      # 메모 CRUD 컴포넌트
├── index.html             # HTML 템플릿
├── vite.config.js         # Vite 설정
├── package.json           # 의존성 관리
├── Dockerfile             # 프로덕션 Docker 이미지
├── nginx.conf             # Nginx 설정
└── README.md              # 이 파일
```

## 로컬 개발 환경 설정

### 1. 의존성 설치
```bash
npm install
```

### 2. 환경변수 설정
`.env` 파일을 생성하고 다음 내용을 추가:
```
VITE_API_AUTH_URL=http://localhost:8000/api/auth
VITE_API_MEMOS_URL=http://localhost:8001/api/memos
```

### 3. 개발 서버 실행
```bash
npm run dev
```

개발 서버가 `http://localhost:5173`에서 실행됩니다.

### 4. 프로덕션 빌드
```bash
npm run build
```

빌드된 파일은 `dist/` 폴더에 생성됩니다.

### 5. 프로덕션 빌드 미리보기
```bash
npm run preview
```

## Docker로 실행

### 프로덕션 빌드 (멀티 스테이지)
```bash
docker build -t jwt-frontend .
docker run -p 3000:80 jwt-frontend
```

`http://localhost:3000`에서 접속 가능합니다.

### Docker Compose로 실행
루트 디렉토리에서:
```bash
docker-compose up frontend
```

## 주요 기능 설명

### 1. API 클라이언트 (src/api.js)

```javascript
import axios from 'axios';

// Axios 인스턴스 생성
const memosApi = axios.create({
  baseURL: MEMOS_API_URL,
});

// 요청 인터셉터: JWT 토큰 자동 추가
memosApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 응답 인터셉터: 401 에러 시 로그아웃
memosApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('accessToken');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);
```

### 2. 인증 플로우

1. **로그인/회원가입**
   - 사용자 인증 정보 입력
   - DRF 백엔드로 요청
   - JWT 토큰을 `localStorage`에 저장

2. **인증된 요청**
   - Axios 인터셉터가 자동으로 `Authorization` 헤더 추가
   - FastAPI 백엔드로 메모 CRUD 요청

3. **로그아웃**
   - `localStorage`에서 토큰 제거
   - 로그인 화면으로 이동

### 3. 컴포넌트 구조

```
App
├── Login (비인증)
├── Register (비인증)
└── Memos (인증 필요)
    ├── 메모 작성 폼
    └── 메모 목록
        └── 메모 아이템 (수정/삭제)
```

## Vite 프록시 설정 (개발 모드)

`vite.config.js`:
```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api/auth': {
        target: 'http://backend-auth:8000',
        changeOrigin: true,
      },
      '/api/memos': {
        target: 'http://backend-api:8001',
        changeOrigin: true,
      },
    },
  },
})
```

개발 모드에서 CORS 문제를 해결하기 위한 프록시 설정입니다.

## 프로덕션 배포

### Dockerfile 멀티 스테이지 빌드

1. **빌드 스테이지**: Node.js로 React 앱 빌드
2. **프로덕션 스테이지**: Nginx로 정적 파일 서빙

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
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx 설정

- React Router를 위한 fallback 설정
- 정적 파일 캐싱
- Gzip 압축

## Nginx 리버스 프록시 구성 (EC2)

EC2에서 메인 Nginx를 통해 프론트엔드와 백엔드를 연결하는 예시:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 프론트엔드 (React)
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # DRF 인증 API
    location /api/auth/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # FastAPI 메모 API
    location /api/memos/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**주의**: 프로덕션 환경에서는 `.env` 파일의 URL을 실제 도메인으로 변경하세요!

```
VITE_API_AUTH_URL=https://your-domain.com/api/auth
VITE_API_MEMOS_URL=https://your-domain.com/api/memos
```

## 환경변수

Vite는 `VITE_` 접두사가 붙은 환경변수만 클라이언트에 노출합니다.

- `VITE_API_AUTH_URL`: DRF 인증 API URL
- `VITE_API_MEMOS_URL`: FastAPI 메모 API URL

## 주의사항

1. **빌드 전 환경변수 설정**
   - `.env` 파일의 URL을 프로덕션 환경에 맞게 수정
   - 빌드 시점에 환경변수가 코드에 하드코딩됨

2. **CORS 설정**
   - 개발 모드: Vite 프록시 사용
   - 프로덕션: 백엔드의 CORS 설정 또는 Nginx 리버스 프록시 사용

3. **토큰 보안**
   - `localStorage`에 JWT 저장
   - XSS 공격 방지를 위한 추가 보안 조치 권장

## 사용 방법

1. 회원가입 또는 로그인
2. 메모 작성 (제목, 내용 입력)
3. 메모 목록 확인
4. 메모 수정/삭제
5. 로그아웃

## 트러블슈팅

### CORS 에러
- 백엔드 CORS 설정 확인
- 개발 모드에서는 Vite 프록시 확인
- 프로덕션에서는 Nginx 설정 확인

### 401 Unauthorized
- 토큰이 만료되었거나 유효하지 않음
- 다시 로그인 필요

### 연결 오류
- 백엔드 서버 실행 확인
- 환경변수 URL 확인
