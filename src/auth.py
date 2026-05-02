from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Header, HTTPException


@dataclass
class CurrentUser:
    id: str
    github_login: str
    token: str


def generate_service_token(secret: str, subject: str = "service:api-gateway") -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": subject,
            "typ": "service",
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        secret,
        algorithm="HS256",
    )


def _decode_bearer(authorization: str, secret: str) -> tuple[str, dict]:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    token = authorization.removeprefix("Bearer ")
    try:
        return token, jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=str(e))


def get_current_user(authorization: str = Header(...)) -> CurrentUser:
    from src.main import settings

    token, claims = _decode_bearer(authorization, settings.auth.jwt_secret)
    if str(claims.get("sub", "")).startswith("service:"):
        raise HTTPException(status_code=403, detail="User token required")
    return CurrentUser(id=claims["sub"], github_login=claims.get("github_login", ""), token=token)


def require_service(authorization: str = Header(...)) -> str:
    from src.main import settings

    token, claims = _decode_bearer(authorization, settings.auth.jwt_secret)
    if claims.get("typ") != "service" and not str(claims.get("sub", "")).startswith("service:"):
        raise HTTPException(status_code=403, detail="Service token required")
    return token
