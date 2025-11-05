from typing import Any, Generic, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session, load_only

from database.base import Base

ModelType = TypeVar('ModelType', bound=Base)


class GenericRepository(Generic[ModelType]):
    """Fornece uma implementação base para operações de acesso a dados (CRUD).

    Esta classe implementa métodos genéricos para Criar, Ler, Atualizar e Deletar
    (CRUD) que podem ser reutilizados por qualquer repositório específico. O objetivo
    é centralizar a lógica comum de interação com a base de dados, seguindo o
    princípio DRY (Don't Repeat Yourself).

    Repositórios específicos para um modelo (ex: `SalesInvoiceRepository`) devem
    herdar desta classe para obter as funcionalidades CRUD básicas e, adicionalmente,
    implementar métodos para queries de negócio complexas e especializadas.

    Atributos:
        model: A classe do modelo SQLAlchemy (ex: `SalesInvoice`) com a qual
               o repositório irá trabalhar.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Inicializa o repositório genérico.

        Args:
            model: A classe do modelo SQLAlchemy com a qual este repositório irá trabalhar.
        """
        self.model = model

    def get_by_id(self, session: Session, id: Any) -> Optional[ModelType]:
        """
        Busca um único registo pela sua chave primária.

        Assume que a chave primária se chama 'id'. Adapte se for diferente.
        """
        # O método session.get é otimizado para busca por PK.
        return session.get(self.model, id)

    def find_all(self, session: Session) -> list[ModelType]:
        """
        Busca todos os registos de um modelo.
        """
        stmt = select(self.model)
        result = session.execute(stmt)
        return list(result.scalars().all())

    def find(
        self,
        session: Session,
        filters: Optional[dict[str, Any]] = None,
        columns_to_load: Optional[list[str]] = None,
    ) -> list[ModelType]:
        """
        Método de busca genérico com filtros e seleção de colunas.

        Este método é ideal para queries simples com filtros de igualdade (ex: WHERE id=5 AND status='A').
        Para JOINs ou filtros complexos (ex: LIKE, IN, <, >), um método
        especializado no repositório filho é recomendado.

        Args:
            session: A sessão SQLAlchemy ativa.
            filters: Dicionário de filtros a serem aplicados com `filter_by` (igualdade).
                     Ex: {'company': 'C01', 'status': 1}
            columns_to_load: Lista opcional de nomes de atributos a carregar.
                             Se None, carrega todas as colunas.

        Returns:
            Uma lista de objetos do modelo correspondentes aos critérios.
        """
        stmt = select(self.model)

        if columns_to_load:
            # Converte a lista de strings para uma lista de objetos de coluna
            column_objects = [getattr(self.model, col_name) for col_name in columns_to_load]
            stmt = stmt.options(load_only(*column_objects))

        if filters:
            # filter_by aplica condições de igualdade (coluna = valor)
            stmt = stmt.filter_by(**filters)

        result = session.execute(stmt)
        return list(result.scalars().all())
