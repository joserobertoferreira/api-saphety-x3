import logging
import urllib.parse
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from config.settings import DATABASE
from database.base import Base

logger = logging.getLogger(__name__)


class DatabaseHandler:
    _engine = None
    _SessionLocal = None  # Fábrica de sessões

    def __init__(self):
        if DatabaseHandler._engine is None:
            self.driver = DATABASE.get('DRIVER', 'ODBC Driver 17 for SQL Server')
            self.server = DATABASE.get('SERVER', 'localhost')
            self.database = DATABASE.get('DATABASE', 'my_database')
            self.schema = DATABASE.get('SCHEMA', 'dbo')
            self.username = DATABASE.get('USERNAME', 'sa')
            self.password = DATABASE.get('PASSWORD', 'password')
            self.trusted_connection = DATABASE.get('TRUSTED_CONNECTION', 'no')

            try:
                if self.trusted_connection == 'yes':
                    params = urllib.parse.quote_plus(
                        f'DRIVER={{{self.driver}}};SERVER={self.server};DATABASE={self.database};Trusted_Connection=yes;'
                    )
                else:
                    params = urllib.parse.quote_plus(
                        f'DRIVER={{{self.driver}}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password};'
                    )
                engine_url = f'mssql+pyodbc:///?odbc_connect={params}'
                DatabaseHandler._engine = create_engine(engine_url, echo=False)  # echo=True para debug SQL

                Base.metadata.reflect(bind=DatabaseHandler._engine)

                DatabaseHandler._SessionLocal = sessionmaker(
                    autocommit=False, autoflush=False, bind=DatabaseHandler._engine
                )
                logger.info('Motor de banco de dados e fábrica de sessão inicializados.')

                # Teste de conexão simples
                with self.get_db() as db:
                    db.execute(text('SELECT 1'))
                logger.info('Conexão com o banco de dados testada com sucesso.')

            except Exception as e:
                logger.exception(f'Falha ao inicializar o motor do banco de dados: {e}')
                DatabaseHandler._engine = None  # Garante que não será usado se falhar
                raise  # Re-levanta a exceção para que a aplicação saiba do problema

    @contextmanager
    def get_db(self):  # noqa: PLR6301
        """Fornece uma sessão de banco de dados."""
        if DatabaseHandler._SessionLocal is None:
            logger.error('Fábrica de sessão não inicializada. Chame __init__ primeiro.')
            raise RuntimeError('Fábrica de sessão não inicializada.')

        db = DatabaseHandler._SessionLocal()
        try:
            yield db
        finally:
            db.close()
