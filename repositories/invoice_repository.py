import logging
from typing import Optional

from sqlalchemy.orm import Session, joinedload, load_only
from sqlalchemy.sql import and_, select

from database.database import db
from models.customer import Customer
from models.sales_invoice import SalesInvoice
from utils.local_menus import NoYes

logger = logging.getLogger(__name__)


class SalesInvoiceRepository:
    """
    Repository for managing sales invoice data.
    This class provides methods to interact with the sales invoice data.
    """

    def fetch_pending_invoices(self, session: Session, invoice_number: Optional[str] = None) -> list[SalesInvoice]:  # noqa: PLR6301
        """
        Search an invoices marked as CIUS-PT invoice and not yet processed.
        Args:
            session (Session): The database session to use for the query.
            invoice_number (Optional[str]): The invoice number to filter by. If None, fetch all pending invoices.
        Returns:
            list[SalesInvoice]: A list of SalesInvoice instances with customers data.
        """
        logger.info('Fetching pending invoices from SalesInvoice table.')

        try:
            stmt = select(SalesInvoice)
            stmt = stmt.options(joinedload(SalesInvoice.customer), joinedload(SalesInvoice.control))

            invoice_columns = [
                SalesInvoice.invoiceNumber,
                SalesInvoice.invoiceDate,
                SalesInvoice.billToCustomer,
            ]

            customer_columns = [
                Customer.customerCode,
                Customer.customerName,
                Customer.ciusType,
            ]

            stmt = select(SalesInvoice).options(
                load_only(*invoice_columns),
                joinedload(SalesInvoice.customer).load_only(*customer_columns),
            )

            conditions = [
                SalesInvoice.isCiusPT == NoYes.YES.value,
                SalesInvoice.control == None,  # noqa
            ]

            if invoice_number:
                # Filter by invoice number if provided (by CLI argument)
                logger.info(f'Filtering by invoice number: {invoice_number}')
                conditions.append(SalesInvoice.invoiceNumber == invoice_number)

            stmt = stmt.where(and_(*conditions))

            records = session.execute(stmt).scalars().all()

            logger.info(f'Fetched {len(records)} pending invoices from SalesInvoice table.')
            return list(records)

        except Exception:
            # Loga a exceção completa (incluindo o traceback)
            logger.exception('Ocorreu um erro inesperado ao buscar faturas pendentes na base de dados.')
            # Relança a exceção para que a camada de serviço que chamou este método
            # possa lidar com ela (ex: fazendo um rollback da transação).
            raise


class ApiInvoiceDetailRepository:
    """
    Repository for managing API invoice detail data.
    This class provides methods to interact with the API invoice detail data.
    """

    def __init__(self):
        self.db = db
