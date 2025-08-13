.PHONY: help install dev test lint format clean shell run

# Variáveis
PYTHON := pipenv run python
PIPENV := pipenv
PIP := pipenv run pip

# Comando padrão
help: ## Mostra esta ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala as dependências do projeto
	$(PIPENV) install --dev

dev: ## Instala dependências de desenvolvimento
	$(PIPENV) install --dev

shell: ## Ativa o ambiente virtual
	$(PIPENV) shell

run: ## Executa o servidor de desenvolvimento
	$(PIPENV) run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

test: ## Executa os testes
	$(PIPENV) run pytest -v

test-coverage: ## Executa os testes com cobertura
	$(PIPENV) run pytest --cov=services --cov=api --cov-report=html --cov-report=term

lint: ## Executa o linter
	$(PIPENV) run flake8 services/ api/ --max-line-length=88 --extend-ignore=E203,W503

format: ## Formata o código com black
	$(PIPENV) run black services/ api/

format-check: ## Verifica se o código está formatado
	$(PIPENV) run black --check services/ api/

type-check: ## Executa verificação de tipos
	$(PIPENV) run mypy services/ api/

check: ## Executa todas as verificações
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test

clean: ## Limpa arquivos temporários
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

services-test: ## Testa os serviços de comandos
	$(PIPENV) run python services/example.py

services-lint: ## Lint dos serviços
	$(PIPENV) run flake8 services/ --max-line-length=88 --extend-ignore=E203,W503

services-format: ## Formata os serviços
	$(PIPENV) run black services/

services-type-check: ## Verificação de tipos dos serviços
	$(PIPENV) run mypy services/

services-check: ## Verifica os serviços
	$(MAKE) services-format
	$(MAKE) services-lint
	$(MAKE) services-type-check
	$(PIPENV) run python -m pytest services/test_commands.py -v

# Comandos de desenvolvimento
dev-setup: ## Configuração inicial do ambiente de desenvolvimento
	$(PIPENV) install --dev
	cp config.env.example .env
	@echo "Ambiente configurado! Edite o arquivo .env com suas configurações."

# Comandos de Docker (se necessário)
docker-build: ## Constrói a imagem Docker
	docker build -t server-manager .

docker-run: ## Executa o container Docker
	docker run -p 8000:8000 server-manager

# Comandos de banco de dados
db-migrate: ## Executa migrações do banco
	$(PIPENV) run alembic upgrade head

db-rollback: ## Reverte migrações
	$(PIPENV) run alembic downgrade -1

db-revision: ## Cria nova migração
	$(PIPENV) run alembic revision --autogenerate -m "$(message)"

# Comandos de segurança
security-check: ## Verifica vulnerabilidades
	$(PIPENV) run safety check

# Comandos de documentação
docs-serve: ## Serve a documentação
	$(PIPENV) run python -m http.server 8080 --directory docs/

# Comandos de deploy
deploy-check: ## Verifica se está pronto para deploy
	$(MAKE) check
	$(MAKE) security-check
	@echo "✅ Projeto pronto para deploy!" 