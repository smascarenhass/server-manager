#!/usr/bin/env python3
"""
API FastAPI para gerenciamento de usuários Samba
"""

import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Adicionar o diretório pai ao path para importar os serviços
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routers import basic_router, user_router, share_router, config_router


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

# Incluir roteadores
app.include_router(basic_router)
app.include_router(user_router)
app.include_router(share_router)
app.include_router(config_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 