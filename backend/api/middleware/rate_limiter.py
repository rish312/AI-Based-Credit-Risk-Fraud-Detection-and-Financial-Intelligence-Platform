from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi import Request
from backend import config

def rate_limit_key(request: Request):
    # Try to extract user from token if available, else fallback to IP
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            import jwt
            payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
            return payload.get("sub", get_remote_address(request))
        except:
            pass
    return get_remote_address(request)

limiter = Limiter(key_func=rate_limit_key, default_limits=["100/minute"])
