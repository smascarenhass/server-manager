# Serviços de Comandos - Server Manager

Sistema simplificado para execução de comandos no sistema operacional.

## 📋 Comandos Disponíveis

### CommandService - Comandos Básicos (10 comandos)

```python
from services import CommandService

cmd_service = CommandService()

# 1. Listar arquivos
result = cmd_service.ls(path=".", options="-la")

# 2. Mudar diretório
result = cmd_service.cd("/home/user")

# 3. Mostrar diretório atual
result = cmd_service.pwd()

# 4. Listar processos
result = cmd_service.ps(options="aux")

# 5. Ver uso de disco
result = cmd_service.df(options="-h")

# 6. Ver uso de memória
result = cmd_service.free(options="-h")

# 7. Ler arquivo
result = cmd_service.cat("/etc/hostname")

# 8. Últimas linhas de arquivo
result = cmd_service.tail("/var/log/syslog", lines=20)

# 9. Buscar em arquivos
result = cmd_service.grep("error", "/var/log/syslog")

# 10. Gerenciar serviços
result = cmd_service.systemctl("status", "nginx")
```

### Comando Genérico

```python
# Executar qualquer comando
result = cmd_service.run("comando_qualquer")
```

### StandardCommands - Comandos Padrão (5 grupos)

```python
from services import StandardCommands

std_commands = StandardCommands()

# 1. Informações do sistema
result = std_commands.execute_standard_command("system_info")

# 2. Uso de disco
result = std_commands.execute_standard_command("disk_usage")

# 3. Uso de memória
result = std_commands.execute_standard_command("memory_usage")

# 4. Processos em execução
result = std_commands.execute_standard_command("processes")

# 5. Status dos serviços
result = std_commands.execute_standard_command("services")
```

### Verificação Completa do Sistema

```python
# Verificação básica do sistema
system_check = std_commands.system_check()
```

## 📝 Exemplo de Uso

```python
from services import CommandService, StandardCommands

# Inicializar serviços
cmd_service = CommandService()
std_commands = StandardCommands()

# Executar comandos básicos
print("=== COMANDOS BÁSICOS ===")
result = cmd_service.ls(".", "-la")
print(f"Listagem: {result.success}")
print(result.stdout)

result = cmd_service.pwd()
print(f"Diretório atual: {result.stdout.strip()}")

result = cmd_service.free("-h")
print(f"Memória: {result.stdout}")

# Executar verificação do sistema
print("\n=== VERIFICAÇÃO DO SISTEMA ===")
system_check = std_commands.system_check()

for check_name, check_result in system_check["system_check"].items():
    print(f"\n{check_name}:")
    print(f"  Descrição: {check_result['description']}")
    print(f"  Comandos: {check_result['successful_commands']}/{check_result['total_commands']} com sucesso")
```

## 🔧 Propriedades do Resultado

```python
result = cmd_service.run("ls -la")

print(f"Comando: {result.command}")
print(f"Saída: {result.stdout}")
print(f"Erro: {result.stderr}")
print(f"Código de retorno: {result.return_code}")
print(f"Tempo de execução: {result.execution_time}s")
print(f"Sucesso: {result.success}")
```

## 📊 Histórico de Comandos

```python
# Executar alguns comandos
cmd_service.run("ls")
cmd_service.run("pwd")
cmd_service.run("whoami")

# Obter histórico
history = cmd_service.get_history()
for i, result in enumerate(history):
    print(f"{i+1}. {result.command} - {'✅' if result.success else '❌'}")

# Último resultado
last_result = cmd_service.get_last_result()
print(f"Último comando: {last_result.command}")
```

## 🚀 Integração com API

```python
from fastapi import APIRouter
from services import CommandService, StandardCommands

router = APIRouter()
cmd_service = CommandService()
std_commands = StandardCommands()

@router.post("/execute")
async def execute_command(command: str):
    result = cmd_service.run(command)
    return cmd_service.to_dict(result)

@router.get("/system-check")
async def system_check():
    return std_commands.system_check()

@router.get("/ls")
async def list_files(path: str = ".", options: str = ""):
    result = cmd_service.ls(path, options)
    return cmd_service.to_dict(result)
```

## 📦 Estrutura de Arquivos

```
services/
├── __init__.py          # Exporta as classes principais
├── command_service.py   # CommandService com 10 comandos básicos
├── standard_commands.py # StandardCommands com 5 grupos de comandos
├── example.py          # Exemplos de uso
├── test_commands.py    # Testes unitários
└── readme.md          # Esta documentação
```

## ✅ Comandos Disponíveis

### CommandService (10 comandos)
1. `ls()` - Listar arquivos
2. `cd()` - Mudar diretório
3. `pwd()` - Mostrar diretório atual
4. `ps()` - Listar processos
5. `df()` - Uso de disco
6. `free()` - Uso de memória
7. `cat()` - Ler arquivo
8. `tail()` - Últimas linhas
9. `grep()` - Buscar em arquivos
10. `systemctl()` - Gerenciar serviços

### StandardCommands (5 grupos)
1. `system_info` - Informações do sistema
2. `disk_usage` - Uso de disco
3. `memory_usage` - Uso de memória
4. `processes` - Processos em execução
5. `services` - Status dos serviços
