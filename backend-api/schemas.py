from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MemoCreate(BaseModel):
    """메모 생성 스키마"""
    title: str = Field(..., min_length=1, max_length=200, description="메모 제목")
    content: str = Field(..., min_length=1, description="메모 내용")


class MemoUpdate(BaseModel):
    """메모 수정 스키마"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="메모 제목")
    content: Optional[str] = Field(None, min_length=1, description="메모 내용")


class MemoResponse(BaseModel):
    """메모 응답 스키마"""
    id: int
    user_id: int
    title: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
