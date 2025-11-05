import logging
import platform
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Type

import pandas as pd
import sqlalchemy as sa
import yaml

from config import settings

# Configurar logging
logger = logging.getLogger(__name__)

MULTI_PAYMENTS = 9


class Generics:
    def __init__(self):
        pass

    @staticmethod
    def check_odbc_driver(driver_name):
        """
        Verifica se o driver ODBC é suportado no sistema operacional atual.
        :param driver_name: Nome do driver ODBC a ser verificado.
        :return: None se o driver for suportado, ou uma mensagem de erro se não for.
        """
        os_name = platform.system()
        error_message = None
        supported_drivers = {'ODBC Driver 17 for SQL Server', 'ODBC Driver 18 for SQL Server'}

        if os_name == 'Windows':
            if driver_name not in supported_drivers:
                error_message = f"Driver '{driver_name}' não é suportado no Windows."
            else:
                driver_name = driver_name.replace(' ', '+')
        elif os_name == 'Linux' and driver_name not in supported_drivers:
            error_message = f"Driver '{driver_name}' não é suportado no Linux."
        elif os_name == 'Darwin' and driver_name not in supported_drivers:
            error_message = f"Driver '{driver_name}' não é suportado no macOS."
        elif os_name not in {'Windows', 'Linux', 'Darwin'}:
            error_message = f"Sistema operacional '{os_name}' não suportado."

        return error_message, driver_name

    @staticmethod
    def build_connection_string(config: dict):
        """
        Builds the database connection string.
        :param config: Dictionary with the database configuration.
        :return: Formatted connection string.
        """
        driver_name = config['DRIVER']
        # error_message, driver_name = self.check_odbc_driver(driver_name)

        # if error_message:
        #     return error_message, None

        conn_str = sa.engine.URL.create(
            drivername='mssql+pyodbc',
            host=config['SERVER'],
            database=config['DATABASE'],
            username=config.get('USERNAME'),
            password=config.get('PASSWORD'),
            query={
                'driver': driver_name,
                # 'Encrypt': config['encrypt'],
                # "TrustServerCertificate": "yes",
                # "Trusted_Connection": config.get("trusted_connection", "no") # Se usar Windows Auth
            },
        )

        logger.info(f'String de conexão criada: {conn_str}')
        return conn_str

    @staticmethod
    def load_config_yaml(file_path='emails.yaml') -> dict:
        """
        Load configuration from a YAML file.
        :param file_path: Path to the YAML file.
        :return: Dictionary with the loaded configuration.
        """
        full_path = settings.CLIENT_DIR / file_path
        if not full_path.exists():
            logger.error(f'Arquivo de configuração {file_path} não encontrado em {settings.CLIENT_DIR}.')
            return {}

        try:
            with open(full_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f'Erro ao carregar configuração de {file_path}: {e}')
            return {}

    @staticmethod
    def create_csv_file(df: pd.DataFrame, file_path: Path) -> None:
        """Create a CSV file from a DataFrame."""
        try:
            # Garante que o diretório pai do arquivo existe
            file_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(file_path, index=False, sep=';', encoding='utf-8')
            logger.info(f'CSV file created at {file_path}')
        except Exception as e:
            logger.error(f'Failed to create CSV file at {file_path}: {e}')
            raise  # Re-lança a exceção para que o chamador saiba que falhou

    @staticmethod
    def create_xlsx_file(df: pd.DataFrame, file_path: Path) -> None:
        """Create an XLSX file from a DataFrame."""
        try:
            # Garante que o diretório pai do arquivo existe
            file_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_excel(file_path, index=False, sheet_name='Diferenças', engine='openpyxl')
            logger.info(f'XLSX file created at {file_path}')
        except Exception as e:
            logger.error(f'Failed to create XLSX file at {file_path}: {e}')
            raise  # Re-lança a exceção para que o chamador saiba que falhou

    @staticmethod
    def is_api_client(data: Any) -> bool:
        """Check if the data is an instance of ApiClient."""

        # Verifica se o dado é um dicionário
        if not isinstance(data, dict):
            return False

        # Verifica se todas as chaves obrigatórias estão presentes
        required_keys = {'company_code', 'client_id', 'store', 'site', 'zone'}

        if not required_keys.issubset(data.keys()):
            return False

        # Verifica se os tipos das chaves obrigatórias estão corretos
        if (
            not isinstance(data['company_code'], str)
            or not isinstance(data['client_id'], str)
            or not isinstance(data['store'], int)
            or not isinstance(data['site'], str)
            or not isinstance(data['zone'], str)
        ):
            return False
        if not isinstance(data['store'], int):
            return False
        if 'process' in data and not isinstance(data['process'], str):
            return False

        return True

    @staticmethod
    def get_enum_name(enum_class: Type[Enum], value: int) -> Optional[str]:
        """
        Retorna o nome (name) de um membro do Enum a partir de um valor numérico.
        Funciona para qualquer Enum ou IntEnum.
        Retorna None se o valor não existir.
        """
        if not issubclass(enum_class, Enum):
            raise TypeError(f'{enum_class} não é uma subclasse de Enum')

        member = enum_class._value2member_map_.get(value)
        return member.name if member else None
