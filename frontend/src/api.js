import axios from 'axios';

// API 기본 URL 설정
// 개발: Vite 프록시 사용 (/api/auth, /api/memos)
// 프로덕션: 환경변수 또는 절대 경로
const AUTH_API_URL = import.meta.env.VITE_API_AUTH_URL || '/api/auth';
const MEMOS_API_URL = import.meta.env.VITE_API_MEMOS_URL || '/api/memos';

// Axios 인스턴스 생성
const authApi = axios.create({
  baseURL: AUTH_API_URL,
});

const memosApi = axios.create({
  baseURL: MEMOS_API_URL,
});

// 요청 인터셉터: 토큰을 헤더에 자동 추가
memosApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터: 401 에러 시 로그아웃 처리
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

// 인증 API
export const register = async (username, password, email) => {
  const response = await authApi.post('/register/', {
    username,
    password,
    password2: password,
    email,
  });
  return response.data;
};

export const login = async (username, password) => {
  const response = await authApi.post('/login/', {
    username,
    password,
  });
  return response.data;
};

export const getUserInfo = async (token) => {
  const response = await authApi.get('/me/', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};

// 메모 API
export const getMemos = async () => {
  const response = await memosApi.get('/');
  return response.data;
};

export const getMemo = async (id) => {
  const response = await memosApi.get(`/${id}`);
  return response.data;
};

export const createMemo = async (title, content) => {
  const response = await memosApi.post('/', { title, content });
  return response.data;
};

export const updateMemo = async (id, title, content) => {
  const response = await memosApi.put(`/${id}`, { title, content });
  return response.data;
};

export const deleteMemo = async (id) => {
  const response = await memosApi.delete(`/${id}`);
  return response.data;
};
