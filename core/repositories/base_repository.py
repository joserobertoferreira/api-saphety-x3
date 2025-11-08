from typing import Any, Generic, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, load_only

from core.database.base import Base

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

        # Adiciona filtros (WHERE)
        if filters:
            # Converte o dicionário de filtros em condições SQLAlchemy
            conditions = [getattr(self.model, key) == value for key, value in filters.items()]
            stmt = stmt.where(*conditions)

        result = session.execute(stmt)
        return list(result.scalars().all())

    def find_with_joins(  # noqa: PLR0913, PLR0917
        self,
        session: Session,
        columns: Optional[list[str]] = None,
        filters: Optional[dict[str, Any]] = None,
        joins: Optional[list[Type[ModelType]]] = None,
        order_by: Optional[list[str]] = None,
        limit: Optional[int] = None,
    ) -> list[ModelType]:
        """
        Executa uma consulta SELECT usando o ORM do SQLAlchemy.

        Args:
            session: A sessão SQLAlchemy ativa.
            model: A classe do modelo principal a ser consultada (ex: SalesInvoice).
            columns: Lista opcional de nomes de atributos a carregar.
            filters: Dicionário de filtros de igualdade.
            joins: Lista de modelos relacionados para aplicar um JOIN.
            order_by: Lista de nomes de atributos para ordenar (ex: ['-invoiceDate']).
            limit: Número máximo de registos a retornar.

        Returns:
            Uma lista de objetos do modelo ORM.
        """
        try:
            # Inicia a construção da query com a entidade principal
            stmt = select(self.model)

            # Adiciona JOINs se forem especificados
            if joins:
                for join_model in joins:
                    # O SQLAlchemy infere a condição ON a partir do relationship
                    stmt = stmt.join(join_model)

            # Adiciona filtros (WHERE)
            if filters:
                # Converte o dicionário de filtros em condições SQLAlchemy
                conditions = [getattr(self.model, key) == value for key, value in filters.items()]
                stmt = stmt.where(*conditions)

            # Adiciona ordenação (ORDER BY)
            if order_by:
                order_clauses = []
                for field in order_by:
                    if field.startswith('-'):
                        order_clauses.append(getattr(self.model, field[1:]).desc())
                    else:
                        order_clauses.append(getattr(self.model, field).asc())
                stmt = stmt.order_by(*order_clauses)

            # Adiciona limite (LIMIT / TOP)
            if limit:
                stmt = stmt.limit(limit)

            # Adiciona seleção de colunas (load_only)
            if columns:
                stmt = stmt.options(load_only(*[getattr(self.model, col) for col in columns]))

            # Executa a query
            result = session.execute(stmt)
            return list(result.scalars().all())

        except SQLAlchemyError:
            raise  # Relança a exceção para que a camada de serviço possa tratar
        except Exception:
            raise
