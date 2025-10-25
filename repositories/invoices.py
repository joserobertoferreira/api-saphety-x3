import datetime
import logging
from decimal import ROUND_FLOOR, ROUND_HALF_UP, Decimal
from typing import Any, Optional

from sqlalchemy import and_, text
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, select

from config.settings import DATABASE, DEFAULT_LEGACY_DATETIME
from database.database import db
from database.database_core import DatabaseCoreManager

logger = logging.getLogger(__name__)

TIP_CODE = -995
ERROR_CODE = 3


class SalesInvoiceRepository:
    """
    Repository for managing sales invoice data.
    This class provides methods to interact with the sales invoice data.
    """

    def __init__(self):
        self.db = db

    def fetch_pending_invoices(self, company: str, document: str, serie: str, sequence: int) -> bool:
        """
        Search an invoice header by its X3 index.
        Args:
            company (str): The company code.
            document (str): The document type.
            serie (str): The series of the document.
            sequence (int): The sequence number of the document.
        Returns:
            Optional[bool]: Returns True if the invoice header exists, otherwise False.
        """
        invoice_number = f'{document}-{company}-{serie}/{sequence:06d}'

        result = False

        with self.db.get_db() as session:
            stmt = select(func.count()).where(ApiInvoiceHeader.reference == invoice_number)
            records = session.scalar(stmt)

        if records is not None:
            result = records > 0
        else:
            result = False

        return result

    def get_invoice_date(self, invoice_number: str) -> datetime.datetime:
        """
        Retrieve the invoice date based on the invoice number.

        Args:
            invoice_number (str): The invoice number in the format 'docType-company-serie/sequence'.

        Returns:
            datetime.datetime: The date of the invoice if found, otherwise a default date.
        """
        try:
            db_core = DatabaseCoreManager(db_manager=self.db)
        except Exception as e:
            logger.error(f'Failed to initialize DatabaseCoreManager: {e}')
            return DEFAULT_LEGACY_DATETIME

        schema = str(DATABASE.get('SCHEMA', None))

        result = db_core.execute_query(
            table=f'{schema + "." if schema else ""}SINVOICE',
            columns=['ACCDAT_0'],
            where_clauses={'NUM_0': ('=', invoice_number)},
        )

        if result.get('records', 0) > 0 and result.get('data'):
            accounting_date = result['data'][0].get('ACCDAT_0')

            if accounting_date:
                if isinstance(accounting_date, str):
                    return datetime.datetime.strptime(accounting_date, '%Y-%m-%d')
                else:
                    return accounting_date

        return DEFAULT_LEGACY_DATETIME

    def get_customer_info(
        self, customer_code: str, name: Optional[str] = None, vat_number: Optional[str] = None
    ) -> dict[str, str]:
        """
        Retrieve customer information based on the customer code.

        Args:
            customer_code (str): The code of the customer.
            name (Optional[str]): The name of the customer.
            vat_number (Optional[str]): The VAT number of the customer.

        Returns:
            dict: A dictionary containing customer information.
        """
        db_core = DatabaseCoreManager(db_manager=self.db)

        customer_info = {}

        if not db_core:
            logger.error('Database core manager is not initialized.')
            return customer_info

        schema = str(DATABASE.get('SCHEMA', ''))

        tabela_customer = f'{schema}.BPCUSTOMER'
        tabela_partner = f'{schema}.BPARTNER'

        result = db_core.execute_query(
            table=tabela_customer,
            columns=['BPCUSTOMER.BPAADD_0', 'BPCUSTOMER.BPCNAM_0', 'BPARTNER.EECNUM_0'],
            where_clauses={'BPCNUM_0': ('=', customer_code)},
            joins=[('INNER', tabela_partner, 'BPCNUM_0', 'BPRNUM_0')],
        )

        if result['records'] > 0:
            _return = result['data'][0]

            customer_info['address_code'] = _return.get('BPAADD_0', '').strip()
            customer_vat = _return.get('EECNUM_0', '').strip()

            if name is None or len(name) == 0:
                customer_info['customer_name'] = _return.get('BPCNAM_0', '').strip()
            else:
                customer_info['customer_name'] = name.strip() if name is not None else ''

            customer_info['company_name'] = customer_info['customer_name'][:35].strip()
            customer_info['company_name_comp'] = customer_info['customer_name'][35:].strip()

            result = db_core.execute_query(
                table='BPADDRESS' if len(schema) == 0 else f'{schema}.BPADDRESS',
                columns=['BPAADDLIG_0', 'BPAADDLIG_1', 'BPAADDLIG_2', 'POSCOD_0', 'CTY_0', 'CRY_0'],
                limit=1,
                where_clauses={
                    'BPATYP_0': ('=', 1),
                    'BPANUM_0': ('=', customer_code),
                    'BPAADDFLG_0': ('=', 2),
                },
            )

            if result['records'] > 0:
                _return = result['data'][0]

                customer_info['address_lines'] = [
                    _return.get('BPAADDLIG_0', '').strip(),
                    _return.get('BPAADDLIG_1', '').strip(),
                    _return.get('BPAADDLIG_2', '').strip(),
                ]
                customer_info['postal_code'] = _return.get('POSCOD_0', '').strip()
                customer_info['city'] = _return.get('CTY_0', '').strip()
                customer_info['country'] = _return.get('CRY_0', 'PT').strip()

            if customer_info['country']:
                result = db_core.execute_query(
                    table='TABCOUNTRY' if len(schema) == 0 else f'{schema}.TABCOUNTRY',
                    columns=['CUR_0'],
                    where_clauses={'CRY_0': ('=', customer_info['country'])},
                )

                _return = result['data'][0]

                customer_info['currency'] = _return.get('CUR_0', 'EUR').strip()

            if customer_vat is not None and len(customer_vat) > 0:
                customer_info['customer_vat_number'] = customer_vat
            elif vat_number is None or len(vat_number) == 0 or vat_number in {'------', 'Consumidor final'}:
                customer_info['customer_vat_number'] = 'PT999999990'
            else:
                customer_info['customer_vat_number'] = 'PT' + vat_number.strip()

        return customer_info

    def get_documents_with_errors(self, company: str) -> list[ApiInvoiceHeader]:
        """Get documents with errors for a specific company.

        Args:
            company (str): The company code.

        Returns:
            list[ApiInvoiceHeader]: A list of documents with errors.
        """
        with self.db.get_db() as session:
            stmt = select(ApiInvoiceHeader).where(
                and_(
                    ApiInvoiceHeader.company == company.strip(),
                    ApiInvoiceHeader.is_processed == ERROR_CODE,
                )
            )
            result = session.execute(stmt)

            # Process the result as needed
            result_list = list(result.scalars().all())

        return result_list


