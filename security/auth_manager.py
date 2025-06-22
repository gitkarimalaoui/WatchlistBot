import json
import os
from functools import wraps
from typing import Callable, Iterable, Optional, Tuple
from datetime import datetime

try:
    import streamlit as st
except Exception:  # pragma: no cover - streamlit optional
    st = None  # type: ignore

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")
LOG_FILE = os.path.join(os.path.dirname(__file__), "journal_connexions.csv")

DEFAULT_USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "trader": {"password": "trader123", "role": "trader"},
    "viewer": {"password": "viewer123", "role": "viewer"},
    "debug": {"password": "debug123", "role": "ia_debug"},
}

def _load_users() -> dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_USERS

def _log_connection(username: str, success: bool, log_file: str = LOG_FILE) -> None:
    header = not os.path.exists(log_file)
    with open(log_file, "a", encoding="utf-8") as f:
        if header:
            f.write("user,timestamp,success\n")
        ts = datetime.utcnow().isoformat()
        f.write(f"{username},{ts},{int(success)}\n")

def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[str]]:
    """Check credentials and return ``(success, role)``."""
    users = _load_users()
    user = users.get(username)
    success = bool(user and user.get("password") == password)
    role = user.get("role") if success else None
    _log_connection(username, success)
    return success, role

def require_role(roles: Iterable[str]) -> Callable[[Callable[..., any]], Callable[..., any]]:
    """Decorator to restrict access based on the current user role."""

    def decorator(func: Callable[..., any]) -> Callable[..., any]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            role = kwargs.pop("user_role", None)
            if role is None and st is not None:
                role = st.session_state.get("user_role")
            if role not in roles:
                if st is not None:
                    st.error("Acc\u00e8s refus\u00e9")
                    return None
                raise PermissionError("Unauthorized")
            return func(*args, **kwargs)

        return wrapper

    return decorator

def generate_jwt_token(username: str) -> str:
    """Placeholder for future JWT integration."""
    raise NotImplementedError("JWT token generation not implemented yet")
