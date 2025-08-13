"""
Service para manipulação do arquivo de configuração do Samba
Permite adicionar, remover e gerenciar usuários e shares
"""

import os
import re
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from services.file_service import FileService
from config.samba_config import SambaConfig


class SambaService:
    """
    Service para manipulação do arquivo de configuração do Samba
    
    Exemplo de uso:
    samba_service = SambaService(environment="production")
    
    # Adicionar um novo usuário
    samba_service.add_user_share("joao", "/home/server/hdds/main/users/joao")
    
    # Remover um usuário
    samba_service.remove_user_share("joao")
    
    # Listar todos os usuários
    users = samba_service.list_user_shares()
    
    # Verificar se um usuário existe
    exists = samba_service.user_share_exists("joao")
    """
    
    def __init__(self, environment="production"):
        """
        Inicializa o SambaService
        
        Args:
            environment (str): Ambiente (development, production, testing)
        """
        self.environment = environment
        self.config = SambaConfig.get_environment_config(environment)
        self.smb_conf_path = self.config["smb_conf_path"]
        
        # Handle backup directory path
        backup_dir = self.config["backup_dir"]
        if backup_dir.startswith('./'):
            # Convert relative path to absolute path based on project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.backup_dir = os.path.join(project_root, backup_dir[2:])
        else:
            self.backup_dir = os.path.expanduser(backup_dir)
            
        self.file_service = FileService()
        
        # Garantir que o diretório de backup existe
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def backup_config(self) -> str:
        """
        Faz backup do arquivo de configuração atual
        
        Returns:
            str: Caminho do arquivo de backup
        """
        if not self.file_service.file_exists(self.smb_conf_path):
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.smb_conf_path}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"smb_conf_backup_{timestamp}.conf")
        
        shutil.copy2(self.smb_conf_path, backup_path)
        return backup_path
    
    def read_config(self) -> str:
        """
        Lê o conteúdo do arquivo de configuração
        
        Returns:
            str: Conteúdo do arquivo
        """
        content = self.file_service.read_file(self.smb_conf_path)
        if content is None:
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.smb_conf_path}")
        return content
    
    def write_config(self, content: str) -> None:
        """
        Escreve o conteúdo no arquivo de configuração
        
        Args:
            content (str): Conteúdo a ser escrito
        """
        self.file_service.write_file(self.smb_conf_path, content)
    
    def parse_shares(self, content: str) -> Dict[str, Dict[str, str]]:
        """
        Parseia as shares do arquivo de configuração
        
        Args:
            content (str): Conteúdo do arquivo
            
        Returns:
            Dict[str, Dict[str, str]]: Dicionário com as shares e suas configurações
        """
        shares = {}
        current_share = None
        current_config = {}
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Nova seção de share
            if line.startswith('[') and line.endswith(']') and not line.startswith('[global]'):
                # Salvar share anterior se existir
                if current_share and current_config:
                    shares[current_share] = current_config
                
                # Iniciar nova share
                current_share = line[1:-1]  # Remove [ e ]
                current_config = {}
            
            # Configuração da share atual
            elif current_share and '=' in line:
                key, value = line.split('=', 1)
                current_config[key.strip()] = value.strip()
        
        # Adicionar última share
        if current_share and current_config:
            shares[current_share] = current_config
        
        return shares
    
    def format_share_config(self, share_name: str, config: Dict[str, str]) -> str:
        """
        Formata a configuração de uma share para escrita no arquivo
        
        Args:
            share_name (str): Nome da share
            config (Dict[str, str]): Configuração da share
            
        Returns:
            str: Configuração formatada
        """
        lines = [f"[{share_name}]"]
        for key, value in config.items():
            lines.append(f"   {key} = {value}")
        return '\n'.join(lines)
    
    def add_user_share(self, username: str, path: str, 
                       browseable: str = "yes", writable: str = "yes",
                       guest_ok: str = "no", create_mask: str = "0660",
                       directory_mask: str = "0770") -> bool:
        """
        Adiciona uma nova share de usuário
        
        Args:
            username (str): Nome do usuário
            path (str): Caminho do diretório
            browseable (str): Se a share é navegável
            writable (str): Se a share é gravável
            guest_ok (str): Se permite acesso de convidados
            create_mask (str): Máscara de criação de arquivos
            directory_mask (str): Máscara de criação de diretórios
            
        Returns:
            bool: True se adicionado com sucesso
        """
        try:
            # Fazer backup
            self.backup_config()
            
            # Ler configuração atual
            content = self.read_config()
            
            # Verificar se usuário já existe
            if self.user_share_exists(username):
                raise ValueError(f"Share para usuário '{username}' já existe")
            
            # Parsear shares existentes
            shares = self.parse_shares(content)
            
            # Criar nova configuração de share
            new_share_config = {
                "path": path,
                "valid users": username,
                "read only": "no",
                "browseable": browseable,
                "create mask": create_mask,
                "directory mask": directory_mask
            }
            
            # Adicionar nova share
            shares[username] = new_share_config
            
            # Reconstruir conteúdo
            new_content = self._rebuild_config_content(content, shares)
            
            # Escrever nova configuração
            self.write_config(new_content)
            
            return True
            
        except Exception as e:
            print(f"Erro ao adicionar share para usuário '{username}': {str(e)}")
            return False
    
    def remove_user_share(self, username: str) -> bool:
        """
        Remove uma share de usuário
        
        Args:
            username (str): Nome do usuário
            
        Returns:
            bool: True se removido com sucesso
        """
        try:
            # Fazer backup
            self.backup_config()
            
            # Ler configuração atual
            content = self.read_config()
            
            # Verificar se usuário existe
            if not self.user_share_exists(username):
                raise ValueError(f"Share para usuário '{username}' não existe")
            
            # Parsear shares existentes
            shares = self.parse_shares(content)
            
            # Remover share
            if username in shares:
                del shares[username]
            
            # Reconstruir conteúdo
            new_content = self._rebuild_config_content(content, shares)
            
            # Escrever nova configuração
            self.write_config(new_content)
            
            return True
            
        except Exception as e:
            print(f"Erro ao remover share para usuário '{username}': {str(e)}")
            return False
    
    def update_user_share(self, username: str, **kwargs) -> bool:
        """
        Atualiza a configuração de uma share de usuário
        
        Args:
            username (str): Nome do usuário
            **kwargs: Configurações a serem atualizadas
            
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            # Fazer backup
            self.backup_config()
            
            # Ler configuração atual
            content = self.read_config()
            
            # Verificar se usuário existe
            if not self.user_share_exists(username):
                raise ValueError(f"Share para usuário '{username}' não existe")
            
            # Parsear shares existentes
            shares = self.parse_shares(content)
            
            # Atualizar configurações
            if username in shares:
                shares[username].update(kwargs)
            
            # Reconstruir conteúdo
            new_content = self._rebuild_config_content(content, shares)
            
            # Escrever nova configuração
            self.write_config(new_content)
            
            return True
            
        except Exception as e:
            print(f"Erro ao atualizar share para usuário '{username}': {str(e)}")
            return False
    
    def user_share_exists(self, username: str) -> bool:
        """
        Verifica se uma share de usuário existe
        
        Args:
            username (str): Nome do usuário
            
        Returns:
            bool: True se a share existe
        """
        try:
            content = self.read_config()
            shares = self.parse_shares(content)
            return username in shares
        except:
            return False
    
    def list_user_shares(self) -> List[Dict[str, str]]:
        """
        Lista todas as shares de usuário
        
        Returns:
            List[Dict[str, str]]: Lista de shares com suas configurações
        """
        try:
            content = self.read_config()
            shares = self.parse_shares(content)
            
            # Filtrar apenas shares de usuário (excluir [printers], [print$], etc.)
            user_shares = []
            for share_name, config in shares.items():
                if share_name not in ['printers', 'print$', 'homes', 'netlogon', 'profiles']:
                    user_shares.append({
                        'username': share_name,
                        'config': config
                    })
            
            return user_shares
        except Exception as e:
            print(f"Erro ao listar shares: {str(e)}")
            return []
    
    def get_user_share_config(self, username: str) -> Optional[Dict[str, str]]:
        """
        Obtém a configuração de uma share de usuário
        
        Args:
            username (str): Nome do usuário
            
        Returns:
            Optional[Dict[str, str]]: Configuração da share ou None se não existir
        """
        try:
            content = self.read_config()
            shares = self.parse_shares(content)
            return shares.get(username)
        except:
            return None
    
    def _rebuild_config_content(self, original_content: str, shares: Dict[str, Dict[str, str]]) -> str:
        """
        Reconstrói o conteúdo do arquivo de configuração
        
        Args:
            original_content (str): Conteúdo original
            shares (Dict[str, Dict[str, str]]): Shares atualizadas
            
        Returns:
            str: Novo conteúdo do arquivo
        """
        lines = original_content.split('\n')
        new_lines = []
        in_share_section = False
        current_share = None
        
        for line in lines:
            # Verificar se estamos em uma seção de share
            if line.strip().startswith('[') and line.strip().endswith(']'):
                share_name = line.strip()[1:-1]
                
                # Se for uma share de usuário, pular até encontrar próxima seção
                if share_name not in ['global', 'printers', 'print$', 'homes', 'netlogon', 'profiles']:
                    in_share_section = True
                    current_share = share_name
                    continue
                else:
                    in_share_section = False
                    current_share = None
                    new_lines.append(line)
                    continue
            
            # Se estamos em uma share de usuário, pular as linhas
            if in_share_section:
                continue
            
            # Adicionar linha se não estamos em uma share de usuário
            new_lines.append(line)
        
        # Adicionar shares de usuário no final
        for share_name, config in shares.items():
            if share_name not in ['global', 'printers', 'print$', 'homes', 'netlogon', 'profiles']:
                new_lines.append('')
                new_lines.append(self.format_share_config(share_name, config))
        
        return '\n'.join(new_lines)
    
    def test_config(self) -> bool:
        """
        Testa a configuração do Samba usando testparm
        
        Returns:
            bool: True se a configuração está válida
        """
        try:
            import subprocess
            result = subprocess.run(['testparm', self.smb_conf_path], 
                                 capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            print(f"Erro ao testar configuração: {str(e)}")
            return False
    
    def reload_samba(self) -> bool:
        """
        Recarrega o serviço do Samba
        
        Returns:
            bool: True se recarregado com sucesso
        """
        try:
            import subprocess
            result = subprocess.run(['systemctl', 'reload', 'smbd'], 
                                 capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            print(f"Erro ao recarregar Samba: {str(e)}")
            return False 

    def create_samba_user(self, username: str, password: str, home_dir: str = None, 
                     share_path: str = None) -> bool:
        """
        Cria usuário no Samba (apenas no smb.conf):
        1. Cria diretório da share
        2. Configura permissões básicas
        3. Adiciona share no smb.conf
        
        Args:
            username (str): Nome do usuário
            password (str): Senha do usuário (não usado, mantido para compatibilidade)
            home_dir (str): Diretório home (opcional)
            share_path (str): Caminho da share (opcional)
            
        Returns:
            bool: True se criado com sucesso
        """
        try:
            print(f"Criando usuário Samba '{username}'...")
            
            # 1. Verificar se usuário já existe
            if self.user_exists(username):
                print(f"Usuário '{username}' já existe no Samba!")
                return False
            
            # 2. Criar diretório da share
            share_dir = share_path or f"/home/server/hdds/main/users/{username}"
            os.makedirs(share_dir, exist_ok=True)
            
            print(f"✅ Diretório da share criado: {share_dir}")
            
            # 3. Adicionar share no smb.conf
            success = self.add_user_share(
                username=username,
                path=share_dir,
                browseable="yes",
                writable="yes",
                guest_ok="no",
                create_mask="0660",
                directory_mask="0770"
            )
            
            if success:
                print(f"✅ Share adicionada ao smb.conf")
                
                # 4. Testar e recarregar
                if self.test_config():
                    if self.reload_samba():
                        print(f"✅ Usuário '{username}' criado com sucesso no Samba!")
                        return True
                    else:
                        print("⚠️ Erro ao recarregar serviço Samba")
                else:
                    print("⚠️ Configuração inválida!")
            else:
                print(f"❌ Erro ao adicionar share no smb.conf")
            
            return False
            
        except Exception as e:
            print(f"Erro ao criar usuário '{username}': {str(e)}")
            return False

    def remove_samba_user(self, username: str, remove_home: bool = False) -> bool:
        """
        Remove usuário do Samba (apenas do smb.conf):
        1. Remove share do smb.conf
        2. Remove diretório (opcional)
        
        Args:
            username (str): Nome do usuário
            remove_home (bool): Se deve remover diretório da share
            
        Returns:
            bool: True se removido com sucesso
        """
        try:
            print(f"Removendo usuário Samba '{username}'...")
            
            # 1. Verificar se usuário existe
            if not self.user_exists(username):
                print(f"Usuário '{username}' não existe no Samba!")
                return False
            
            # 2. Remover share do smb.conf
            success = self.remove_user_share(username)
            if success:
                print(f"✅ Share removida do smb.conf")
            
            # 3. Remover diretório se solicitado
            if remove_home:
                try:
                    # Encontrar o caminho da share antes de remover
                    share_config = self.get_user_share_config(username)
                    if share_config and 'path' in share_config:
                        share_path = share_config['path']
                        if os.path.exists(share_path):
                            shutil.rmtree(share_path)
                            print(f"✅ Diretório removido: {share_path}")
                except Exception as e:
                    print(f"Aviso: Erro ao remover diretório: {str(e)}")
            
            # 4. Testar e recarregar
            if self.test_config():
                if self.reload_samba():
                    print(f"✅ Usuário '{username}' removido com sucesso do Samba!")
                    return True
                else:
                    print("⚠️ Erro ao recarregar serviço Samba")
            else:
                print("⚠️ Configuração inválida!")
            
            return False
            
        except Exception as e:
            print(f"Erro ao remover usuário '{username}': {str(e)}")
            return False

    def user_exists(self, username: str) -> bool:
        """
        Verifica se um usuário existe no arquivo smb.conf
        
        Args:
            username (str): Nome do usuário
            
        Returns:
            bool: True se o usuário existe
        """
        try:
            content = self.read_config()
            shares = self.parse_shares(content)
            
            # Verificar se existe uma share para este usuário
            for share_name, config in shares.items():
                if share_name not in ['global', 'printers', 'print$', 'homes', 'netlogon', 'profiles', 'main']:
                    if 'valid users' in config and config['valid users'] == username:
                        return True
            
            return False
        except:
            return False

    def list_samba_users(self) -> List[Dict[str, str]]:
        """
        Lista todos os usuários Samba (sistema + shares)
        
        Returns:
            List[Dict[str, str]]: Lista de usuários com informações
        """
        try:
            # Ler configuração atual
            content = self.read_config()
            
            # Parsear shares existentes
            shares = self.parse_shares(content)
            
            samba_users = []
            
            # Filtrar apenas shares de usuário (excluir [printers], [print$], [homes], etc.)
            for share_name, config in shares.items():
                if share_name not in ['global', 'printers', 'print$', 'homes', 'netlogon', 'profiles', 'main']:
                    # Verificar se é uma share de usuário
                    if 'valid users' in config:
                        username = config['valid users']
                        
                        # Verificar se usuário existe no sistema
                        user_exists = self.user_exists(username)
                        
                        samba_users.append({
                            'username': username,
                            'has_share': True,
                            'share_path': config.get('path', 'N/A'),
                            'share_name': share_name,
                            'browseable': config.get('browseable', 'N/A'),
                            'writable': config.get('writable', 'N/A'),
                            'read_only': config.get('read only', 'N/A'),
                            'create_mask': config.get('create mask', 'N/A'),
                            'directory_mask': config.get('directory mask', 'N/A')
                        })
            
            return samba_users
            
        except Exception as e:
            print(f"Erro ao listar usuários Samba: {str(e)}")
            return []

    def change_samba_password(self, username: str, new_password: str) -> bool:
        """
        Altera a senha de um usuário Samba (apenas no arquivo de configuração)
        
        Args:
            username (str): Nome do usuário
            new_password (str): Nova senha (não usado, mantido para compatibilidade)
            
        Returns:
            bool: True se alterado com sucesso
        """
        try:
            print(f"Alterando configuração do usuário '{username}'...")
            
            # Verificar se usuário existe
            if not self.user_exists(username):
                print(f"Usuário '{username}' não existe no Samba!")
                return False
            
            # Como estamos trabalhando apenas com o arquivo smb.conf,
            # não há senhas para alterar. Esta função mantém compatibilidade
            # mas não faz alterações reais.
            print(f"✅ Configuração do usuário '{username}' verificada (sem alterações de senha)")
            return True
            
        except Exception as e:
            print(f"Erro ao verificar usuário: {str(e)}")
            return False 