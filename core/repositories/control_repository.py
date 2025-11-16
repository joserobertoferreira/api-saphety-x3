import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models.saphety_control import SaphetyApiControl
from core.types.types import ControlArgs

from .base_repository import GenericRepository

logger = logging.getLogger(__name__)


class ControlRepository(GenericRepository[SaphetyApiControl]):
    """
    Repositório para gerir as operações na tabela de controlo de faturas Saphety.
    """

    _FIELD_MAP = {
        'status': 'status',
        'filename': 'filename',
        'message': 'message',
        'sendDate': 'sendDate',
        'requestStatus': 'requestStatus',
        'integrationStatus': 'integrationStatus',
        'notificationStatus': 'notificationStatus',
        'financialId': 'financialId',
    }

    def get_by_invoice_number(self, session: Session, invoice_number: str) -> Optional[SaphetyApiControl]:  # noqa: PLR6301
        """Busca um registo de controlo pelo número da fatura."""
        stmt = select(SaphetyApiControl).where(SaphetyApiControl.invoiceNumber == invoice_number)
        return session.execute(stmt).scalar_one_or_none()

    def create_or_update_record(self, session: Session, data: ControlArgs) -> SaphetyApiControl:  # noqa: PLR0912
        """
        Cria um novo registo de controlo ou atualiza um existente.

        Esta função implementa uma lógica "upsert" (UPDATE or INSERT).

        Args:
            session: A sessão SQLAlchemy ativa.
            **kwargs: Os argumentos de controlo a serem registados.
              - invoice_number: O número da fatura a ser registada.
              - status: O código numérico do novo status.
              - filename: O nome do ficheiro XML gerado (opcional).
              - message: Uma mensagem opcional (ex: ID de submissão, mensagem de erro).
              - sended_at: A data de envio (opcional).

        Returns:
            O objeto CiusPTControl criado ou atualizado.
        """
        invoice_number = data.get('invoice_number')
        if not invoice_number:
            raise ValueError("Parâmetro 'invoice_number' é obrigatório.")

        logger.debug(f'Criar/atualizar registo de controlo para a fatura {invoice_number}.')

        # Unpack the control arguments
        update_data = {self._FIELD_MAP[key]: value for key, value in data.items() if key in self._FIELD_MAP}

        # Tenta encontrar um registo existente
        control_record = self.get_by_invoice_number(session, invoice_number)

        if control_record:
            # Se existe, atualiza os campos
            logger.debug('Registo existente encontrado. Atualizar.')
            for key, value in update_data.items():
                setattr(control_record, key, value)
        else:
            # Se não existe, cria um novo
            logger.debug('Nenhum registo existente. Criar novo.')
            update_data['invoiceNumber'] = invoice_number

            # Remove chaves com valor None para não sobrepor defaults do modelo
            init_data = {k: v for k, v in update_data.items() if v is not None}

            control_record = SaphetyApiControl(**init_data)
            session.add(control_record)

        return control_record
