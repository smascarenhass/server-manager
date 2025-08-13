"""
Rotas para gerenciamento de usuários
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
from models.user_models import UserCreate, UserUpdate, UserResponse
from models.api_models import ApiResponse
from services.samba_service import SambaService

router = APIRouter(prefix="/users", tags=["Users"])
samba_service = SambaService(environment="production")


@router.get("/", response_model=List[UserResponse])
async def list_users():
    """Lista todos os usuários Samba"""
    try:
        users = samba_service.list_samba_users()
        user_shares = samba_service.list_user_shares()
        
        # Combinar informações
        result = []
        for user in users:
            share_config = None
            for share in user_shares:
                if share['username'] == user['username']:
                    share_config = share['config']
                    break
            
            result.append(UserResponse(
                username=user['username'],
                has_share=user['has_share'],
                share_path=user['share_path'],
                share_config=share_config
            ))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar usuários: {str(e)}"
        )


@router.get("/{username}", response_model=UserResponse)
async def get_user(username: str):
    """Obtém informações de um usuário específico"""
    try:
        # Verificar se usuário existe no sistema
        if not samba_service.user_exists(username):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário '{username}' não encontrado"
            )
        
        # Verificar se tem share
        has_share = samba_service.user_share_exists(username)
        share_path = "N/A"
        share_config = None
        
        if has_share:
            config = samba_service.get_user_share_config(username)
            share_path = config.get('path', 'N/A')
            share_config = config
        
        return UserResponse(
            username=username,
            has_share=has_share,
            share_path=share_path,
            share_config=share_config
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter usuário: {str(e)}"
        )


@router.post("/", response_model=ApiResponse)
async def create_user(user: UserCreate):
    """Cria um novo usuário Samba completo"""
    try:
        # Verificar se usuário já existe
        if samba_service.user_exists(user.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Usuário '{user.username}' já existe"
            )
        
        # Criar usuário
        success = samba_service.create_samba_user(
            username=user.username,
            password=user.password,
            home_dir=user.home_dir,
            share_path=user.share_path
        )
        
        if success:
            return ApiResponse(
                success=True,
                message=f"Usuário '{user.username}' criado com sucesso",
                data={
                    "username": user.username,
                    "has_share": True
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar usuário '{user.username}'"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar usuário: {str(e)}"
        )


@router.put("/{username}", response_model=ApiResponse)
async def update_user(username: str, user_update: UserUpdate):
    """Atualiza configurações de um usuário"""
    try:
        # Verificar se usuário existe
        if not samba_service.user_exists(username):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário '{username}' não encontrado"
            )
        
        # Preparar parâmetros para atualização
        update_params = {}
        if user_update.share_path:
            update_params['path'] = user_update.share_path
        if user_update.browseable:
            update_params['browseable'] = user_update.browseable
        if user_update.writable:
            update_params['writable'] = user_update.writable
        if user_update.guest_ok:
            update_params['guest_ok'] = user_update.guest_ok
        if user_update.create_mask:
            update_params['create_mask'] = user_update.create_mask
        if user_update.directory_mask:
            update_params['directory_mask'] = user_update.directory_mask
        
        # Atualizar configurações da share se existir
        if update_params and samba_service.user_share_exists(username):
            success = samba_service.update_user_share(username, **update_params)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao atualizar configurações da share"
                )
        
        # Alterar senha se fornecida
        if user_update.password:
            success = samba_service.change_samba_password(username, user_update.password)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao alterar senha"
                )
        
        return ApiResponse(
            success=True,
            message=f"Usuário '{username}' atualizado com sucesso"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar usuário: {str(e)}"
        )


@router.delete("/{username}", response_model=ApiResponse)
async def delete_user(username: str, remove_home: bool = False):
    """Remove um usuário Samba completo"""
    try:
        # Verificar se usuário existe
        if not samba_service.user_exists(username):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário '{username}' não encontrado"
            )
        
        # Remover usuário
        success = samba_service.remove_samba_user(username, remove_home)
        
        if success:
            return ApiResponse(
                success=True,
                message=f"Usuário '{username}' removido com sucesso"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao remover usuário '{username}'"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover usuário: {str(e)}"
        )


@router.post("/{username}/password", response_model=ApiResponse)
async def change_password(username: str, password: str):
    """Altera a senha de um usuário"""
    try:
        # Verificar se usuário existe
        if not samba_service.user_exists(username):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário '{username}' não encontrado"
            )
        
        # Alterar senha
        success = samba_service.change_samba_password(username, password)
        
        if success:
            return ApiResponse(
                success=True,
                message=f"Senha do usuário '{username}' alterada com sucesso"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao alterar senha do usuário '{username}'"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao alterar senha: {str(e)}"
        ) 