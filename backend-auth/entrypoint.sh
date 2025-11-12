#!/bin/bash

# 데이터베이스가 준비될 때까지 대기
echo "Waiting for PostgreSQL..."
while ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do
  sleep 1
done
echo "PostgreSQL is ready!"

# 마이그레이션 실행
python manage.py makemigrations
python manage.py migrate

# 서버 시작
exec python manage.py runserver 0.0.0.0:8000
