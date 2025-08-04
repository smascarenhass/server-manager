#!/usr/bin/env python3
"""
Exemplo de uso dos serviços de comandos do Server Manager
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.command_service import CommandService, CommandResult
from services.standard_commands import StandardCommands
import json

def exemplo_command_service():
    """Exemplo básico do CommandService"""
    print("=== EXEMPLO COMMAND SERVICE ===")
    
    # Inicializar serviço
    cmd_service = CommandService()
    
    # Executar comandos básicos
    print("\n1. Listando arquivos:")
    result = cmd_service.ls(".", "-la")
    print(f"Comando: {result.command}")
    print(f"Sucesso: {result.success}")
    print(f"Saída: {result.stdout[:200]}...")
    
    print("\n2. Mostrando diretório atual:")
    result = cmd_service.pwd()
    print(f"Diretório: {result.stdout.strip()}")
    
    print("\n3. Informações do sistema:")
    result = cmd_service.run("uname -a")
    print(f"Sistema: {result.stdout.strip()}")
    
    print("\n4. Uso de memória:")
    result = cmd_service.free("-h")
    print(f"Memória: {result.stdout.strip()}")
    
    # Mostrar histórico
    print(f"\n5. Histórico ({len(cmd_service.command_history)} comandos):")
    for i, hist in enumerate(cmd_service.get_history(5)):
        print(f"  {i+1}. {hist.command} - {'✅' if hist.success else '❌'} ({hist.execution_time:.2f}s)")

def exemplo_standard_commands():
    """Exemplo do StandardCommands"""
    print("\n=== EXEMPLO STANDARD COMMANDS ===")
    
    # Inicializar serviço
    std_commands = StandardCommands()
    
    # Mostrar comandos disponíveis
    print("\n1. Comandos padrão disponíveis:")
    available = std_commands.get_available_commands()
    for name, info in available["available_commands"].items():
        print(f"  - {name}: {info['description']} ({info['command_count']} comandos)")
    
    # Executar verificação do sistema
    print("\n2. Verificação do sistema:")
    system_check = std_commands.system_check()
    
    for check_name, check_result in system_check["system_check"].items():
        print(f"\n  {check_name.upper()}:")
        print(f"    Descrição: {check_result['description']}")
        print(f"    Comandos: {check_result['successful_commands']}/{check_result['total_commands']} com sucesso")
        
        for result in check_result['results']:
            status = "✅" if result['success'] else "❌"
            print(f"      {status} {result['command']}")

def exemplo_comandos_especificos():
    """Exemplo de comandos específicos"""
    print("\n=== EXEMPLO COMANDOS ESPECÍFICOS ===")
    
    cmd_service = CommandService()
    
    # Comandos básicos
    print("\n1. Comandos básicos:")
    
    # Listar arquivos
    result = cmd_service.ls(".", "-la")
    print(f"Listar arquivos: {'✅' if result.success else '❌'}")
    
    # Ver uso de disco
    result = cmd_service.df("-h")
    print(f"Uso de disco: {'✅' if result.success else '❌'}")
    print(result.stdout)
    
    # Ver processos
    result = cmd_service.ps("aux --sort=-%cpu | head -5")
    print(f"Top 5 processos: {'✅' if result.success else '❌'}")
    print(result.stdout)

def exemplo_json_output():
    """Exemplo de saída em JSON"""
    print("\n=== EXEMPLO SAÍDA JSON ===")
    
    cmd_service = CommandService()
    std_commands = StandardCommands()
    
    # Executar comando e converter para JSON
    result = cmd_service.run("ls -la")
    json_result = cmd_service.to_dict(result)
    
    print("Resultado em JSON:")
    print(json.dumps(json_result, indent=2, ensure_ascii=False))
    
    # Verificação do sistema em JSON
    system_check = std_commands.system_check()
    
    print("\nVerificação do sistema em JSON:")
    print(json.dumps(system_check, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    print("🚀 SERVER MANAGER - EXEMPLOS DE USO")
    print("=" * 50)
    
    try:
        exemplo_command_service()
        exemplo_standard_commands()
        exemplo_comandos_especificos()
        exemplo_json_output()
        
        print("\n✅ Todos os exemplos executados com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc() 