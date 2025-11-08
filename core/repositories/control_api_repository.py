import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models.saphety_control import APIControlView
from core.utils.local_menus import SaphetyStatus

from .base_repository import GenericRepository

logger = logging.getLogger(__name__)


class ControlApiRepository(GenericRepository[APIControlView]):
    """
    Repositório para gerir as operações na tabela de controlo de faturas CIUS-PT.
    """

    def get_by_invoice_number(self, session: Session, invoice_number: str) -> Optional[APIControlView]:  # noqa: PLR6301
        """Busca um registo de controlo pelo número da fatura."""
        stmt = select(APIControlView).where(APIControlView.invoiceNumber == invoice_number)
        return session.execute(stmt).scalar_one_or_none()

    def get_invoices_by_status(  # noqa: PLR6301
        self, session: Session, status: SaphetyStatus, invoice_id: str | None = None
    ) -> list[str]:
        """
        Recupera uma lista de números de faturas com um status específico.

        Args:
            session: A sessão SQLAlchemy ativa.
            status: O código numérico do status a filtrar.
            invoice_id: O ID da fatura a ser filtrada (opcional).

        Returns:
            Uma lista de números de faturas que correspondem ao status fornecido.
        """
        stmt = select(APIControlView.invoiceNumber).where(APIControlView.status == status)

        if invoice_id:
            stmt = stmt.where(APIControlView.invoiceNumber == invoice_id)

        result = session.execute(stmt).scalars().all()
        return list(result)
