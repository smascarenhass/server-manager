#!/usr/bin/env python3
"""
Testes unitários para os serviços de comandos
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Adicionar o diretório atual ao path para importar os módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from command_service import CommandService, CommandResult
from standard_commands import StandardCommands

class TestCommandService(unittest.TestCase):
    """Testes para o CommandService"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.cmd_service = CommandService()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Limpeza após cada teste"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_run_simple_command(self):
        """Testa execução de comando simples"""
        result = self.cmd_service.run("echo 'test'")
        
        self.assertTrue(result.success)
        self.assertEqual(result.stdout.strip(), "test")
        self.assertEqual(result.return_code, 0)
        self.assertIsInstance(result.execution_time, float)
        self.assertIsInstance(result.timestamp, type(result.timestamp))
    
    def test_run_failing_command(self):
        """Testa execução de comando que falha"""
        result = self.cmd_service.run("false")
        
        self.assertFalse(result.success)
        self.assertEqual(result.return_code, 1)
        self.assertEqual(result.stdout, "")
    
    def test_run_nonexistent_command(self):
        """Testa execução de comando inexistente"""
        result = self.cmd_service.run("comando_que_nao_existe_12345")
        
        self.assertFalse(result.success)
        self.assertEqual(result.return_code, 127)  # Comando não encontrado
    
    def test_run_with_timeout(self):
        """Testa timeout em comando"""
        result = self.cmd_service.run("sleep 10", timeout=1)
        
        self.assertFalse(result.success)
        self.assertIn("expirou", result.stderr)
    
    def test_ls_command(self):
        """Testa comando ls"""
        result = self.cmd_service.ls(".", "-la")
        
        self.assertTrue(result.success)
        self.assertIn("ls", result.command)
    
    def test_pwd_command(self):
        """Testa comando pwd"""
        result = self.cmd_service.pwd()
        
        self.assertTrue(result.success)
        self.assertIsInstance(result.stdout, str)
        self.assertGreater(len(result.stdout.strip()), 0)
    
    def test_cd_command(self):
        """Testa comando cd"""
        original_dir = os.getcwd()
        
        result = self.cmd_service.cd(self.temp_dir)
        
        self.assertTrue(result.success)
        self.assertEqual(os.getcwd(), self.temp_dir)
        
        # Voltar ao diretório original
        os.chdir(original_dir)
    
    def test_command_history(self):
        """Testa histórico de comandos"""
        # Executar alguns comandos
        self.cmd_service.run("echo 'test1'")
        self.cmd_service.run("echo 'test2'")
        self.cmd_service.run("echo 'test3'")
        
        history = self.cmd_service.get_history()
        
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0].stdout.strip(), "test1")
        self.assertEqual(history[1].stdout.strip(), "test2")
        self.assertEqual(history[2].stdout.strip(), "test3")
    
    def test_get_last_result(self):
        """Testa obtenção do último resultado"""
        result1 = self.cmd_service.run("echo 'first'")
        result2 = self.cmd_service.run("echo 'second'")
        
        last_result = self.cmd_service.get_last_result()
        
        self.assertEqual(last_result, result2)
        self.assertEqual(last_result.stdout.strip(), "second")
    
    def test_clear_history(self):
        """Testa limpeza do histórico"""
        self.cmd_service.run("echo 'test'")
        self.cmd_service.run("echo 'test2'")
        
        self.assertEqual(len(self.cmd_service.command_history), 2)
        
        self.cmd_service.clear_history()
        
        self.assertEqual(len(self.cmd_service.command_history), 0)
    
    def test_to_dict_conversion(self):
        """Testa conversão para dicionário"""
        result = self.cmd_service.run("echo 'test'")
        dict_result = self.cmd_service.to_dict(result)
        
        self.assertIsInstance(dict_result, dict)
        self.assertIn("command", dict_result)
        self.assertIn("stdout", dict_result)
        self.assertIn("stderr", dict_result)
        self.assertIn("return_code", dict_result)
        self.assertIn("execution_time", dict_result)
        self.assertIn("timestamp", dict_result)
        self.assertIn("success", dict_result)
        
        self.assertEqual(dict_result["stdout"].strip(), "test")
        self.assertTrue(dict_result["success"])

class TestStandardCommands(unittest.TestCase):
    """Testes para o StandardCommands"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.std_commands = StandardCommands()
    
    def test_get_available_commands(self):
        """Testa obtenção de comandos disponíveis"""
        available = self.std_commands.get_available_commands()
        
        self.assertIn("available_commands", available)
        self.assertIsInstance(available["available_commands"], dict)
        
        # Verificar se alguns comandos padrão existem
        expected_commands = ["system_info", "disk_usage", "memory_usage"]
        for cmd in expected_commands:
            self.assertIn(cmd, available["available_commands"])
    
    def test_execute_standard_command(self):
        """Testa execução de comando padrão"""
        result = self.std_commands.execute_standard_command("system_info")
        
        self.assertIn("command_name", result)
        self.assertIn("description", result)
        self.assertIn("results", result)
        self.assertIn("total_commands", result)
        self.assertIn("successful_commands", result)
        
        self.assertEqual(result["command_name"], "system_info")
        self.assertIsInstance(result["results"], list)
    
    def test_execute_nonexistent_command(self):
        """Testa execução de comando padrão inexistente"""
        result = self.std_commands.execute_standard_command("comando_inexistente")
        
        self.assertIn("error", result)
        self.assertIn("available_commands", result)
    
    def test_system_check(self):
        """Testa verificação do sistema"""
        result = self.std_commands.system_check()
        
        self.assertIn("system_check", result)
        self.assertIn("timestamp", result)
        
        checks = result["system_check"]
        expected_checks = ["system_info", "disk_usage", "memory_usage", "processes"]
        
        for check in expected_checks:
            self.assertIn(check, checks)
    
    def test_custom_command_group(self):
        """Testa grupo de comandos customizados"""
        commands = ["echo 'test1'", "echo 'test2'", "echo 'test3'"]
        
        result = self.std_commands.custom_command_group(commands, "test_group")
        
        self.assertIn("group_name", result)
        self.assertIn("commands", result)
        self.assertIn("results", result)
        self.assertIn("total_commands", result)
        self.assertIn("successful_commands", result)
        
        self.assertEqual(result["group_name"], "test_group")
        self.assertEqual(result["commands"], commands)
        self.assertEqual(result["total_commands"], 3)
        self.assertEqual(result["successful_commands"], 3)

class TestIntegration(unittest.TestCase):
    """Testes de integração"""
    
    def test_command_service_with_standard_commands(self):
        """Testa integração entre CommandService e StandardCommands"""
        cmd_service = CommandService()
        std_commands = StandardCommands(cmd_service)
        
        # Verificar se compartilham a mesma instância
        self.assertEqual(std_commands.command_service, cmd_service)
        
        # Executar comando padrão
        result = std_commands.execute_standard_command("system_info")
        
        self.assertTrue(result["total_commands"] > 0)
        self.assertGreaterEqual(result["successful_commands"], 0)
        
        # Verificar se o histórico foi atualizado
        history = cmd_service.get_history()
        self.assertGreater(len(history), 0)

if __name__ == "__main__":
    # Executar os testes
    unittest.main(verbosity=2) 