"""
Modelos Pydantic para usuários
"""

from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    home_dir: Optional[str] = None
    share_path: Optional[str] = None
    browseable: str = "yes"
    writable: str = "yes"
    guest_ok: str = "no"
    create_mask: str = "0660"
    directory_mask: str = "0770"


class UserUpdate(BaseModel):
    password: Optional[str] = None
    share_path: Optional[str] = None
    browseable: Optional[str] = None
    writable: Optional[str] = None
    guest_ok: Optional[str] = None
    create_mask: Optional[str] = None
    directory_mask: Optional[str] = None


class UserResponse(BaseModel):
    username: str
    has_share: bool
    share_path: str
    share_config: Optional[dict] = None 