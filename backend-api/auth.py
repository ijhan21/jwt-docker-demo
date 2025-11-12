import os
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# JWT 설정
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

# Bearer 토큰 스키마
security = HTTPBearer()


def verify_jwt(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    JWT 토큰을 검증하고 사용자 정보를 반환합니다.

    Args:
        credentials: HTTP Authorization 헤더의 Bearer 토큰

    Returns:
        dict: 디코딩된 토큰 페이로드 (user_id 포함)

    Raises:
        HTTPException: 토큰이 유효하지 않은 경우
    """
    token = credentials.credentials

    try:
        # JWT 토큰 디코딩
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="토큰이 만료되었습니다."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="유효하지 않은 토큰입니다."
        )


def get_current_user_id(payload: dict = Security(verify_jwt)) -> int:
    """
    JWT 페이로드에서 사용자 ID를 추출합니다.

    Args:
        payload: verify_jwt에서 반환된 페이로드

    Returns:
        int: 사용자 ID

    Raises:
        HTTPException: user_id가 페이로드에 없는 경우
    """
    user_id = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="토큰에 사용자 정보가 없습니다."
        )

    return user_id
