import json
import logging

import requests
from requests.exceptions import HTTPError
from sqlalchemy.orm import Session

from core.config.settings import API_PASSWORD, API_USER, SERVER_BASE_ADDRESS
from core.database.database import db
from core.models.saphety_control import APIControlView
from core.services.authentication import AuthenticationService
from core.services.control_service import ControlService
from core.types.types import (
    ControlArgs,
    SaphetyIntegrationData,
    SaphetyIntegrationResponse,
    SaphetyIntegrationResult,
)
from core.utils.local_menus import SaphetyIntegrationStatus
from core.utils.xml_handler import XMLHandler

logger = logging.getLogger(__name__)


class SaphetyApiIntegrationService:
    """
    Um serviço para interagir com a API de integração de faturas da Saphety.
    """

    def __init__(self):
        self.base_url = f'https://{SERVER_BASE_ADDRESS}/api'
        self.xml_handler = XMLHandler()
        self.auth_service = AuthenticationService()
        self.control_service = ControlService()

    def _process_invoices(self, token: str, sent_invoices: list[APIControlView]) -> list[SaphetyIntegrationResult]:
        """Processa as faturas pendentes e retorna uma lista de resultados."""
        status_results: list[SaphetyIntegrationResult] = []

        for invoice in sent_invoices:
            status = self.integration_status(request_id=invoice.financialId, token=token)

            if status.get('IsValid'):
                logger.info(f'Fatura {invoice.invoiceNumber} verificada com sucesso. Status: {status.get("Data")}')
            else:
                logger.error(f'Erro ao verificar a fatura {invoice.invoiceNumber}: {status.get("Errors")}')

            status_results.append({'invoice_number': invoice.invoiceNumber, 'response': status})

        return status_results

    def _update_invoices(self, status_results: list[SaphetyIntegrationResult]) -> None:
        """Atualiza o estado das faturas na tabela de controlo."""

        # Obtém uma sessão da base de dados usando o nosso gestor
        with db.get_db() as session:
            try:
                for result in status_results:
                    invoice_number = result.get('invoice_number')
                    response = result.get('response')
                    data = response.get('Data', None)

                    if data is not None and isinstance(data, dict):
                        self._handle_with_dict(
                            session=session,
                            invoice_number=invoice_number,
                            request_id=response.get('CorrelationId', ''),
                            data=data,
                        )

            except Exception:
                logger.exception('Ocorreu um erro crítico durante o processamento. Fazer rollback...')
                session.rollback()  # Garante que nenhuma alteração parcial é guardada

    def _handle_with_dict(
        self, session: Session, invoice_number: str, request_id: str, data: SaphetyIntegrationData
    ) -> None:
        """Processa a resposta quando o campo 'Data' é um dicionário."""

        notification_status = data.get('NotificationStatus', None)
        integration_status = data.get('IntegrationStatus', None)

        updated_data: ControlArgs = {'invoice_number': invoice_number, 'requestId': request_id}

        if notification_status:
            updated_data['notificationStatus'] = SaphetyIntegrationStatus[notification_status.upper()]

        if integration_status:
            updated_data['integrationStatus'] = SaphetyIntegrationStatus[integration_status.upper()]

        self.control_service.mark_as_sent(session=session, context=updated_data)

    def verify_invoice_status(self, invoice_id: str | None = None) -> None:
        """
        Verifica o estado das faturas enviadas para a API da Saphety.
        Faz a leitura da tabela de controlo e verifica as faturas enviadas.
        Faz a verificação do estado das faturas enviadas.
        """

        if invoice_id and invoice_id == 'CHECK_ALL':
            invoice_id = None

        # Obtém uma sessão da base de dados usando o nosso gestor
        with db.get_db() as session:
            try:
                # Recupera as faturas enviadas da tabela de controlo
                sent_invoices = self.control_service.fetch_invoices_to_be_checked(
                    session=session, invoice_number=invoice_id
                )
            except Exception:
                logger.exception('Ocorreu um erro crítico durante o processamento. Fazer rollback...')
                if 'session' in locals():
                    session.rollback()  # Garante que nenhuma alteração parcial é guardada

        if not sent_invoices:
            logger.info('Nenhuma fatura enviada encontrada para verificação.')
            return

        # Obtém um token válido antes de verificar qualquer fatura
        token = self.auth_service.login(API_USER, API_PASSWORD)

        if not token:
            logger.error('Falha na autenticação. Não foi possível obter o token.')
            return

        # Processa cada fatura pendente
        status_results = self._process_invoices(token=token, sent_invoices=sent_invoices)

        # Atualiza o estado das faturas na tabela de controlo
        self._update_invoices(status_results=status_results)

    def integration_status(self, request_id: str, token: str) -> SaphetyIntegrationResponse:
        """
        Este método consulta o estado da integração de uma fatura enviada.

        Args:
            request_id (str): O ID de correlação retornado pela API ao enviar a fatura
            token (str): O token de autenticação para a API Saphety
        Returns:
            SaphetyIntegrationResponse: A resposta da API com o estado da integração
        """

        service_url = f'{self.base_url}/OutboundFinancialDocument/{request_id}'
        headers = {'Authorization': f'bearer {token}'}

        try:
            # Requisição GET para consultar o estado da fatura
            response = requests.get(service_url, headers=headers, timeout=15)

            # Levanta uma exceção HTTPError se a resposta for um erro.
            response.raise_for_status()

            # Formata a resposta para JSON apenas para fins de visualização
            json_response = json.loads(response.text)

            return json_response

        except HTTPError as http_err:
            logger.error(f'Erro HTTP ao consultar o estado da fatura com CorrelationId {request_id}: {http_err}')
            return {'CorrelationId': request_id, 'IsValid': False, 'Errors': [str(http_err)], 'Data': {}}
