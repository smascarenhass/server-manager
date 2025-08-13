"""
Modelos Pydantic para respostas da API
"""

from typing import Optional
from pydantic import BaseModel


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None 