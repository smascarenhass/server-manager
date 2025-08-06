"""
Testes para o SambaService
"""

import os
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock
from services.samba_service import SambaService
from config.samba_config import SambaConfig


class TestSambaService(unittest.TestCase):
    """Testes para o SambaService"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Criar arquivo temporário para testes
        self.temp_dir = tempfile.mkdtemp()
        self.test_smb_conf = os.path.join(self.temp_dir, "test_smb.conf")
        
        # Conteúdo de teste do smb.conf
        self.test_content = """#
# Sample configuration file for the Samba suite
#

[global]
   workgroup = WORKGROUP
   server string = %h server (Samba, Ubuntu)
   log file = /var/log/samba/log.%m
   max log size = 1000
   server role = standalone server
   map to guest = bad user

[printers]
   comment = All Printers
   browseable = no
   path = /var/tmp
   printable = yes
   guest ok = no
   read only = yes
   create mask = 0700

[print$]
   comment = Printer Drivers
   path = /var/lib/samba/printers
   browseable = yes
   read only = yes
   guest ok = no

[main]
   path = /home/server/hdds/main
   browseable = yes
   writable = yes
   guest ok = no
   valid users = server

[eric]
   path = /home/server/hdds/main/users/eric
   valid users = eric
   read only = no
   browseable = yes
   create mask = 0660
   directory mask = 0770
