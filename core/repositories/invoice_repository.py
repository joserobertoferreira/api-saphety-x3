"""Módulo do repositório para interações com dados de faturas.

Este módulo contém a classe SalesInvoiceRepository, que abstrai todas as
operações de base de dados relacionadas com as faturas de venda (SINVOICEV),
cabeçalhos (SINVOICE) e entidades relacionadas.
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session, joinedload, load_only
from sqlalchemy.sql import and_, select

from core.models.customer import Customer
from core.models.sales_invoice import CustomerInvoiceHeader, SalesInvoice, SalesInvoiceDetail, SalesInvoiceTax
from core.utils.local_menus import NoYes

logger = logging.getLogger(__name__)


class SalesInvoiceRepository:
    """
    Repository for managing sales invoice data.
    This class provides methods to interact with the sales invoice data.
    """

    def fetch_pending_invoices(  # noqa: PLR6301
        self,
        session: Session,
        invoice_number: Optional[str] = None,
        invoice_cols: Optional[list[str]] = None,
        invoice_header_cols: Optional[list[str]] = None,
        customer_cols: Optional[list[str]] = None,
    ) -> list[SalesInvoice]:  # noqa: PLR6301
        """
        Search invoices marked as CIUS-PT invoice and not yet processed.
        Args:
            session (Session): The database session to use for the query.
            invoice_number (Optional[str]): The invoice number to filter by. If None, fetch all pending invoices.
            invoice_cols (Optional[list[str]]): List of invoice column names to load. If None, load default columns.
            invoice_header_cols (Optional[list[str]]): List of invoice header column names to load. If None,
            load default columns.
            customer_cols (Optional[list[str]]): List of customer column names to load. If None, load default columns.
        Returns:
            list[SalesInvoice]: A list of SalesInvoice instances with customers data.
        """
        logger.info('Fetching pending invoices from SalesInvoice table.')

        try:
            stmt = select(SalesInvoice)

            query = []

            if invoice_cols:
                query.append(load_only(*[getattr(SalesInvoice, col) for col in invoice_cols]))

            header_loader = joinedload(SalesInvoice.invoice_header)

            if invoice_header_cols:
                header_loader = header_loader.load_only(*[
                    getattr(CustomerInvoiceHeader, col) for col in invoice_header_cols
                ])

            customer_loader = joinedload(SalesInvoice.customer)

            if customer_cols:
                customer_loader = customer_loader.load_only(*[getattr(Customer, col) for col in customer_cols])

            query.append(customer_loader)
            query.append(header_loader)

            stmt = stmt.options(*query)

            conditions = [
                SalesInvoice.isSaphety == NoYes.YES.value,
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

    def fetch_details_for_invoice(self, session: Session, invoice_number: str) -> list[SalesInvoiceDetail]:  # noqa: PLR6301
        """Busca todas as linhas de detalhe para um número de fatura específico."""
        logger.info(f'Buscar linhas de detalhe para a fatura {invoice_number}...')

        stmt = select(SalesInvoiceDetail).where(SalesInvoiceDetail.invoiceNumber == invoice_number)

        records = session.execute(stmt).scalars().all()

        logger.info(f'Encontradas {len(records)} linhas para a fatura {invoice_number}.')
        return list(records)

    def fetch_taxes_for_invoice(self, session: Session, invoice_number: str) -> list[SalesInvoiceTax]:  # noqa: PLR6301
        """Busca todas as linhas de impostos para um número de fatura específico."""
        logger.info(f'Buscar linhas de impostos para a fatura {invoice_number}...')

        stmt = select(SalesInvoiceTax).where(SalesInvoiceTax.invoiceNumber == invoice_number)

        records = session.execute(stmt).scalars().all()

        logger.info(f'Encontradas {len(records)} linhas de impostos para a fatura {invoice_number}.')
        return list(records)
