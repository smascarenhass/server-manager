#!/usr/bin/env python3
"""
API FastAPI para gerenciamento de usuários Samba
"""

import sys
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Adicionar o diretório pai ao path para importar os serviços
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.samba_service import SambaService
from config.samba_config import SambaConfig


# Modelos Pydantic
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


class ShareConfig(BaseModel):
    path: str
    valid_users: str
    read_only: str
    browseable: str
    create_mask: str
    directory_mask: str


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


# Inicializar FastAPI
app = FastAPI(
    title="Samba Manager API",
    description="API para gerenciamento de usuários Samba",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar SambaService
samba_service = SambaService(environment="production")


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz"""
    return {
        "message": "Samba Manager API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
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


@app.get("/environments", tags=["Configuration"])
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


@app.get("/users", response_model=List[UserResponse], tags=["Users"])
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


@app.get("/users/{username}", response_model=UserResponse, tags=["Users"])
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


@app.post("/users", response_model=ApiResponse, tags=["Users"])
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


@app.put("/users/{username}", response_model=ApiResponse, tags=["Users"])
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


@app.delete("/users/{username}", response_model=ApiResponse, tags=["Users"])
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


@app.post("/users/{username}/password", response_model=ApiResponse, tags=["Users"])
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


@app.post("/shares", response_model=ApiResponse, tags=["Shares"])
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


@app.delete("/shares/{username}", response_model=ApiResponse, tags=["Shares"])
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


@app.post("/config/test", response_model=ApiResponse, tags=["Configuration"])
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


@app.post("/config/reload", response_model=ApiResponse, tags=["Configuration"])
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


@app.post("/config/backup", response_model=ApiResponse, tags=["Configuration"])
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


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 