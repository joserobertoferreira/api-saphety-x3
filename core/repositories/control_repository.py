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

    def get_by_invoice_number(self, session: Session, invoice_number: str) -> Optional[SaphetyApiControl]:  # noqa: PLR6301
        """Busca um registo de controlo pelo número da fatura."""
        stmt = select(SaphetyApiControl).where(SaphetyApiControl.invoiceNumber == invoice_number)
        return session.execute(stmt).scalar_one_or_none()

    def create_or_update_record(self, session: Session, data: ControlArgs) -> SaphetyApiControl:
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
        update_data = {}

        if 'status' in data:
            update_data['status'] = data.get('status')
        if 'filename' in data:
            update_data['filename'] = data.get('filename')
        if 'message' in data:
            update_data['message'] = data.get('message')
        if 'sended_at' in data:
            update_data['sendDate'] = data.get('sended_at')
        if 'requestStatus' in data:
            update_data['requestStatus'] = data.get('requestStatus')
        if 'requestStatus' in data:
            update_data['requestStatus'] = data.get('requestStatus')
        if 'integrationStatus' in data:
            update_data['integrationStatus'] = data.get('integrationStatus')
        if 'notificationStatus' in data:
            update_data['notificationStatus'] = data.get('notificationStatus')
        if 'financialId' in data:
            update_data['financialId'] = data.get('financialId')

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
            control_record = SaphetyApiControl(**update_data)
            session.add(control_record)

        return control_record
