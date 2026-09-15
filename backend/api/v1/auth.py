from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from backend.api.schemas import LoginRequest, LoginResponse, UserResponse
from backend.api.middleware.auth import (
    verify_password, create_access_token, create_refresh_token, 
    get_current_user, require_role, hash_password
)
from backend.database import get_connection

router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash, role FROM users WHERE username = ?", (request.username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or not verify_password(request.password, row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = str(row["id"])
    role = row["role"]
    access_token = create_access_token(user_id=user_id, username=request.username, role=role)
    refresh_token = create_refresh_token(user_id=user_id)
    
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest, current_user: dict = Depends(require_role("admin"))):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (request.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already registered")
        
    hashed_pwd = hash_password(request.password)
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (request.username, hashed_pwd, request.role)
        )
        conn.commit()
        user_id = str(cursor.lastrowid)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        conn.close()
        
    return UserResponse(id=user_id, username=request.username, role=request.role)

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["sub"],
        username=current_user["username"],
        role=current_user["role"]
    )

@router.post("/refresh", response_model=LoginResponse)
def refresh_token(request: RefreshRequest):
    from backend.api.middleware.auth import verify_token
    try:
        payload = verify_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        
        user_id = payload.get("sub")
        
        # We need username and role to create a new access token
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
            
        access_token = create_access_token(user_id=user_id, username=row["username"], role=row["role"])
        new_refresh = create_refresh_token(user_id=user_id)
        
        return LoginResponse(access_token=access_token, refresh_token=new_refresh)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
