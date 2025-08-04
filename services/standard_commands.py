from typing import Dict, Any, List
from .command_service import CommandService, CommandResult

class StandardCommands:
    """Serviço com comandos padrão básicos"""
    
    def __init__(self, command_service: CommandService = None):
        """
        Inicializa o StandardCommands
        
        Args:
            command_service: Instância do CommandService (cria uma nova se não fornecida)
        """
        self.command_service = command_service or CommandService()
        
        # Comandos padrão básicos
        self.standard_commands = {
            "system_info": {
                "description": "Informações básicas do sistema",
                "commands": [
                    "uname -a",
                    "hostname",
                    "whoami"
                ]
            },
            
            "disk_usage": {
                "description": "Uso de disco",
                "commands": [
                    "df -h"
                ]
            },
            
            "memory_usage": {
                "description": "Uso de memória",
                "commands": [
                    "free -h"
                ]
            },
            
            "processes": {
                "description": "Processos em execução",
                "commands": [
                    "ps aux --sort=-%cpu | head -10"
                ]
            },
            
            "services": {
                "description": "Status dos serviços",
                "commands": [
                    "systemctl list-units --type=service --state=running"
                ]
            }
        }
    
    def execute_standard_command(self, command_name: str) -> Dict[str, Any]:
        """
        Executa um comando padrão pré-definido
        
        Args:
            command_name: Nome do comando padrão
            
        Returns:
            Dicionário com os resultados de todos os comandos
        """
        if command_name not in self.standard_commands:
            return {
                "error": f"Comando padrão '{command_name}' não encontrado",
                "available_commands": list(self.standard_commands.keys())
            }
        
        command_info = self.standard_commands[command_name]
        results = []
        
        for cmd in command_info["commands"]:
            result = self.command_service.run(cmd)
            results.append(self.command_service.to_dict(result))
        
        return {
            "command_name": command_name,
            "description": command_info["description"],
            "results": results,
            "total_commands": len(results),
            "successful_commands": sum(1 for r in results if r["success"])
        }
    
    def get_available_commands(self) -> Dict[str, Any]:
        """Retorna lista de comandos padrão disponíveis"""
        return {
            "available_commands": {
                name: {
                    "description": info["description"],
                    "command_count": len(info["commands"])
                }
                for name, info in self.standard_commands.items()
            }
        }
    
    def system_check(self) -> Dict[str, Any]:
        """Executa verificação básica do sistema"""
        checks = [
            "system_info",
            "disk_usage", 
            "memory_usage",
            "processes"
        ]
        
        results = {}
        for check in checks:
            results[check] = self.execute_standard_command(check)
        
        return {
            "system_check": results,
            "timestamp": self.command_service.get_last_result().timestamp.isoformat() if self.command_service.get_last_result() else None
        }
    
    def custom_command_group(self, commands: List[str], group_name: str = "custom") -> Dict[str, Any]:
        """
        Executa um grupo de comandos customizados
        
        Args:
            commands: Lista de comandos a executar
            group_name: Nome do grupo
            
        Returns:
            Resultados dos comandos
        """
        results = []
        
        for cmd in commands:
            result = self.command_service.run(cmd)
            results.append(self.command_service.to_dict(result))
        
        return {
            "group_name": group_name,
            "commands": commands,
            "results": results,
            "total_commands": len(results),
            "successful_commands": sum(1 for r in results if r["success"])
        } 