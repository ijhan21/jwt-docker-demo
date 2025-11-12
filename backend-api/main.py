from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database import engine, Base, get_db
from models import Memo
from schemas import MemoCreate, MemoUpdate, MemoResponse
from auth import get_current_user_id


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 생명주기 관리 (최신 FastAPI 문법)

    시작 시: 데이터베이스 테이블 생성
    종료 시: 필요한 정리 작업 수행
    """
    # 시작 시 실행
    print("🚀 FastAPI 서버 시작 중...")
    print("📊 데이터베이스 테이블 생성 중...")
    Base.metadata.create_all(bind=engine)
    print("✅ 데이터베이스 준비 완료!")

    yield  # 애플리케이션 실행

    # 종료 시 실행
    print("👋 FastAPI 서버 종료 중...")


# FastAPI 앱 생성 (lifespan 적용)
app = FastAPI(
    title="JWT Memo API",
    description="JWT 인증을 사용하는 메모 CRUD API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """루트 엔드포인트"""
    return {
        "message": "JWT Memo API",
        "version": "1.0.0",
        "endpoints": {
            "memos": "/api/memos",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


@app.post("/api/memos", response_model=MemoResponse, status_code=status.HTTP_201_CREATED)
def create_memo(
    memo: MemoCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    새 메모 생성

    - JWT 토큰 필요
    - 제목과 내용 필수
    """
    new_memo = Memo(
        user_id=user_id,
        title=memo.title,
        content=memo.content
    )
    db.add(new_memo)
    db.commit()
    db.refresh(new_memo)

    return new_memo


@app.get("/api/memos", response_model=List[MemoResponse])
def get_memos(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    현재 사용자의 모든 메모 조회

    - JWT 토큰 필요
    - 페이지네이션 지원 (skip, limit)
    """
    memos = db.query(Memo).filter(
        Memo.user_id == user_id
    ).offset(skip).limit(limit).all()

    return memos


@app.get("/api/memos/{memo_id}", response_model=MemoResponse)
def get_memo(
    memo_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    특정 메모 조회

    - JWT 토큰 필요
    - 본인의 메모만 조회 가능
    """
    memo = db.query(Memo).filter(
        Memo.id == memo_id,
        Memo.user_id == user_id
    ).first()

    if not memo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="메모를 찾을 수 없습니다."
        )

    return memo


@app.put("/api/memos/{memo_id}", response_model=MemoResponse)
def update_memo(
    memo_id: int,
    memo_update: MemoUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    메모 수정

    - JWT 토큰 필요
    - 본인의 메모만 수정 가능
    - 제목 또는 내용을 선택적으로 수정
    """
    memo = db.query(Memo).filter(
        Memo.id == memo_id,
        Memo.user_id == user_id
    ).first()

    if not memo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="메모를 찾을 수 없습니다."
        )

    # 수정할 필드만 업데이트
    if memo_update.title is not None:
        memo.title = memo_update.title
    if memo_update.content is not None:
        memo.content = memo_update.content

    db.commit()
    db.refresh(memo)

    return memo


@app.delete("/api/memos/{memo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memo(
    memo_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    메모 삭제

    - JWT 토큰 필요
    - 본인의 메모만 삭제 가능
    """
    memo = db.query(Memo).filter(
        Memo.id == memo_id,
        Memo.user_id == user_id
    ).first()

    if not memo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="메모를 찾을 수 없습니다."
        )

    db.delete(memo)
    db.commit()

    return None
