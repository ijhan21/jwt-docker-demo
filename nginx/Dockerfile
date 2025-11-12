FROM nginx:alpine

# envsubst를 위한 패키지 설치 (이미 포함되어 있음)
# nginx:alpine에는 envsubst가 포함되어 있음

# nginx 템플릿 복사
COPY nginx.conf.template /etc/nginx/nginx.conf.template

# 환경변수를 치환하여 실제 설정 파일 생성 후 nginx 실행
# 기본값 설정 (환경변수가 없을 경우 대비)
ENV BACKEND_AUTH_HOST=backend-auth \
    BACKEND_AUTH_INTERNAL_PORT=8000 \
    BACKEND_API_HOST=backend-api \
    BACKEND_API_INTERNAL_PORT=8001 \
    FRONTEND_HOST=frontend \
    FRONTEND_INTERNAL_PORT=80

EXPOSE 80 443

# envsubst로 템플릿 치환 후 nginx 실행
CMD ["/bin/sh", "-c", "envsubst '${BACKEND_AUTH_HOST} ${BACKEND_AUTH_INTERNAL_PORT} ${BACKEND_API_HOST} ${BACKEND_API_INTERNAL_PORT} ${FRONTEND_HOST} ${FRONTEND_INTERNAL_PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && nginx -g 'daemon off;'"]
