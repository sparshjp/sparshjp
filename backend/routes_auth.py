"""Authentication & RBAC module for Kairos ERP."""
from fastapi import APIRouter, HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import os
import uuid
import secrets

router = APIRouter(prefix="/auth")
db = None

JWT_ALGORITHM = "HS256"

# ── ROLE DEFINITIONS ──
ROLES = {
    "creator": {
        "label": "Creator",
        "description": "Platform owner — full access including Kairos AI Engine",
        "level": 100,
    },
    "admin": {
        "label": "Admin",
        "description": "Company administrator — full access except Kairos AI Engine",
        "level": 90,
    },
    "finance_manager": {
        "label": "Finance Manager",
        "description": "Financial Statements, Journal Entries, CoA, Bank Recon, Audit Trail",
        "level": 70,
    },
    "project_manager": {
        "label": "Project Manager",
        "description": "Projects, Timesheets, Resource Allocation, Revenue Recognition",
        "level": 70,
    },
    "hr_manager": {
        "label": "HR Manager",
        "description": "Employees, Payroll, Leave Management",
        "level": 70,
    },
    "ap_clerk": {
        "label": "AP Clerk",
        "description": "Buying, Vendor Bills, Purchase Orders, Payments",
        "level": 50,
    },
    "ar_clerk": {
        "label": "AR Clerk",
        "description": "Selling, Invoices, Customer Receipts, Aging",
        "level": 50,
    },
    "tax_compliance": {
        "label": "Tax & Compliance",
        "description": "GST, TDS, E-Invoice, GSTR-1, GSTR-3B",
        "level": 50,
    },
    "viewer": {
        "label": "Viewer",
        "description": "Read-only access to Dashboard and Reports",
        "level": 10,
    },
}

# ── ROUTE ACCESS MATRIX ──
# Maps sidebar section IDs to allowed roles
SECTION_ACCESS = {
    "core": ["creator", "admin", "finance_manager", "project_manager", "hr_manager", "ap_clerk", "ar_clerk", "tax_compliance", "viewer"],
    "selling": ["creator", "admin", "finance_manager", "ar_clerk"],
    "buying": ["creator", "admin", "finance_manager", "ap_clerk"],
    "stock": ["creator", "admin", "finance_manager", "ap_clerk", "ar_clerk"],
    "hr": ["creator", "admin", "hr_manager"],
    "ai": ["creator"],
    "delivery": ["creator", "admin", "project_manager"],
    "accounting": ["creator", "admin", "finance_manager"],
    "gst": ["creator", "admin", "finance_manager", "tax_compliance"],
    "tds": ["creator", "admin", "finance_manager", "tax_compliance"],
    "reporting-ai": ["creator", "admin", "finance_manager", "project_manager"],
    "reports": ["creator", "admin", "finance_manager", "project_manager", "hr_manager", "viewer"],
    "settings": ["creator", "admin"],
    "user-management": ["creator", "admin"],
    "approvals": ["creator", "admin", "finance_manager", "project_manager", "hr_manager"],
    "budgets": ["creator", "admin", "finance_manager"],
    "contracts": ["creator", "admin", "finance_manager", "project_manager"],
    "resources": ["creator", "admin", "project_manager", "hr_manager"],
    "forex": ["creator", "admin", "finance_manager"],
    "billing": ["creator", "admin", "finance_manager", "project_manager"],
    "doc-mgmt": ["creator", "admin", "finance_manager", "project_manager", "hr_manager", "ap_clerk", "ar_clerk"],
    "notifications": ["creator", "admin", "finance_manager", "project_manager", "hr_manager", "ap_clerk", "ar_clerk", "tax_compliance", "viewer"],
    "compliance": ["creator", "admin"],
    "portal": ["creator", "admin", "project_manager"],
}

# Maps specific route paths to allowed roles (overrides section-level)
ROUTE_ACCESS = {
    "/ai-agents": ["creator"],
    "/admin/tables": ["creator", "admin"],
    "/company-setup": ["creator", "admin"],
    "/settings": ["creator", "admin"],
    "/user-management": ["creator", "admin"],
}


