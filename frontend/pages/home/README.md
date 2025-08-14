# Página de Usuários - Server Manager

Esta página exibe todos os usuários do sistema Samba em formato de cards, incluindo suas configurações de compartilhamento.

## Funcionalidades

- **Listagem de Usuários**: Exibe todos os usuários cadastrados no sistema
- **Status de Compartilhamento**: Mostra se o usuário tem compartilhamento ativo
- **Configurações Detalhadas**: Exibe todas as configurações do compartilhamento Samba
- **Interface Responsiva**: Cards se adaptam a diferentes tamanhos de tela

## Como Usar

1. **Acesse a página**: Abra `index.html` em um navegador
2. **Visualize os usuários**: Os cards são carregados automaticamente da API
3. **Navegue pelo menu**: Use o botão ☰ para abrir/fechar o menu lateral

## Estrutura dos Dados

Cada usuário exibe:
- **Avatar**: Primeira letra do nome de usuário
- **Nome**: Nome completo do usuário
- **Status**: Se tem compartilhamento ativo ou não
- **Caminho**: Diretório do compartilhamento
- **Configurações**: Todas as configurações Samba (permissões, máscaras, etc.)

## Configuração da API

A página se conecta à API na porta 8000. Verifique se:
- A API está rodando em `http://localhost:8000`
- O endpoint `/users` está funcionando
- CORS está configurado corretamente

## Desenvolvimento

Para modificar:
- **Estilos**: Edite `style.css`
- **Lógica**: Edite `main.js`
- **Configuração**: Edite `config.js`
- **Layout**: Edite `index.html` 