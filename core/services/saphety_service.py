import json
import logging
from pathlib import Path

import requests
from requests.exceptions import HTTPError
from sqlalchemy.orm import Session

from core.config.settings import API_PASSWORD, API_USER, SERVER_BASE_ADDRESS
from core.database.database import db
from core.models.saphety_control import APIControlView
from core.repositories.company_repository import CompanyRepository
from core.services.authentication import AuthenticationService
from core.services.control_service import ControlService
from core.types.types import ControlArgs, SaphetyResponse, SaphetyResult
from core.utils.local_menus import InvoiceType, SaphetyRequestStatus
from core.utils.xml_handler import XMLHandler

logger = logging.getLogger(__name__)


class SaphetyApiClient:
    """
    Um cliente para interagir com a API de submissão de faturas da Saphety.
    """

    def __init__(self):
        self.base_url = SERVER_BASE_ADDRESS
        self.xml_handler = XMLHandler()
        self.auth_service = AuthenticationService()
        self.company_repo = CompanyRepository()
        self.control_service = ControlService()

    def _process_invoices(self, token: str, pending_invoices: list[APIControlView]) -> list[SaphetyResult]:
        """Processa as faturas pendentes e retorna uma lista de resultados."""
        send_results: list[SaphetyResult] = []

        for invoice in pending_invoices:
            send_status = self.send_message(invoice, token)

            # Verifica o resultado do envio
            if send_status.get('IsValid'):
                request_id = send_status.get('Data', '')

                if isinstance(request_id, list):
                    request_id = request_id[0]

                status = self.request_status(request_id=request_id, token=token)

                if status.get('IsValid'):
                    logger.info(f'Fatura {invoice.invoiceNumber} enviada com sucesso. RequestId: {request_id}')
                else:
                    logger.error(f'Erro ao processar a fatura {invoice.invoiceNumber}: {status.get("Errors")}')

                send_results.append({'invoice_number': invoice.invoiceNumber, 'response': status})
            else:
                logger.error(f'Erro ao enviar a fatura {invoice.invoiceNumber}: {send_status.get("Errors")}')
                send_results.append({'invoice_number': invoice.invoiceNumber, 'response': send_status})

        return send_results

    def _update_invoices(self, send_results: list[SaphetyResult]) -> None:
        """Atualiza o estado das faturas na tabela de controlo."""

        # Obtém uma sessão da base de dados usando o nosso gestor
        with db.get_db() as session:
            try:
                for result in send_results:
                    invoice_number = result.get('invoice_number')
                    response = result.get('response')
                    data = response.get('Data', None)

                    if isinstance(data, dict):
                        self._handle_with_dict(session=session, invoice_number=invoice_number, data=data)
                    elif isinstance(data, str):
                        self._handle_with_string(
                            session=session, invoice_number=invoice_number, data=data, response=response
                        )

                session.commit()
            except Exception:
                logger.exception('Ocorreu um erro crítico durante o processamento. Fazer rollback...')
                session.rollback()  # Garante que nenhuma alteração parcial é guardada

    def _handle_with_dict(self, session: Session, invoice_number: str, data: dict) -> None:
        """Processa a resposta quando o campo 'Data' é um dicionário."""
        async_status = data.get('AsyncStatus', None)

        if async_status in {'Queued', 'Running', 'Error', 'Finished'}:
            api_status = SaphetyRequestStatus[async_status.upper()]

            updated_data: ControlArgs = {'invoice_number': invoice_number}

            if api_status == SaphetyRequestStatus.FINISHED:
                updated_data['requestStatus'] = api_status
                updated_data['requestId'] = data.get('CorrelationId', '')
                updated_data['financialId'] = data.get('OutboundFinancialDocumentId', '')
            elif api_status == SaphetyRequestStatus.ERROR:
                errors = data.get('Errors', [])

                updated_data['requestStatus'] = api_status
                updated_data['requestId'] = data.get('CorrelationId', '')
                updated_data['message'] = ', '.join(errors)[:250]
            else:
                updated_data['requestStatus'] = api_status
                updated_data['requestId'] = data.get('CorrelationId', '')

            if async_status == 'Error':
                self.control_service.log_sending_error(session=session, context=updated_data)
            else:
                self.control_service.mark_as_sent(session=session, context=updated_data)

    def _handle_with_string(self, session: Session, invoice_number: str, data: str, response: SaphetyResponse) -> None:
        """Processa a resposta quando o campo 'Data' é uma string."""
        errors = response.get('Errors', [])

        if errors:
            updated_data: ControlArgs = {
                'invoice_number': invoice_number,
                'requestStatus': SaphetyRequestStatus.ERROR,
                'message': ', '.join(errors)[:250],
            }
            self.control_service.log_sending_error(session=session, context=updated_data)
        else:
            updated_data: ControlArgs = {
                'invoice_number': invoice_number,
                'requestStatus': SaphetyRequestStatus.QUEUED,
            }
            self.control_service.mark_as_sent(session=session, context=updated_data)

    def send_pending_invoices(self, invoice_id: str | None = None) -> None:
        """
        Envia faturas pendentes para a API da Saphety.
        Faz a leitura da tabela de controlo e verifica as faturas pendentes de envio.
        Faz a verificação dos ficheiros xmls pendentes e envia-os.

        Args:
            invoice_id (str | None, optional): O ID da fatura a ser enviada. Defaults to None.
        """

        # Obtém uma sessão da base de dados usando o nosso gestor
        with db.get_db() as session:
            try:
                # Recupera as faturas pendentes da tabela de controlo
                pending_invoices = self.control_service.get_pending_invoices(session=session, invoice_number=invoice_id)
            except Exception:
                logger.exception('Ocorreu um erro crítico durante o processamento. Fazer rollback...')
                if 'session' in locals():
                    session.rollback()  # Garante que nenhuma alteração parcial é guardada

        # Obtém um token válido antes de enviar qualquer fatura
        token = self.auth_service.login(API_USER, API_PASSWORD)

        if not token:
            logger.error('Falha na autenticação. Não foi possível obter o token.')
            return

        # Processa cada fatura pendente
        send_results = self._process_invoices(token=token, pending_invoices=pending_invoices)

        # Atualiza o estado das faturas na tabela de controlo
        self._update_invoices(send_results=send_results)

    def send_message(self, invoice: APIControlView, token: str) -> SaphetyResponse:
        """
        Este método recebe uma fatura a ser enviada.

        Args:
            invoice (APIControlView): A fatura a ser enviada
            token (str): O token de autenticação para a API Saphety
        """

        # Verifica se o ficheiro XML existe
        xml_file_path = Path(invoice.filename)

        try:
            with open(xml_file_path, 'rb') as xml_file:
                request_data = xml_file.read()

            # Monta os dados para envio
            document_type = 'Invoice' if invoice.category == InvoiceType.INVOICE else 'Credit_Note'
            service_url = (
                f'https://{self.base_url}/api/CountryFormatAsyncRequest/processDocument/'
                + f'{invoice.sender}/{document_type}/PT'
            )
            headers = {'Content-Type': 'application/xml', 'Authorization': f'bearer {token}'}

            # Requisição POST para enviar o ficheiro XML
            response = requests.post(service_url, data=request_data, headers=headers, timeout=15)

            # Levanta uma exceção HTTPError se a resposta for um erro.
            response.raise_for_status()

            # Formata a resposta para JSON apenas para fins de visualização
            json_response = json.loads(response.text)

            return json_response

        except FileNotFoundError:
            logger.info(f'Erro: O ficheiro XML não foi encontrado em {xml_file_path}')
            return {'CorrelationId': '', 'IsValid': False, 'Errors': ['Ficheiro XML não encontrado.'], 'Data': ''}
        except HTTPError as http_err:
            logger.error(f'Erro HTTP ao enviar a fatura {invoice.invoiceNumber}: {http_err}')
            return {'CorrelationId': '', 'IsValid': False, 'Errors': [str(http_err)], 'Data': ''}

    def request_status(self, request_id: str, token: str) -> SaphetyResponse:
        """
        Este método consulta o estado do processamento de uma fatura enviada.

        Args:
            request_id (str): O ID de correlação retornado pela API ao enviar a fatura
            token (str): O token de autenticação para a API Saphety
        """

        service_url = f'https://{self.base_url}/api/CountryFormatAsyncRequest/{request_id}'
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
            return {'CorrelationId': request_id, 'IsValid': False, 'Errors': [str(http_err)], 'Data': ''}
