from pathlib import Path
from typing import Any

import lxml.etree as etree  # noqa: PLR0402

from core.config.settings import DATABASE, INPUT_PDF_FOLDER, NS_CAC, NS_CBC, OUTPUT_FOLDER, PRODUCTION
from core.database.database import db
from core.database.database_core import DatabaseCoreManager
from core.mappers.base_mapper import BaseMapper
from core.models.sales_invoice import SalesInvoice
from core.types.types import InvoiceXmlData
from core.utils.conversions import Conversions
from core.utils.generics import Generics
from core.utils.local_menus import InvoiceType, NoYes, TaxLevelCode
from core.utils.xml_handler import XMLHandler


class MopMapper(BaseMapper):
    """
    Classe para mapeamento específico do cliente MOP.

    Esta classe herda de BaseMapper e pode sobrescrever métodos para
    adaptar o mapeamento às necessidades específicas do cliente MOP.
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

        if invoice.customerReference and invoice.customerReference.strip():
            return invoice.customerReference.strip()

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

        if invoice.customer.generatePDF == NoYes.YES:
            # match invoice.invoiceType:
            #     case InvoiceType.INVOICE:
            #         scheme_id = 'IV'
            #     case InvoiceType.CREDIT_NOTE:
            #         scheme_id = 'CD'
            #     case _:
            #         scheme_id = 'AIM'

            filename = ''.join(c for c in invoice.invoiceNumber if c.isalnum())
            filename = f'{invoice.billToCustomer}_{filename}'

            if not PRODUCTION:
                # Cria uma instância do DatabaseCoreManager
                db_core = DatabaseCoreManager(db_manager=db)

                # Buscar localização do ficheiro pdf da fatura
                filters = {'PARAM_0': ('=', 'PDFFLD')}

                result = db_core.execute_query(table='ADOVAL', columns=['VALEUR_0'], where_clauses=filters)

                if not result and result.get('status') != 'success' and result.get('records', 0) == 0:
                    return None

                data_row = result['data'][0]
                folder = Path(data_row.get('VALEUR_0').strip().replace('$1$', DATABASE.get('SCHEMA')))
            else:
                folder = Path(INPUT_PDF_FOLDER)

            pdf_folder = Path(
                f'{folder}/{invoice.company}/{invoice.salesSite}/{invoice.invoiceDate.year}/'
                f'{invoice.invoiceDate.month}/{invoice.invoiceDate.day}'
            )

            # Verifica se o ficheiro existe
            if not pdf_folder.joinpath(f'{filename}.pdf').is_file():
                return None

            # Converte o ficheiro para base64
            pdf_base64 = Conversions.convert_file_to_base64(str(pdf_folder), f'{filename}.pdf')

            description = (
                'INVOICE_REPRESENTATION' if invoice.category == InvoiceType.INVOICE else 'CREDITNOTE_REPRESENTATION'
            )

            return {
                'schemeID': 'AIM',
                'type_code': '130',
                'description': description,
                'file_name': f'{filename}.pdf',
                'pdf_base64': pdf_base64,
            }

        return None

    def save_invoice_xml(self, xml_tree: etree._Element, context: InvoiceXmlData) -> Path | None:  # noqa: PLR6301
        """
        Salva o XML da fatura na pasta de saída usando o XMLHandler.

        Args:
            xml_tree: A árvore de elementos lxml a ser guardada.
            context: Dados adicionais da fatura para determinar o caminho de salvamento.

        Returns:
            O caminho (Path object) para o ficheiro que foi criado.
        """

        invoice_number = context.get('invoice_number')
        company = context.get('company')
        site = context.get('site')
        invoice_date = context.get('invoice_date')

        if not PRODUCTION:
            # Cria uma instância do DatabaseCoreManager
            db_core = DatabaseCoreManager(db_manager=db)

            # Buscar localização do ficheiro pdf da fatura
            filters = {'PARAM_0': ('=', 'XMLFLD')}

            result = db_core.execute_query(table='ADOVAL', columns=['VALEUR_0'], where_clauses=filters)

            if not result and result.get('status') != 'success' and result.get('records', 0) == 0:
                return None

            data_row = result['data'][0]
            folder = Path(data_row.get('VALEUR_0').strip().replace('$1$', DATABASE.get('SCHEMA')))
        else:
            folder = Path(OUTPUT_FOLDER)

        xml_folder = Path(f'{folder}/{company}/{site}/{invoice_date.year}/{invoice_date.month}/{invoice_date.day}')

        # Verifica se a pasta existe, se não existir cria
        xml_folder.mkdir(parents=True, exist_ok=True)

        # Define o nome do ficheiro XML
        filename = ''.join(c for c in invoice_number if c.isalnum()) + '.xml'

        # Salva o XML usando o XMLHandler
        xml_file = XMLHandler.save_xml_to_file(xml_tree, file_path=xml_folder, filename=filename)

        return xml_file

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

        etree.SubElement(item, f'{{{NS_CBC}}}Name').text = detail.itemDescription.strip()

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
