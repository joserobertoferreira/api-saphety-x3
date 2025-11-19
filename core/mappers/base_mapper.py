from pathlib import Path
from typing import TYPE_CHECKING, Any

import lxml.etree as etree  # noqa: PLR0402

from core.config.settings import NS_CAC, NS_CBC
from core.models.sales_invoice import SalesInvoice
from core.types.types import InvoiceXmlData, OrderReference
from core.utils.conversions import Conversions
from core.utils.local_menus import InvoiceOrigin, InvoiceType, TaxLevelCode

if TYPE_CHECKING:
    from core.utils.generics import Generics


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

    def save_invoice_xml(self, xml_tree: etree._Element, context: InvoiceXmlData) -> Path | None:  # noqa: PLR6301
        """
        Salva o conteúdo XML gerado em um ficheiro.

        O comportamento padrão é salvar o ficheiro no diretório atual.

        Args:
            xml_content: O conteúdo XML a ser salvo.
            context: Informações adicionais sobre a fatura para nomeação do ficheiro.
        """

        return None

    def build_invoice_line(self, parent: etree._Element, currency: str, category: int, detail: Any) -> None:  # noqa: PLR6301
        """
        Constrói a linha da fatura no XML.

        Permite customizar a construção da linha da fatura (<cac:InvoiceLine>).

        Args:
            parent: O elemento pai no XML onde a linha será adicionada.
            currency: A moeda usada na fatura.
            category: A categoria da fatura (fatura, nota de crédito, etc.).
            detail: O detalhe específico da linha da fatura.
        """

        # Bloco Principal <cac:InvoiceLine>
        if category == InvoiceType.INVOICE:
            label = ('Invoice', 'InvoicedQuantity')
        else:
            label = ('CreditNote', 'CreditedQuantity')

        line_item = etree.SubElement(parent, f'{{{NS_CAC}}}{label[0]}Line')

        # ID da Linha
        etree.SubElement(line_item, f'{{{NS_CBC}}}ID').text = str(int(detail.lineNumber / 1000))

        # Quantidade Faturada
        etree.SubElement(line_item, f'{{{NS_CBC}}}{label[1]}', unitCode='C62').text = str(
            str(Conversions.convert_value(detail.quantityInSalesUnit, precision=2))
        )

        # Valor Líquido da Linha (sem impostos)
        etree.SubElement(
            line_item, f'{{{NS_CBC}}}LineExtensionAmount', {'currencyID': currency}
        ).text = Conversions.format_monetary(detail.lineAmountExcludingTax)

        # Detalhes do Item <cac:Item>
        item = etree.SubElement(line_item, f'{{{NS_CAC}}}Item')

        etree.SubElement(item, f'{{{NS_CBC}}}Name').text = detail.productDescriptionUserLanguage.strip()

        # Imposto do Item
        tax_category = etree.SubElement(item, f'{{{NS_CAC}}}ClassifiedTaxCategory')

        # Converte o código interno para o código de categoria CIUS ('NOR', 'RED', 'INT', etc.)
        cius_code = Generics.get_enum_name(TaxLevelCode, int(detail.taxRates))

        etree.SubElement(tax_category, f'{{{NS_CBC}}}ID').text = cius_code
        etree.SubElement(tax_category, f'{{{NS_CBC}}}Percent').text = Conversions.format_monetary(detail.taxRates)

        tax_scheme = etree.SubElement(tax_category, f'{{{NS_CAC}}}TaxScheme')
        etree.SubElement(tax_scheme, f'{{{NS_CBC}}}ID').text = 'VAT'

        # Preço do Item <cac:Price>
        price = etree.SubElement(line_item, f'{{{NS_CAC}}}Price')
        etree.SubElement(
            price, f'{{{NS_CBC}}}PriceAmount', {'currencyID': currency}
        ).text = Conversions.format_monetary(detail.netPrice)