def set_db(database):
    global db
    db = database


def _get_jwt_secret():
    return os.environ["JWT_SECRET"]


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        "type": "access",
    }
    return jwt.encode(payload, _get_jwt_secret(), algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "type": "refresh",
    }
    return jwt.encode(payload, _get_jwt_secret(), algorithm=JWT_ALGORITHM)


async def get_current_user(request: Request) -> dict:
    """Extract and validate user from JWT token (cookie or header)."""
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, _get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"id": payload["sub"]})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        user.pop("_id", None)
        user.pop("password_hash", None)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=86400, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")


def _clear_auth_cookies(response: Response):
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")


# ── BRUTE FORCE PROTECTION ──

async def _check_brute_force(identifier: str):
    attempt = await db.login_attempts.find_one({"identifier": identifier}, {"_id": 0})
    if attempt and attempt.get("count", 0) >= 5:
        locked_until = attempt.get("locked_until")
        if locked_until and datetime.now(timezone.utc) < datetime.fromisoformat(locked_until):
            remaining = (datetime.fromisoformat(locked_until) - datetime.now(timezone.utc)).seconds // 60
            raise HTTPException(status_code=429, detail=f"Account locked. Try again in {remaining + 1} minutes.")
        else:
            await db.login_attempts.delete_one({"identifier": identifier})


async def _record_failed_attempt(identifier: str):
    attempt = await db.login_attempts.find_one({"identifier": identifier})
    if attempt:
        new_count = attempt.get("count", 0) + 1
        update = {"$set": {"count": new_count, "last_attempt": datetime.now(timezone.utc).isoformat()}}
        if new_count >= 5:
            update["$set"]["locked_until"] = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
        await db.login_attempts.update_one({"identifier": identifier}, update)
    else:
        await db.login_attempts.insert_one({
            "identifier": identifier,
            "count": 1,
            "last_attempt": datetime.now(timezone.utc).isoformat(),
        })


async def _clear_attempts(identifier: str):
    await db.login_attempts.delete_many({"identifier": identifier})


# ── ENDPOINTS ──

@router.post("/login")
async def login(body: dict, request: Request, response: Response):
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    client_ip = request.client.host if request.client else "unknown"
    identifier = f"{client_ip}:{email}"
    await _check_brute_force(identifier)

    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user or not verify_password(password, user.get("password_hash", "")):
        await _record_failed_attempt(identifier)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    await _clear_attempts(identifier)

    access_token = create_access_token(user["id"], email)
    refresh_token = create_refresh_token(user["id"])
    _set_auth_cookies(response, access_token, refresh_token)

    safe_user = {k: v for k, v in user.items() if k != "password_hash"}
    return {"token": access_token, "user": safe_user}


@router.post("/register")
async def register(body: dict, response: Response):
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")
    name = body.get("name", "").strip()
    role = body.get("role", "viewer")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if role not in ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role: {role}")
    if role in ["creator"]:
        raise HTTPException(status_code=403, detail="Cannot self-register as creator")

    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": name or email.split("@")[0],
        "password_hash": hash_password(password),
        "role": role,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.users.insert_one(user)

    access_token = create_access_token(user["id"], email)
    refresh_token = create_refresh_token(user["id"])
    _set_auth_cookies(response, access_token, refresh_token)

    safe_user = {k: v for k, v in user.items() if k not in ("password_hash", "_id")}
    return {"token": access_token, "user": safe_user}


@router.get("/me")
async def get_me(request: Request):
    user = await get_current_user(request)
    return user


@router.post("/logout")
async def logout(response: Response):
    _clear_auth_cookies(response)
    return {"status": "ok"}


@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        payload = jwt.decode(token, _get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        access_token = create_access_token(user["id"], user["email"])
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=86400, path="/")
        return {"token": access_token}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.get("/roles")
async def get_roles():
    return {"roles": ROLES, "section_access": SECTION_ACCESS}


