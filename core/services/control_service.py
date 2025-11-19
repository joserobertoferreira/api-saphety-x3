import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from core.models.saphety_control import APIControlView, SaphetyApiControl
from core.repositories.control_api_repository import ControlApiRepository
from core.repositories.control_repository import ControlRepository
from core.types.types import ControlArgs
from core.utils.local_menus import SaphetyIntegrationStatus, SaphetyRequestStatus, SaphetyStatus

logger = logging.getLogger(__name__)


class ControlService:
    """
    Serviço dedicado a gerir o estado das faturas na tabela de controlo.
    """

    def __init__(self):
        self.control_repo = ControlRepository(SaphetyApiControl)
        self.api_repo = ControlApiRepository(APIControlView)

    def _update_record(self, session: Session, data: ControlArgs):
        """
        Método auxiliar central que cria ou atualiza um registo de controlo.

        Args:
            session: A sessão SQLAlchemy ativa.
            data: Os dados a serem atualizados.
        """
        self.control_repo.create_or_update_record(session=session, data=data)

    def mark_as_generated(self, session: Session, invoice_number: str, file_path: str):
        """Regista que o XML de uma fatura foi gerado com sucesso."""
        logger.info(f"Marcar a fatura {invoice_number} como 'XML Gerado'.")

        self._update_record(
            session=session,
            data={
                'invoice_number': invoice_number,
                'status': SaphetyStatus.WAITING,
                'filename': file_path,
                'message': 'Ficheiro XML gerado',
            },
        )

    def log_processing_error(self, session: Session, invoice_number: str, error: Exception | str):
        """Regista um erro ocorrido durante o processamento de uma fatura."""
        logger.error(f'Registar erro de processamento para a fatura {invoice_number}.')

        self._update_record(
            session=session,
            data={
                'invoice_number': invoice_number,
                'status': SaphetyStatus.GENERATION_ERROR,
                'message': str(error)[:250],
            },
        )

    def mark_as_sent(self, session: Session, context: ControlArgs):
        """Regista que uma fatura foi enviada com sucesso para a API."""

        context['status'] = SaphetyStatus.SENT_SUCCESSFULLY
        context['message'] = 'Enviado com sucesso'
        context['sendDate'] = datetime.now(timezone.utc).date()

        self._update_record(session=session, data=context)

    def log_sending_error(self, session: Session, context: ControlArgs):
        """Regista um erro retornado pela API durante o envio."""

        context['status'] = SaphetyStatus.SENT_ERROR
        context['sendDate'] = datetime.now(timezone.utc).date()

        self._update_record(session=session, data=context)

    def update_integration_status(self, session: Session, context: ControlArgs):
        """Atualiza o estado de integração de uma fatura."""
        self._update_record(session=session, data=context)

    def get_pending_invoices(self, session: Session, invoice_number: str | None = None) -> list[APIControlView]:
        """Recupera a lista de faturas pendentes de envio."""
        filters: dict[str, tuple[str, Any]] = {'status': ('=', SaphetyStatus.WAITING)}

        if invoice_number:
            filters['invoiceNumber'] = ('=', invoice_number)

        results = self.api_repo.find(session=session, where_clauses=filters)

        return results

    def fetch_invoices_by_status(
        self, session: Session, status: SaphetyRequestStatus, invoice_number: str | None = None
    ) -> list[APIControlView]:
        """Recupera a lista de faturas por status."""

        filters: dict[str, tuple[str, Any]] = {'requestStatus': ('=', status)}

        if invoice_number is not None:
            filters['invoiceNumber'] = ('=', invoice_number)

        results = self.api_repo.find(session=session, where_clauses=filters)

        return results

    def fetch_invoices_to_be_checked(self, session: Session, invoice_number: str | None = None) -> list[APIControlView]:
        """Recupera a lista de faturas que precisam ter o status verificado."""

        filters: dict[str, tuple[str, Any]] = {
            'requestStatus': ('=', SaphetyRequestStatus.FINISHED),
            'integrationStatus': ('!=', SaphetyIntegrationStatus.RECEIVED),
        }

        if invoice_number is not None:
            filters['invoiceNumber'] = ('=', invoice_number)

        results = self.api_repo.find(session=session, where_clauses=filters)

        return results
