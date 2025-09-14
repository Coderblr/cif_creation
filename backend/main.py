from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import logging
import json
from typing import Optional, Dict, Any, List
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auth_system.log'),
        logging.StreamHandler()
    ]
)

auth_logger = logging.getLogger('auth_system')
user_action_logger = logging.getLogger('user_actions')
security_logger = logging.getLogger('security')

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

app = FastAPI(title="Authentication System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
users_db: Dict[str, Dict[str, Any]] = {}
login_attempts: List[Dict[str, Any]] = []
user_counter = 1

class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    created_at: str
    last_login: Optional[str]

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_client_ip(request: Request) -> str:
    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"].split(",")[0]
    elif "x-real-ip" in request.headers:
        return request.headers["x-real-ip"]
    else:
        return request.client.host if request.client else "unknown"

def create_user(user_data: UserRegistration) -> int:
    global user_counter

    if user_data.email in users_db:
        auth_logger.warning(f"Attempted to create duplicate user: {user_data.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user_data.password)
    user_id = user_counter
    user_counter += 1

    users_db[user_data.email] = {
        "id": user_id,
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow().isoformat(),
        "last_login": None,
        "is_active": True
    }

    auth_logger.info(f"New user created: {user_data.email} (ID: {user_id})")
    return user_id

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    return users_db.get(email)

def update_last_login(user_id: int):
    for user in users_db.values():
        if user["id"] == user_id:
            user["last_login"] = datetime.utcnow().isoformat()
            break

def log_login_attempt(email: str, ip_address: str, user_agent: str, success: bool):
    attempt = {
        "email": email,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }
    login_attempts.append(attempt)

    # Keep only last 1000 attempts
    if len(login_attempts) > 1000:
        login_attempts.pop(0)

def log_user_action(action: str, user_email: str, ip_address: str, additional_data: Optional[Dict[str, Any]] = None):
    log_data = {
        "action": action,
        "user_email": user_email,
        "ip_address": ip_address,
        "timestamp": datetime.utcnow().isoformat(),
        "additional_data": additional_data or {}
    }
    user_action_logger.info(f"USER_ACTION: {json.dumps(log_data)}")

def log_security_event(event_type: str, details: Dict[str, Any], severity: str = "INFO"):
    log_data = {
        "event_type": event_type,
        "severity": severity,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }
    if severity == "WARNING":
        security_logger.warning(f"SECURITY_EVENT: {json.dumps(log_data)}")
    elif severity == "ERROR":
        security_logger.error(f"SECURITY_EVENT: {json.dumps(log_data)}")
    else:
        security_logger.info(f"SECURITY_EVENT: {json.dumps(log_data)}")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.utcnow()
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "unknown")

    request_data = {
        "method": request.method,
        "url": str(request.url),
        "client_ip": client_ip,
        "user_agent": user_agent,
        "headers": dict(request.headers)
    }
    auth_logger.info(f"REQUEST: {json.dumps(request_data)}")

    response = await call_next(request)

    process_time = (datetime.utcnow() - start_time).total_seconds()
    response_data = {
        "status_code": response.status_code,
        "process_time_seconds": process_time
    }
    auth_logger.info(f"RESPONSE: {json.dumps(response_data)}")

    return response

@app.post("/auth/register", response_model=dict)
async def register_user(user_data: UserRegistration, request: Request):
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "unknown")

    auth_logger.info(f"Registration attempt for email: {user_data.email}")

    if len(user_data.password) < 8:
        log_security_event(
            "WEAK_PASSWORD_ATTEMPT",
            {"email": user_data.email, "ip_address": client_ip},
            "WARNING"
        )
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

    try:
        user_id = create_user(user_data)

        log_user_action(
            "USER_REGISTERED",
            user_data.email,
            client_ip,
            {
                "user_id": user_id,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "user_agent": user_agent
            }
        )

        return {
            "message": "User registered successfully",
            "user_id": user_id
        }
    except Exception as e:
        auth_logger.error(f"Registration failed for {user_data.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/auth/login", response_model=Token)
