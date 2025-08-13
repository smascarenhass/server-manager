"""
Roteadores da API Samba Manager
"""

from .basic_routes import router as basic_router
from .user_routes import router as user_router
from .share_routes import router as share_router
from .config_routes import router as config_router

__all__ = [
    "basic_router",
    "user_router",
    "share_router", 
    "config_router"
] 