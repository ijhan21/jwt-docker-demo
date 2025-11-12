from sqlalchemy import Column, Integer, String, Text, DateTime, func
from database import Base


class Memo(Base):
    """메모 모델"""
    __tablename__ = "memos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # DRF User ID
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Memo(id={self.id}, title={self.title}, user_id={self.user_id})>"