async def login_user(user_credentials: UserLogin, request: Request):
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "unknown")

    auth_logger.info(f"Login attempt for email: {user_credentials.email}")

    user = get_user_by_email(user_credentials.email)

    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
        log_login_attempt(user_credentials.email, client_ip, user_agent, False)

        log_security_event(
            "FAILED_LOGIN_ATTEMPT",
            {
                "email": user_credentials.email,
                "ip_address": client_ip,
                "user_agent": user_agent
            },
            "WARNING"
        )

        auth_logger.warning(f"Failed login attempt for: {user_credentials.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user["is_active"]:
        log_security_event(
            "INACTIVE_USER_LOGIN_ATTEMPT",
            {"email": user_credentials.email, "ip_address": client_ip},
            "WARNING"
        )
        raise HTTPException(status_code=401, detail="Account is inactive")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": user["id"]},
        expires_delta=access_token_expires
    )

    update_last_login(user["id"])

    log_login_attempt(user_credentials.email, client_ip, user_agent, True)

    log_user_action(
        "USER_LOGIN",
        user_credentials.email,
        client_ip,
        {
            "user_id": user["id"],
            "user_agent": user_agent,
            "token_expires": (datetime.utcnow() + access_token_expires).isoformat()
        }
    )

    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        created_at=user["created_at"],
        last_login=user["last_login"]
    )

    auth_logger.info(f"Successful login for: {user_credentials.email}")

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None or not isinstance(email, str):
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user

@app.get("/auth/profile", response_model=UserResponse)
async def get_user_profile(request: Request, current_user: Dict[str, Any] = Depends(get_current_user)):
    client_ip = get_client_ip(request)

    log_user_action(
        "PROFILE_ACCESS",
        current_user["email"],
        client_ip,
        {"user_id": current_user["id"]}
    )

    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        created_at=current_user["created_at"],
        last_login=current_user["last_login"]
    )

@app.post("/auth/logout")
async def logout_user(request: Request, current_user: Dict[str, Any] = Depends(get_current_user)):
    client_ip = get_client_ip(request)

    log_user_action(
        "USER_LOGOUT",
        current_user["email"],
        client_ip,
        {"user_id": current_user["id"]}
    )

    return {"message": "Successfully logged out"}

@app.get("/auth/stats")
async def get_auth_stats():
    total_users = len(users_db)

    # Count active users (logged in within last 30 days)
    active_users = 0
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    for user in users_db.values():
        if user["last_login"]:
            last_login = datetime.fromisoformat(user["last_login"])
            if last_login > thirty_days_ago:
                active_users += 1

    # Count today's login attempts
    today = datetime.utcnow().date()
    login_attempts_today = len([a for a in login_attempts if datetime.fromisoformat(a["timestamp"]).date() == today])
    successful_logins_today = len([a for a in login_attempts if a["success"] and datetime.fromisoformat(a["timestamp"]).date() == today])
    failed_logins_today = len([a for a in login_attempts if not a["success"] and datetime.fromisoformat(a["timestamp"]).date() == today])

    stats = {
        "total_users": total_users,
        "active_users_30_days": active_users,
        "login_attempts_today": login_attempts_today,
        "successful_logins_today": successful_logins_today,
        "failed_logins_today": failed_logins_today,
        "success_rate_today": (successful_logins_today / login_attempts_today * 100) if login_attempts_today > 0 else 0
    }

    auth_logger.info(f"Auth stats requested: {stats}")
    return stats

@app.get("/auth/recent-activity")
async def get_recent_activity(limit: int = 10):
    # Sort by timestamp descending and take the most recent
    sorted_attempts = sorted(login_attempts, key=lambda x: x["timestamp"], reverse=True)
    activities = sorted_attempts[:limit]

    return {"recent_activities": activities}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {
        "message": "Authentication System API",
        "version": "1.0.0",
        "endpoints": {
            "register": "/auth/register",
            "login": "/auth/login",
            "profile": "/auth/profile",
            "logout": "/auth/logout",
            "stats": "/auth/stats",
            "recent_activity": "/auth/recent-activity",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    auth_logger.info("Starting Authentication System API...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
