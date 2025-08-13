"""
Rotas para gerenciamento de shares
"""

from fastapi import APIRouter, HTTPException, status
from models.api_models import ApiResponse
from services.samba_service import SambaService

router = APIRouter(prefix="/shares", tags=["Shares"])
samba_service = SambaService(environment="production")


@router.post("/", response_model=ApiResponse)
async def add_share(username: str, path: str, **kwargs):
    """Adiciona uma share para um usuário existente"""
    try:
        # Verificar se usuário existe
        if not samba_service.user_exists(username):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário '{username}' não encontrado"
            )
        
        # Verificar se já tem share
        if samba_service.user_share_exists(username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Usuário '{username}' já possui uma share"
            )
        
        # Adicionar share
        success = samba_service.add_user_share(username, path, **kwargs)
        
        if success:
            return ApiResponse(
                success=True,
                message=f"Share adicionada para usuário '{username}' com sucesso"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao adicionar share para usuário '{username}'"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar share: {str(e)}"
        )


@router.delete("/{username}", response_model=ApiResponse)
async def remove_share(username: str):
    """Remove a share de um usuário"""
    try:
        # Verificar se usuário tem share
        if not samba_service.user_share_exists(username):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário '{username}' não possui share"
            )
        
        # Remover share
        success = samba_service.remove_user_share(username)
        
        if success:
            return ApiResponse(
                success=True,
                message=f"Share removida do usuário '{username}' com sucesso"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao remover share do usuário '{username}'"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover share: {str(e)}"
        ) 