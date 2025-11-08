import logging
from http import HTTPStatus

from core.auth.auth import Auth
from core.config import settings

logger = logging.getLogger(__name__)


class AuthenticationService:
    def __init__(self):
        self.auth = Auth(settings.SERVER_BASE_ADDRESS)

    def login(self, username: str, password: str) -> str | None:
        """Este endpoint é usado para obter um token de autenticação necessário para acessar a
        API da Saphety Invoice Network.

        Tokens obtidos através deste endpoint são válidos por 1 hora e devem ser incluídos em solicitações
        subsequentes à API como um cabeçalho de autorização (Authorization: Bearer <access_token>).

            Args:
                username (str): O nome de usuário para autenticação.
                password (str): A senha para autenticação.

            Returns:
                str | None: O token de autenticação ou uma mensagem de erro.
        """
        login_data = self.auth.login(username, password)

        # Verifica se o login foi bem-sucedido E se o token não é nulo/vazio
        if login_data.get('HttpStatus') == HTTPStatus.OK:
            return login_data.get('Token')

        return None

    def logout(self, token: str) -> None:
        self.auth.logout(token)
