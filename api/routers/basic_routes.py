"""
Rotas básicas da API
"""

from fastapi import APIRouter
from services.samba_service import SambaService

router = APIRouter(tags=["Root"])
samba_service = SambaService(environment="production")


@router.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Samba Manager API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@router.get("/health")
async def health_check():
    """Verificação de saúde da API"""
    try:
        # Testar se o SambaService está funcionando
        config_valid = samba_service.test_config()
        return {
            "status": "healthy",
            "samba_config_valid": config_valid,
            "environment": samba_service.environment
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        } 