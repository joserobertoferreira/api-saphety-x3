"""Módulo do repositório para interações com dados de endereços.

Este módulo contém a classe AddressRepository, que abstrai todas as
operações de base de dados relacionadas com as moradas (BPADDRESS).
"""

import logging

from core.models.address import Address

from .base_repository import GenericRepository

logger = logging.getLogger(__name__)


class AddressRepository(GenericRepository[Address]):
    """
    Repositório para gerir dados de moradas.
    """

    def __init__(self):
        super().__init__(Address)
