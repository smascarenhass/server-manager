# Samba Manager API

API FastAPI para gerenciamento de usuários Samba.

## Estrutura do Projeto

```
api/
├── main.py              # Arquivo principal da aplicação
├── models/              # Modelos Pydantic
│   ├── __init__.py
│   ├── user_models.py   # Modelos relacionados a usuários
│   ├── share_models.py  # Modelos relacionados a shares
│   └── api_models.py    # Modelos de resposta da API
├── routers/             # Roteadores organizados por funcionalidade
│   ├── __init__.py
│   ├── basic_routes.py  # Rotas básicas (root, health)
│   ├── user_routes.py   # Rotas para gerenciamento de usuários
│   ├── share_routes.py  # Rotas para gerenciamento de shares
│   └── config_routes.py # Rotas para configurações
└── README.md
```

## Modelos

### UserCreate
Modelo para criação de usuários com campos opcionais para configuração de shares.

### UserUpdate
Modelo para atualização de usuários com todos os campos opcionais.

### UserResponse
Modelo de resposta para informações de usuários.

### ShareConfig
Modelo para configuração de shares.

### ApiResponse
Modelo padrão para respostas da API com sucesso, mensagem e dados opcionais.

## Roteadores

### Basic Routes (`/`)
- `GET /` - Informações da API
- `GET /health` - Verificação de saúde

### User Routes (`/users`)
- `GET /users` - Lista todos os usuários
- `GET /users/{username}` - Obtém usuário específico
- `POST /users` - Cria novo usuário
- `PUT /users/{username}` - Atualiza usuário
- `DELETE /users/{username}` - Remove usuário
- `POST /users/{username}/password` - Altera senha

### Share Routes (`/shares`)
- `POST /shares` - Adiciona share para usuário
- `DELETE /shares/{username}` - Remove share do usuário

### Config Routes (`/config`)
- `GET /config/environments` - Lista ambientes disponíveis
- `POST /config/test` - Testa configuração
- `POST /config/reload` - Recarrega serviço Samba
- `POST /config/backup` - Faz backup da configuração

## Como Executar

```bash
cd api
python main.py
```

A API estará disponível em `http://localhost:8000` com documentação em `/docs`.

## Benefícios da Nova Estrutura

1. **Separação de Responsabilidades**: Cada arquivo tem uma função específica
2. **Manutenibilidade**: Código mais fácil de manter e modificar
3. **Reutilização**: Modelos podem ser reutilizados em diferentes partes
4. **Organização**: Estrutura clara e lógica
5. **Escalabilidade**: Fácil adicionar novas funcionalidades 