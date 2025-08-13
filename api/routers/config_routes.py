"""
Rotas para gerenciamento de configurações
"""

from fastapi import APIRouter, HTTPException, status
from models.api_models import ApiResponse
from services.samba_service import SambaService
from config.samba_config import SambaConfig

router = APIRouter(prefix="/config", tags=["Configuration"])
samba_service = SambaService(environment="production")


@router.get("/environments")
async def list_environments():
    """Lista ambientes disponíveis"""
    environments = SambaConfig.list_environments()
    configs = {}
    
    for env in environments:
        config = SambaConfig.get_environment_config(env)
        configs[env] = config
    
    return {
        "environments": environments,
        "configs": configs
    }


@router.post("/test", response_model=ApiResponse)
async def test_config():
    """Testa a configuração do Samba"""
    try:
        config_valid = samba_service.test_config()
        
        if config_valid:
            return ApiResponse(
                success=True,
                message="Configuração válida"
            )
        else:
            return ApiResponse(
                success=False,
                message="Configuração inválida"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao testar configuração: {str(e)}"
        )


@router.post("/reload", response_model=ApiResponse)
async def reload_samba():
    """Recarrega o serviço Samba"""
    try:
        reloaded = samba_service.reload_samba()
        
        if reloaded:
            return ApiResponse(
                success=True,
                message="Serviço Samba recarregado com sucesso"
            )
        else:
            return ApiResponse(
                success=False,
                message="Erro ao recarregar serviço Samba"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao recarregar serviço: {str(e)}"
        )


@router.post("/backup", response_model=ApiResponse)
async def backup_config():
    """Faz backup da configuração atual"""
    try:
        backup_path = samba_service.backup_config()
        
        return ApiResponse(
            success=True,
            message="Backup criado com sucesso",
            data={"backup_path": backup_path}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer backup: {str(e)}"
        ) 