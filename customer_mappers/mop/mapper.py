from pathlib import Path
from typing import Any

from core.config.settings import DATABASE, DEBUG, INPUT_PDF_FOLDER
from core.database.database import db
from core.database.database_core import DatabaseCoreManager
from core.mappers.base_mapper import BaseMapper
from core.models.sales_invoice import SalesInvoice
from core.utils.conversions import Conversions
from core.utils.local_menus import NoYes


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

            if not DEBUG:
                # Cria uma instância do DatabaseCoreManager
                db_core = DatabaseCoreManager(db_manager=db)

                # Buscar localização do ficheiro pdf da fatura
                filters = {'PARAM_0': ('=', 'PDFFLD')}

                result = db_core.execute_query(table='ADOVAL', columns=['VALEUR_0'], where_clauses=filters)

                if not result and result.get('status') != 'success' and result.get('records', 0) == 0:
                    return None

                data_row = result['data'][0]
                pdf_folder = Path(data_row.get('VALEUR_0').strip().replace('$1$', DATABASE.get('SCHEMA')))
            else:
                pdf_folder = Path(INPUT_PDF_FOLDER)

            # Converte o ficheiro para base64
            pdf_base64 = Conversions.convert_file_to_base64(str(pdf_folder), f'{filename}.pdf')

            return {
                'schemeID': 'AIM',
                'type_code': '130',
                'description': 'INVOICE_REPRESENTATION',
                'file_name': f'{filename}.pdf',
                'pdf_base64': pdf_base64,
            }

        return None