class ApiInvoiceDetailRepository:
    """
    Repository for managing API invoice detail data.
    This class provides methods to interact with the API invoice detail data.
    """

    def __init__(self):
        self.db = db

    def search_by_x3_index_line(self, document: str, line: int) -> bool:
        """
        Search an invoice header by its X3 index.
        Args:
            company (str): The company code.
            document (str): The document type.
            serie (str): The series of the document.
            sequence (int): The sequence number of the document.
            line (int): The line number of the document.
        Returns:
            Optional[bool]: Returns True if the invoice header exists, otherwise False.
        """
        result = False

        with self.db.get_db() as session:
            stmt = select(func.count()).where(ApiInvoiceDetail.reference == document, ApiInvoiceDetail.line == line)
            records = session.scalar(stmt)

        if records is not None:
            result = records > 0
        else:
            result = False

        return result

    @staticmethod
    def create_invoice_detail(db: Session, control_data: ApiInvoiceDetail) -> None:
        """Create a new invoice detail in the database."""

        db.add(control_data)
        db.flush()
        db.commit()
        db.refresh(control_data)

    def fetch_invoice_lines_without_product(self, company: str, store: int) -> list[ApiInvoiceDetail]:
        """
        Fetch invoice lines without a product for a specific company and store.
        Args:
            company (str): The company code.
            store (int): The store number.
            invoice_number (str): The invoice number.
        Returns:
            list[ApiInvoiceDetail]: A list of ApiInvoiceDetail instances.
        """
        with self.db.get_db() as session:
            # invoice_lines = (
            #     session.query(ApiInvoiceDetail)
            #     .join(ApiInvoiceHeader, ApiInvoiceDetail.reference == ApiInvoiceHeader.reference)
            #     .filter(
            #         ApiInvoiceHeader.company == company,
            #         ApiInvoiceHeader.store == store,
            #         ApiInvoiceHeader.invoice_number == invoice_number,
            #         ApiInvoiceDetail.product == text("''"),
            #     )
            #     .all()
            # )
            stmt = (
                select(ApiInvoiceDetail)
                .join(ApiInvoiceHeader, ApiInvoiceDetail.reference == ApiInvoiceHeader.reference)
                .where(
                    and_(
                        ApiInvoiceHeader.company == company,
                        ApiInvoiceHeader.store == store,
                        ApiInvoiceHeader.is_processed == 99,  # noqa: PLR2004
                        ApiInvoiceDetail.product == text("''"),
                    )
                )
            )
            result = session.execute(stmt)

            # Process the result as needed
            result_list = list(result.scalars().all())

        return result_list

    def get_invoice_details(  # noqa: PLR0912, PLR0915
        self, company: str, store: int, reference: str, details: list[dict[str, Any]], factor: int
    ) -> list[dict[str, Any]]:
        """
        Get the invoice details for a given invoice number.
        Args:
            company (str): The company code.
            store (int): The store number.
            reference (str): The invoice reference number.
            details (list[dict[str, Any]]): The list of invoice details.
            factor (int): The factor to adjust the line number.
        Returns:
            list[dict[str, Any]]: A list of processed invoice details.
        """
        if not details:
            logger.warning('No invoice details to process.')
            return []

        processed_details = []
        line_number = 0

        for line, detail in enumerate(details):
            if detail is None or len(detail) == 0:
                logger.warning('Detail is empty or None, skipping.')
                continue

            description = str(detail.get('descricao', '').strip())

            if description.startswith('@'):
                continue

            processed_detail = {}

            line_number += 1000
            article = int(detail.get('codigo', 0))
            product_stock = int(detail.get('prodstock', 0))

            if product_stock != article:
                article = product_stock if product_stock != 0 else article
            else:
                discount = Decimal(str(detail.get('desconto2', 0.0))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                line_value = Decimal(str(detail.get('valor', 0.0)))

                if discount == 0 and line_value == 0:
                    line_number -= 1000
                    continue

            processed_detail = {
                'reference': reference,
                'line': line_number,
                'invoice_number': reference,
                'detail_line': line_number,
                'discount_1': Decimal(str(detail.get('desconto2', 0.0))).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                ),
                'article': article,
            }

            if description.upper() == 'TAXA DE SERVIÇO' or article == TIP_CODE:
                product, description = get_tip_details(description)
            else:
                product, description = get_product_by_family(company, store, article, description)

            product_info = get_product_info(product)

            if len(description) == 0:
                description = product_info.get('description', '')

            vat_rate = int(detail.get('iva', 0))

            processed_detail['product'] = product
            processed_detail['description'] = description[:60]
            processed_detail['sales_unit'] = product_info.get('unit', '')
            processed_detail['stock_unit'] = product_info.get('stock_unit', product_info.get('unit', ''))
            processed_detail['stock_management'] = product_info.get('stock_management', '1')
            processed_detail['rate'] = vat_rate

            tax_level = get_miscellaneous_table(table_number=6207, code=str(vat_rate), columns=['A1_0'])

            if len(tax_level) == 0:
                try:
                    tax_level = TaxLevel(vat_rate)
                    processed_detail['taxes_level'] = [tax_level.name, '', '']
                except ValueError:
                    processed_detail['taxes_level'] = ['', '', '']
            else:
                processed_detail['taxes_level'] = [tax_level.get('A1_0', '').strip(), '', '']

            processed_detail['taxes'] = get_tax_code(processed_detail['taxes_level'][0], 'CON')

            quantity = self._calculate_quantity(Decimal(str(detail.get('qtd', 0.0))), factor)
            value = Decimal(str(detail.get('valor', 0.0)))

            if quantity is not None or quantity > 0:
                value = Decimal(value / quantity).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)

            processed_detail['quantity'] = quantity
            processed_detail['net_price'] = value
            processed_detail['net_no_tax_price'] = Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            processed_detail['gross_price'] = Decimal(str(detail.get('punit', 0.0))).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

            value = Decimal(str(detail.get('liquido', 0.0))) * factor
            processed_detail['amount_line_no_tax'] = Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            value = Decimal(str(detail.get('total', 0.0))) * factor
            processed_detail['amount_line'] = Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            processed_details.append(processed_detail)

        return processed_details

    @staticmethod
    def _calculate_quantity(quantity: Decimal, factor: int) -> Decimal:
        """
        Calculate the quantity based on the provided value.
        Args:
            quantity (Decimal): The quantity to be calculated.
            factor (int): The factor to adjust the quantity.
        Returns:
            Decimal: The calculated quantity.
        """
        if quantity is None or quantity == 0:
            return Decimal('0.0000')

        value = quantity.to_integral_value(rounding=ROUND_FLOOR)
        difference = quantity - value

        if difference >= Decimal('0.5'):
            return (value + Decimal('1')) * factor

        return value * factor


class ApiInvoiceTaxRepository:
    """
    Repository for managing API invoice tax data.
    This class provides methods to interact with the API invoice tax data.
    """

    def __init__(self):
        self.db = db

    @staticmethod
    def create_invoice_tax(db: Session, control_data: ApiInvoiceTax) -> None:
        """Create a new invoice tax in the database."""

        db.add(control_data)
        db.flush()
        db.commit()
        db.refresh(control_data)

    @staticmethod
    def delete_invoice_tax(db: Session, invoice_number: str) -> int:
        """
        Delete all tax records associated with a specific invoice number.
        Args:
            db (Session): The database session.
            invoice_number (str): The invoice number to delete tax records for.
        Returns:
            int: The number of tax records deleted.
        """
        deleted_rows = (
            db.query(ApiInvoiceTax).filter(ApiInvoiceTax.reference == invoice_number).delete(synchronize_session=False)
        )
        db.commit()
        return deleted_rows
