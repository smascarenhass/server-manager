# Server Manager

> Interface moderna para gerenciamento de servidores via comandos encapsulados em uma estrutura de microsserviços.

## 🚀 Visão Geral

O **Server Manager** é uma aplicação para facilitar o gerenciamento de servidores Linux através de uma interface amigável, com backend desacoplado, filas de mensagens e cache para desempenho otimizado.

---

## 🎯 Objetivo

Eliminar a complexidade do terminal ao administrar servidores, oferecendo uma solução moderna com painel de controle, execução de comandos, monitoramento em tempo real e integração com ferramentas como Docker, Redis e RabbitMQ.

---

## 🛠️ Tecnologias Utilizadas

- **Frontend:** JavaScript, Html e Css (vanila)
- **Backend:** Python (FastAPI)
- **Arquitetura:** Microsserviços
- **Containerização:** Docker
- **Mensageria:** RabbitMQ
- **Cache:** Redis
- **Banco de Dados:** PostgreSQL
- **Controle de versão:** Git + GitHub

---

## 🔧 Funcionalidades Esperadas

- [ ] Autenticação de usuários
- [ ] Adição/remoção de servidores
- [ ] Execução de comandos pré-definidos
- [ ] Visualização de logs em tempo real
- [ ] Monitoramento de serviços (CPU, memória, processos)
- [ ] Sistema de filas para comandos usando RabbitMQ
- [ ] Cache de resultados usando Redis
- [ ] API REST para integração externa

---

## 📦 Estrutura de Pastas (prevista)

/server-manager
│
├── api/ # Backend Python
├── frontend/ # Interface em JS
├── services/ # Microsserviços especializados
├── docker/ # Configuração de containers
├── database/ # Migrations e seeders
└── README.md

---

## ⚙️ Pré-requisitos

- Docker
- Docker Compose
- Git
- Python 3.11+

---

📫 Contato
Desenvolvido por Otávio Mascarenhas / Eric Telhado / Guilherme Trindade
GitHub: @smascarenhass / @erictelhado / @guicasta009
