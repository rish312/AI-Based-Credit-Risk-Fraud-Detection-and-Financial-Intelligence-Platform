import time
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from backend.database import get_connection
import uuid
from backend import config

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract basic info
        method = request.method
        url = str(request.url)
        endpoint = request.url.path
        client_ip = request.client.host if request.client else None
        
        # Read request body
        request_body = b""
        if method in ["POST", "PUT", "PATCH"]:
            request_body = await request.body()
            
            # Reset the request body so endpoints can read it
            async def receive():
                return {"type": "http.request", "body": request_body}
            request._receive = receive
        
        # Get response
        try:
            response = await call_next(request)
            
            # Read response body for logging
            response_body = b""
            if hasattr(response, "body_iterator"):
                body_chunks = []
                async for chunk in response.body_iterator:
                    body_chunks.append(chunk)
                response_body = b"".join(body_chunks)
                
                # Re-create the iterator
                async def new_body_iterator():
                    for chunk in body_chunks:
                        yield chunk
                response.body_iterator = new_body_iterator()
            
            status_code = response.status_code
        except Exception as e:
            response = Response(content="Internal Server Error", status_code=500)
            response_body = b"Internal Server Error"
            status_code = 500
            raise e
        finally:
            duration_ms = (time.time() - start_time) * 1000
            
            # Extract user info if possible
            user_id = None
            username = None
            # Here we might decode JWT manually or get from request state if set by another middleware
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                try:
                    import jwt
                    token = auth_header.split(" ")[1]
                    payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM], options={"verify_exp": False})
                    user_id = payload.get("sub")
                    username = payload.get("username")
                except:
                    pass
            
            # Truncate response_body if > 10KB
            resp_str = response_body.decode('utf-8', errors='ignore')
            if len(resp_str) > 10240:
                resp_str = resp_str[:10240] + "... [truncated]"
            
            req_str = request_body.decode('utf-8', errors='ignore')
            
            # Log to DB
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    '''INSERT INTO audit_logs 
                       (user_id, username, endpoint, method, request_body, response_body, status_code, duration_ms, ip_address)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (user_id, username, endpoint, method, req_str, resp_str, status_code, duration_ms, client_ip)
                )
                conn.commit()
                conn.close()
            except Exception as db_err:
                # print(f"Error logging to audit table: {db_err}")
                pass
                
        return response
