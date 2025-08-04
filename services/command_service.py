import subprocess
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CommandResult:
    """Resultado da execução de um comando"""
    command: str
    stdout: str
    stderr: str
    return_code: int
    execution_time: float
    timestamp: datetime
    success: bool

class CommandService:
    """Serviço para execução de comandos no sistema operacional"""
    
    def __init__(self, working_directory: str = None):
        """
        Inicializa o CommandService
        
        Args:
            working_directory: Diretório de trabalho padrão para os comandos
        """
        self.working_directory = working_directory or os.getcwd()
        self.command_history: List[CommandResult] = []
        
    def run(self, command: str, timeout: int = 30) -> CommandResult:
        """
        Executa um comando no sistema
        
        Args:
            command: Comando a ser executado
            timeout: Timeout em segundos
            
        Returns:
            CommandResult com os resultados da execução
        """
        start_time = datetime.now()
        
        try:
            # Executa o comando
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.working_directory
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            command_result = CommandResult(
                command=command,
                stdout=result.stdout or "",
                stderr=result.stderr or "",
                return_code=result.returncode,
                execution_time=execution_time,
                timestamp=start_time,
                success=result.returncode == 0
            )
            
            # Adiciona ao histórico
            self.command_history.append(command_result)
            
            logger.info(f"Comando executado: {command} - Sucesso: {command_result.success}")
            
            return command_result
            
        except subprocess.TimeoutExpired:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_result = CommandResult(
                command=command,
                stdout="",
                stderr=f"Comando expirou após {timeout} segundos",
                return_code=-1,
                execution_time=execution_time,
                timestamp=start_time,
                success=False
            )
            self.command_history.append(error_result)
            logger.error(f"Timeout no comando: {command}")
            return error_result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_result = CommandResult(
                command=command,
                stdout="",
                stderr=str(e),
                return_code=-1,
                execution_time=execution_time,
                timestamp=start_time,
                success=False
            )
            self.command_history.append(error_result)
            logger.error(f"Erro ao executar comando {command}: {e}")
            return error_result
    
    # Comandos básicos (máximo 10)
    def ls(self, path: str = ".", options: str = "") -> CommandResult:
        """Lista arquivos e diretórios"""
        command = f"ls {options} {path}"
        return self.run(command)
    
    def cd(self, path: str) -> CommandResult:
        """Muda o diretório de trabalho"""
        try:
            os.chdir(path)
            self.working_directory = os.getcwd()
            return CommandResult(
                command=f"cd {path}",
                stdout=f"Diretório alterado para: {self.working_directory}",
                stderr="",
                return_code=0,
                execution_time=0.0,
                timestamp=datetime.now(),
                success=True
            )
        except Exception as e:
            return CommandResult(
                command=f"cd {path}",
                stdout="",
                stderr=str(e),
                return_code=-1,
                execution_time=0.0,
                timestamp=datetime.now(),
                success=False
            )
    
    def pwd(self) -> CommandResult:
        """Mostra o diretório atual"""
        return self.run("pwd")
    
    def ps(self, options: str = "aux") -> CommandResult:
        """Lista processos em execução"""
        return self.run(f"ps {options}")
    
    def df(self, options: str = "-h") -> CommandResult:
        """Mostra uso de disco"""
        return self.run(f"df {options}")
    
    def free(self, options: str = "-h") -> CommandResult:
        """Mostra uso de memória"""
        return self.run(f"free {options}")
    
    def cat(self, file_path: str) -> CommandResult:
        """Mostra conteúdo de um arquivo"""
        return self.run(f"cat {file_path}")
    
    def tail(self, file_path: str, lines: int = 10) -> CommandResult:
        """Mostra as últimas linhas de um arquivo"""
        return self.run(f"tail -n {lines} {file_path}")
    
    def grep(self, pattern: str, file_path: str = "", options: str = "") -> CommandResult:
        """Busca padrões em arquivos"""
        if file_path:
            return self.run(f"grep {options} '{pattern}' {file_path}")
        else:
            return self.run(f"grep {options} '{pattern}'")
    
    def systemctl(self, action: str, service: str = "") -> CommandResult:
        """Gerencia serviços do systemd"""
        if service:
            return self.run(f"systemctl {action} {service}")
        else:
            return self.run(f"systemctl {action}")
    
    def get_history(self, limit: int = None) -> List[CommandResult]:
        """Retorna o histórico de comandos"""
        if limit:
            return self.command_history[-limit:]
        return self.command_history.copy()
    
    def get_last_result(self) -> Optional[CommandResult]:
        """Retorna o resultado do último comando"""
        if self.command_history:
            return self.command_history[-1]
        return None
    
    def clear_history(self):
        """Limpa o histórico de comandos"""
        self.command_history.clear()
    
    def to_dict(self, result: CommandResult) -> Dict[str, Any]:
        """Converte um CommandResult para dicionário"""
        return {
            "command": result.command,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.return_code,
            "execution_time": result.execution_time,
            "timestamp": result.timestamp.isoformat(),
            "success": result.success
        } 