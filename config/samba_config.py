"""
Configuração para o Samba Service
Especifica o caminho do arquivo smb.conf para diferentes ambientes
"""

import os

class SambaConfig:
    """Configuração para o Samba Service"""
    
    # Caminho padrão do arquivo smb.conf
    DEFAULT_SMB_CONF_PATH = "/etc/samba/smb.conf"
    
    # Configurações por ambiente
    ENVIRONMENTS = {
        "development": {
            "smb_conf_path": "/etc/samba/smb.conf",
            "backup_dir": "/tmp/samba_backups"
        },
        "production": {
            "smb_conf_path": "/etc/samba/smb.conf",
            "backup_dir": "./backups/samba"
        },
        "testing": {
            "smb_conf_path": "/tmp/test_smb.conf",
            "backup_dir": "/tmp/samba_test_backups"
        }
    }
    
    @classmethod
    def get_smb_conf_path(cls, environment="production"):
        """Retorna o caminho do arquivo smb.conf para o ambiente especificado"""
        return cls.ENVIRONMENTS.get(environment, cls.ENVIRONMENTS["production"])["smb_conf_path"]
    
    @classmethod
    def get_backup_dir(cls, environment="production"):
        """Retorna o diretório de backup para o ambiente especificado"""
        return cls.ENVIRONMENTS.get(environment, cls.ENVIRONMENTS["production"])["backup_dir"]
    
    @classmethod
    def get_environment_config(cls, environment="production"):
        """Retorna toda a configuração para o ambiente especificado"""
        return cls.ENVIRONMENTS.get(environment, cls.ENVIRONMENTS["production"])
    
    @classmethod
    def list_environments(cls):
        """Lista todos os ambientes disponíveis"""
        return list(cls.ENVIRONMENTS.keys()) 