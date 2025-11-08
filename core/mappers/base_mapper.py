from typing import Any

from core.models.sales_invoice import SalesInvoice
from core.types.types import OrderReference
from core.utils.local_menus import InvoiceOrigin


class BaseMapper:
    """
    Classe base para mapeamentos específicos de clientes.

    Define a "interface" de quais pontos do processo podem ser customizados.
    Cada cliente terá a sua própria implementação desta classe.
    """

    def get_buyer_reference(self, invoice: SalesInvoice) -> str | None:  # noqa: PLR6301
        """
        Retorna a Referência do Cliente (BT-10) a ser usada no XML.

        O comportamento padrão é não retornar nenhuma referência, pois este
        campo é opcional na norma base.

        Args:
            invoice: O objeto SalesInvoice principal.

        Returns:
            A string da referência do cliente, ou None se não aplicável.
        """
        return None

    def get_order_reference(self, invoice: SalesInvoice) -> OrderReference | None:  # noqa: PLR6301
        """
        Retorna a referência do pedido a ser usada para uma linha da fatura.

        O comportamento padrão é simplesmente retornar a referência do pedido.
        Classes filhas podem sobrepor este método para implementar lógicas customizadas.

        Args:
            invoice: O objeto SalesInvoice principal.

        Returns:
            Um dicionário com 'order_number' e 'order_date', ou None se não aplicável.
        """

        if invoice.sourceDocumentCategory == InvoiceOrigin.ORDER:
            return {'order_number': invoice.sourceDocumentNumber, 'order_date': invoice.sourceDocumentDate}

        return None

    def get_additional_document_reference(self, invoice: SalesInvoice) -> dict[str, Any] | None:  # noqa: PLR6301
        """
        Retorna a Referência de Documento Adicional (BT-23) a ser usada no XML.

        Para o cliente MOP, este campo deve ser preenchido com o valor
        do campo "Order Number" da fatura, se disponível.

        Args:
            invoice: O objeto SalesInvoice principal.
        Returns:
            Um dicionário com 'schemeID' e 'value', ou None se não aplicável.
        """

        return None