@router.post("/forgot-password")
async def forgot_password(body: dict):
    email = body.get("email", "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        return {"status": "ok", "message": "If the email exists, a reset link has been sent."}
    token = secrets.token_urlsafe(32)
    await db.password_reset_tokens.insert_one({
        "token": token,
        "user_id": user["id"],
        "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
        "used": False,
    })
    frontend_url = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:3000")
    print(f"[PASSWORD RESET] {email} → {frontend_url}/reset-password?token={token}")
    return {"status": "ok", "message": "If the email exists, a reset link has been sent."}


@router.post("/reset-password")
async def reset_password(body: dict):
    token = body.get("token", "")
    new_password = body.get("password", "")
    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Token and new password required")
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    record = await db.password_reset_tokens.find_one({"token": token, "used": False}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    if datetime.now(timezone.utc) > record.get("expires_at", datetime.min.replace(tzinfo=timezone.utc)):
        raise HTTPException(status_code=400, detail="Reset token expired")
    await db.users.update_one({"id": record["user_id"]}, {"$set": {"password_hash": hash_password(new_password)}})
    await db.password_reset_tokens.update_one({"token": token}, {"$set": {"used": True}})
    return {"status": "ok", "message": "Password reset successfully"}


# ── USER MANAGEMENT (Admin/Creator only) ──

@router.get("/users")
async def list_users(request: Request):
    current = await get_current_user(request)
    if current["role"] not in ["creator", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).to_list(500)
    return users


@router.post("/users")
async def create_user(body: dict, request: Request):
    current = await get_current_user(request)
    if current["role"] not in ["creator", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")
    name = body.get("name", "").strip()
    role = body.get("role", "viewer")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    if role not in ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role: {role}")
    if role == "creator" and current["role"] != "creator":
        raise HTTPException(status_code=403, detail="Only creator can assign creator role")
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")
    user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": name or email.split("@")[0],
        "password_hash": hash_password(password),
        "role": role,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.users.insert_one(user)
    user.pop("_id", None)
    user.pop("password_hash", None)
    return user


@router.put("/users/{user_id}")
async def update_user(user_id: str, body: dict, request: Request):
    current = await get_current_user(request)
    if current["role"] not in ["creator", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    target = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target["role"] == "creator" and current["role"] != "creator":
        raise HTTPException(status_code=403, detail="Cannot modify creator account")
    update = {}
    if "name" in body:
        update["name"] = body["name"]
    if "role" in body:
        if body["role"] not in ROLES:
            raise HTTPException(status_code=400, detail=f"Invalid role: {body['role']}")
        if body["role"] == "creator" and current["role"] != "creator":
            raise HTTPException(status_code=403, detail="Only creator can assign creator role")
        update["role"] = body["role"]
    if "is_active" in body:
        update["is_active"] = body["is_active"]
    if "password" in body and body["password"]:
        update["password_hash"] = hash_password(body["password"])
    if update:
        await db.users.update_one({"id": user_id}, {"$set": update})
    updated = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    return updated


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, request: Request):
    current = await get_current_user(request)
    if current["role"] not in ["creator", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    target = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target["role"] == "creator":
        raise HTTPException(status_code=403, detail="Cannot delete creator account")
    await db.users.delete_one({"id": user_id})
    return {"status": "ok", "deleted": user_id}


# ── SEEDING ──

async def seed_users():
    """Seed creator account and create indexes."""
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id", unique=True)
    await db.login_attempts.create_index("identifier")

    creator_email = os.environ.get("ADMIN_EMAIL", "kairoserp").strip().lower()
    creator_password = os.environ.get("ADMIN_PASSWORD", "¢re@tor@AIengine")

    existing = await db.users.find_one({"email": creator_email})
    if existing is None:
        await db.users.insert_one({
            "id": str(uuid.uuid4()),
            "email": creator_email,
            "name": "Kairos Creator",
            "password_hash": hash_password(creator_password),
            "role": "creator",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        print(f"[AUTH] Seeded creator account: {creator_email}")
    elif not verify_password(creator_password, existing.get("password_hash", "")):
        await db.users.update_one(
            {"email": creator_email},
            {"$set": {"password_hash": hash_password(creator_password)}}
        )
        print(f"[AUTH] Updated creator password for: {creator_email}")
    else:
        print(f"[AUTH] Creator account exists: {creator_email}")