"""
        
        # Escrever arquivo de teste
        with open(self.test_smb_conf, 'w') as f:
            f.write(self.test_content)
        
        # Configurar ambiente de teste
        self.test_config = {
            "smb_conf_path": self.test_smb_conf,
            "backup_dir": os.path.join(self.temp_dir, "backups")
        }
        
        # Mock da configuração
        with patch.object(SambaConfig, 'get_environment_config', return_value=self.test_config):
            self.samba_service = SambaService(environment="testing")
    
    def tearDown(self):
        """Limpeza após os testes"""
        # Remover diretório temporário
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Testa inicialização do service"""
        self.assertEqual(self.samba_service.smb_conf_path, self.test_smb_conf)
        self.assertEqual(self.samba_service.backup_dir, os.path.join(self.temp_dir, "backups"))
        self.assertTrue(os.path.exists(self.samba_service.backup_dir))
    
    def test_read_config(self):
        """Testa leitura da configuração"""
        content = self.samba_service.read_config()
        self.assertIn("[global]", content)
        self.assertIn("[printers]", content)
        self.assertIn("[eric]", content)
    
    def test_parse_shares(self):
        """Testa parseamento das shares"""
        content = self.samba_service.read_config()
        shares = self.samba_service.parse_shares(content)
        
        # Verificar se todas as shares foram parseadas
        self.assertIn("printers", shares)
        self.assertIn("print$", shares)
        self.assertIn("main", shares)
        self.assertIn("eric", shares)
        
        # Verificar configuração da share eric
        eric_config = shares["eric"]
        self.assertEqual(eric_config["path"], "/home/server/hdds/main/users/eric")
        self.assertEqual(eric_config["valid users"], "eric")
        self.assertEqual(eric_config["read only"], "no")
    
    def test_user_share_exists(self):
        """Testa verificação de existência de usuário"""
        # Usuário que existe
        self.assertTrue(self.samba_service.user_share_exists("eric"))
        self.assertTrue(self.samba_service.user_share_exists("main"))
        
        # Usuário que não existe
        self.assertFalse(self.samba_service.user_share_exists("joao"))
        self.assertFalse(self.samba_service.user_share_exists("maria"))
    
    def test_list_user_shares(self):
        """Testa listagem de shares de usuário"""
        user_shares = self.samba_service.list_user_shares()
        
        # Deve encontrar as shares de usuário (excluindo printers, print$)
        usernames = [share['username'] for share in user_shares]
        self.assertIn("main", usernames)
        self.assertIn("eric", usernames)
        self.assertNotIn("printers", usernames)
        self.assertNotIn("print$", usernames)
    
    def test_get_user_share_config(self):
        """Testa obtenção de configuração de usuário"""
        # Usuário que existe
        config = self.samba_service.get_user_share_config("eric")
        self.assertIsNotNone(config)
        self.assertEqual(config["path"], "/home/server/hdds/main/users/eric")
        self.assertEqual(config["valid users"], "eric")
        
        # Usuário que não existe
        config = self.samba_service.get_user_share_config("joao")
        self.assertIsNone(config)
    
    def test_add_user_share(self):
        """Testa adição de usuário"""
        # Adicionar novo usuário
        success = self.samba_service.add_user_share(
            username="joao",
            path="/home/server/hdds/main/users/joao",
            browseable="yes",
            writable="yes"
        )
        
        self.assertTrue(success)
        
        # Verificar se foi adicionado
        self.assertTrue(self.samba_service.user_share_exists("joao"))
        
        # Verificar configuração
        config = self.samba_service.get_user_share_config("joao")
        self.assertEqual(config["path"], "/home/server/hdds/main/users/joao")
        self.assertEqual(config["valid users"], "joao")
        self.assertEqual(config["read only"], "no")
        self.assertEqual(config["browseable"], "yes")
    
    def test_add_user_share_already_exists(self):
        """Testa adição de usuário que já existe"""
        # Tentar adicionar usuário que já existe
        success = self.samba_service.add_user_share(
            username="eric",
            path="/novo/caminho"
        )
        
        self.assertFalse(success)
    
    def test_remove_user_share(self):
        """Testa remoção de usuário"""
        # Remover usuário existente
        success = self.samba_service.remove_user_share("eric")
        
        self.assertTrue(success)
        
        # Verificar se foi removido
        self.assertFalse(self.samba_service.user_share_exists("eric"))
        
        # Verificar se configuração foi removida
        config = self.samba_service.get_user_share_config("eric")
        self.assertIsNone(config)
    
    def test_remove_user_share_not_exists(self):
        """Testa remoção de usuário que não existe"""
        # Tentar remover usuário que não existe
        success = self.samba_service.remove_user_share("joao")
        
        self.assertFalse(success)
    
    def test_update_user_share(self):
        """Testa atualização de configuração de usuário"""
        # Atualizar configuração
        success = self.samba_service.update_user_share(
            "eric",
            browseable="no",
            create_mask="0640"
        )
        
        self.assertTrue(success)
        
        # Verificar se foi atualizado
        config = self.samba_service.get_user_share_config("eric")
        self.assertEqual(config["browseable"], "no")
        self.assertEqual(config["create mask"], "0640")
        
        # Verificar se outras configurações foram preservadas
        self.assertEqual(config["path"], "/home/server/hdds/main/users/eric")
        self.assertEqual(config["valid users"], "eric")
    
    def test_update_user_share_not_exists(self):
        """Testa atualização de usuário que não existe"""
        # Tentar atualizar usuário que não existe
        success = self.samba_service.update_user_share(
            "joao",
            browseable="no"
        )
        
        self.assertFalse(success)
    
    def test_backup_config(self):
        """Testa backup da configuração"""
        backup_path = self.samba_service.backup_config()
        
        # Verificar se backup foi criado
        self.assertTrue(os.path.exists(backup_path))
        
        # Verificar se conteúdo é igual
        with open(backup_path, 'r') as f:
            backup_content = f.read()
        
        original_content = self.samba_service.read_config()
        self.assertEqual(backup_content, original_content)
    
    def test_format_share_config(self):
        """Testa formatação de configuração de share"""
        config = {
            "path": "/test/path",
            "valid users": "testuser",
            "read only": "no"
        }
        
        formatted = self.samba_service.format_share_config("testuser", config)
        
        expected = """[testuser]
   path = /test/path
   valid users = testuser
   read only = no"""
        
        self.assertEqual(formatted, expected)
    
    @patch('subprocess.run')
    def test_test_config_success(self, mock_run):
        """Testa validação de configuração com sucesso"""
        mock_run.return_value.returncode = 0
        
        result = self.samba_service.test_config()
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_test_config_failure(self, mock_run):
        """Testa validação de configuração com falha"""
        mock_run.return_value.returncode = 1
        
        result = self.samba_service.test_config()
        
        self.assertFalse(result)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_reload_samba_success(self, mock_run):
        """Testa recarregamento do Samba com sucesso"""
        mock_run.return_value.returncode = 0
        
        result = self.samba_service.reload_samba()
        
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ['systemctl', 'reload', 'smbd'],
            capture_output=True,
            text=True,
            timeout=30
        )
    
    @patch('subprocess.run')
    def test_reload_samba_failure(self, mock_run):
        """Testa recarregamento do Samba com falha"""
        mock_run.return_value.returncode = 1
        
        result = self.samba_service.reload_samba()
        
        self.assertFalse(result)
        mock_run.assert_called_once()
    
    def test_rebuild_config_content(self):
        """Testa reconstrução do conteúdo do arquivo"""
        # Ler configuração original
        original_content = self.samba_service.read_config()
        
        # Parsear shares
        shares = self.samba_service.parse_shares(original_content)
        
        # Remover uma share
        del shares["eric"]
        
        # Reconstruir conteúdo
        new_content = self.samba_service._rebuild_config_content(original_content, shares)
        
        # Verificar se share foi removida
        self.assertNotIn("[eric]", new_content)
        
        # Verificar se outras shares foram preservadas
        self.assertIn("[global]", new_content)
        self.assertIn("[printers]", new_content)
        self.assertIn("[main]", new_content)


class TestSambaConfig(unittest.TestCase):
    """Testes para o SambaConfig"""
    
    def test_list_environments(self):
        """Testa listagem de ambientes"""
        environments = SambaConfig.list_environments()
        expected = ['development', 'production', 'testing']
        self.assertEqual(environments, expected)
    
    def test_get_environment_config(self):
        """Testa obtenção de configuração de ambiente"""
        # Ambiente existente
        config = SambaConfig.get_environment_config("production")
        self.assertIn("smb_conf_path", config)
        self.assertIn("backup_dir", config)
        
        # Ambiente inexistente (deve retornar production)
        config = SambaConfig.get_environment_config("inexistente")
        self.assertIn("smb_conf_path", config)
        self.assertIn("backup_dir", config)
    
    def test_get_smb_conf_path(self):
        """Testa obtenção do caminho do arquivo smb.conf"""
        path = SambaConfig.get_smb_conf_path("production")
        self.assertEqual(path, "/etc/samba/smb.conf")
    
    def test_get_backup_dir(self):
        """Testa obtenção do diretório de backup"""
        backup_dir = SambaConfig.get_backup_dir("production")
        self.assertEqual(backup_dir, "/var/backups/samba")


if __name__ == '__main__':
    unittest.main() 