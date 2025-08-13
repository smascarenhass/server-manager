"""
Modelos Pydantic para shares
"""

from pydantic import BaseModel


class ShareConfig(BaseModel):
    path: str
    valid_users: str
    read_only: str
    browseable: str
    create_mask: str
    directory_mask: str 