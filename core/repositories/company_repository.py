"""Módulo do repositório para interações com dados de empresas.

Este módulo contém a classe CompanyRepository, que abstrai todas as
operações de base de dados relacionadas com as sociedades (COMPANY).
"""

import logging
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, load_only

from core.models.address import Address
from core.models.company import Company
from core.utils.local_menus import EntityType

from .base_repository import GenericRepository

logger = logging.getLogger(__name__)


class CompanyRepository(GenericRepository[Company]):
    """
    Repositório para gerir dados de empresas.
    """

    def __init__(self):
        super().__init__(Company)

    def find_with_address(  # noqa: PLR6301
        self,
        session: Session,
        company_filters: Optional[dict[str, Any]] = None,
        address_filters: Optional[dict[str, Any]] = None,
        company_cols: Optional[list[str]] = None,
        address_cols: Optional[list[str]] = None,
    ) -> list[Company]:
        """
        Busca empresas e popula um atributo `addresses` com as suas moradas filtradas.

        Esta implementação não depende de um `relationship` pré-definido e usa
        duas queries eficientes para evitar `JOIN`s complexos e duplicação de dados.

        Args:
            session: A sessão SQLAlchemy ativa.
            company_filters: Filtros de igualdade para a tabela Company.
            address_filters: Filtros de igualdade para a tabela Address.
            company_cols: Colunas a carregar do modelo Company.
            address_cols: Colunas a carregar do modelo Address.

        Returns:
            Uma lista de objetos Company. Cada objeto terá um novo atributo `addresses`
            (uma lista) contendo os objetos Address correspondentes aos filtros.
        """

        # Busca as empresas com os filtros e colunas especificadas
        company_stmt = select(Company)

        if company_cols:
            company_stmt = company_stmt.options(load_only(*[getattr(Company, col) for col in company_cols]))

        if company_filters:
            company_stmt = company_stmt.filter_by(**company_filters)

        companies = list(session.execute(company_stmt).scalars().all())

        if not companies:
            return []  # Se não houver empresas, não há nada mais a fazer

        # Mapeia os números de entidade das empresas para os objetos Company
        entity_numbers = [company.company for company in companies]

        # Monta o where para a query de moradas
        address_conditions = [Address.entityNumber.in_(entity_numbers), Address.entityType == EntityType.COMPANY]

        if address_filters:
            for key, value in address_filters.items():
                address_conditions.append(getattr(Address, key) == value)

        # Monta a query para buscar as moradas
        address_stmt = select(Address).where(*address_conditions)

        if address_cols:
            address_stmt = address_stmt.options(load_only(*[getattr(Address, col) for col in address_cols]))

        addresses = list(session.execute(address_stmt).scalars().all())

        # Mapeia as moradas encontradas para as suas empresas correspondentes
        companies_map = {c.company: c for c in companies}

        for company in companies:
            company.addresses = []

        # Associar as moradas às empresas
        for address in addresses:
            if address.entityNumber in companies_map:
                companies_map[address.entityNumber].addresses.append(address)

        return companies
