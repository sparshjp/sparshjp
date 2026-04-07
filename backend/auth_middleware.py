"""Authentication middleware for Kairos ERP"""
from fastapi import HTTPException, Request
import jwt
import os
from typing import Optional, List

ADMIN_ONLY_TOOLS = [
    "write_file", "create_file", "patch_file", "insert_lines", "delete_lines",
    "restart_service", "run_command", "install_package", "scaffold_module",
    "create_page", "run_tests"
]

READ_ONLY_TOOLS = [
    "read_file", "list_files", "grep_search", "get_schema", "check_logs",
    "run_query", "test_api", "web_search", "take_screenshot"
]

async def verify_token(authorization: Optional[str]) -> dict:
    """Verify JWT token and return user payload"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(
            token, 
            os.environ.get("JWT_SECRET", "kairos-secret-key"), 
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def check_tool_permission(user_role: str, tool_name: str) -> bool:
    """Check if user has permission to execute a tool"""
    if user_role == "admin":
        return True
    
    if tool_name in READ_ONLY_TOOLS:
        return True
    
    if tool_name in ADMIN_ONLY_TOOLS:
        return False
    
    # Allow other tools for regular users (like verify_deployment)
    return True

async def require_auth(request: Request, db) -> dict:
    """Middleware to require authentication"""
    auth_header = request.headers.get("Authorization")
    payload = await verify_token(auth_header)
    
    # Fetch full user from database
    user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.get("is_active"):
        raise HTTPException(status_code=403, detail="Account disabled")
    
    return user

async def require_admin(request: Request, db) -> dict:
    """Middleware to require admin role"""
    user = await require_auth(request, db)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
