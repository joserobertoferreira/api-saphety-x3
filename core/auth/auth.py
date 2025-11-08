import json
import logging
from http import HTTPStatus
from typing import Any

import requests

SERVER_ERROR_CODE = 500

logger = logging.getLogger(__name__)


class Auth:
    def __init__(self, base_url: str) -> None:
        # Garante que o URL base começa com https://
        if not base_url.startswith('https://'):
            self.base_url = f'https://{base_url}'
        else:
            self.base_url = base_url

        self.headers = {'content-type': 'application/json'}

    def login(self, username: str, password: str) -> dict[str, Any]:
        """
        Tenta autenticar na API e obter um token de acesso.
        """
        service_url = f'{self.base_url}/api/Account/getToken'

        payload = {'Username': username, 'Password': password}

        logger.info(f'Tentar autenticar o utilizador {username} em {self.base_url}')

        try:
            # Serializa o objeto payload para json
            request_data = json.dumps(payload)

            # Requisição POST para obter um token
            response = requests.post(service_url, data=request_data, headers=self.headers, timeout=15)

            # Levanta uma exceção HTTPError se a resposta for um erro.
            response.raise_for_status()

            # Formata a resposta para JSON apenas para fins de visualização
            json_response = json.loads(response.text)

            logger.info('Autenticação bem-sucedida. Token recebido.')

            correlation_id = json_response.get('CorrelationId', '')
            result_data = json_response.get('Data', '')
            result_flag = json_response.get('IsValid', False)
            errors = json_response.get('Errors', [])

            return {
                'HttpStatus': HTTPStatus.OK if result_flag else HTTPStatus.UNAUTHORIZED,
                'CorrelationId': correlation_id,
                'Token': result_data,
                'Errors': errors,
            }

        except requests.exceptions.HTTPError as e:
            # Este erro é levantado pelo raise_for_status() para 4xx e 5xx
            logger.error(
                f'O pedido de login falhou com o status HTTP {e.response.status_code}. '
                f'URL: {e.request.url}. Resposta: {e.response.text}'
            )
            # Retorna um dicionário de erro consistente
            return {'HttpStatus': e.response.status_code, 'Token': None, 'Errors': [e.response.text]}

        except json.JSONDecodeError:
            # Ocorre se raise_for_status() não falhou (ex: status 200),
            # mas o corpo da resposta não é JSON.
            logger.error(
                f'A API retornou uma resposta não-JSON inesperada (Status: {response.status_code}). '
                f'Resposta: {response.text}'
            )
            return {'HttpStatus': 500, 'Token': None, 'Errors': ['Resposta inválida da API.']}

        except requests.RequestException as e:
            # Captura outros erros de rede (DNS, timeout, conexão recusada)
            logger.error(f'Erro de rede ao tentar fazer login: {e}')
            return {'HttpStatus': 503, 'Token': None, 'Errors': ['Erro de conexão com a API.']}

    def logout(self, token: str) -> int:
        service_url = f'{self.base_url}/Logout'

        headers = {'Authorization': 'Bearer ' + token}

        response = requests.get(service_url, headers=headers)

        if response.status_code < SERVER_ERROR_CODE:
            json_response = json.loads(response.text)

            return json_response['ResultCode']

        return 0
