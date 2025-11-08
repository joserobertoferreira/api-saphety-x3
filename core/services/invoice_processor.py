import logging
from collections import defaultdict
from decimal import Decimal

import lxml.etree as etree  # noqa: PLR0402
from sqlalchemy.orm import Session

from core.config.settings import DEFAULT_LEGACY_DATE, NS_CAC, NS_CBC, NS_ESPAP, NS_ROOT, NSMAP
from core.database.database import db
from core.mappers.base_mapper import BaseMapper
from core.models.sales_invoice import CustomerInvoiceHeader, SalesInvoice, SalesInvoiceTax
from core.repositories.company_repository import CompanyRepository
from core.repositories.invoice_repository import SalesInvoiceRepository
from core.services.control_service import ControlService
from core.utils.conversions import Conversions
from core.utils.generics import Generics
from core.utils.local_menus import InvoiceType, NoYes, TaxLevelCode
from core.utils.xml_handler import XMLHandler

logger = logging.getLogger(__name__)


class InvoiceProcessorService:
    """
    Serviço responsável por processar faturas pendentes,
    gerar o XML CIUS-PT e coordenar o envio.
    """

    def __init__(self, customer_mapper: BaseMapper):
        """
        Inicializa o serviço e as suas dependências (repositórios).
        """
        self.invoice_repo = SalesInvoiceRepository()
        self.company_repo = CompanyRepository()
        self.xml_handler = XMLHandler()

        self.mapper = customer_mapper

        self.control_service = ControlService()

    def _build_cius_pt_xml(
        self, session: Session, invoice: SalesInvoice, mapper: BaseMapper, filename: str
    ) -> etree._Element:
        """
        Constrói a árvore XML para uma única fatura.

        Args:
            session: A sessão do banco de dados.
            invoice: O objeto SalesInvoice com os dados do cliente já carregados.
            mapper: O mapeador para customizações específicas do cliente.
            filename: O nome do ficheiro XML a ser gerado (sem extensão).

        Returns:
            Um objeto ElementTree representando o XML da fatura.
        """
        logger.info(f'Construir o XML para a fatura: {invoice.invoiceNumber}')

        # Criação do Elemento Raiz
        root = etree.Element(f'{{{NS_ROOT}}}Invoice', nsmap=NSMAP)

        # Cabeçalho da Fatura
        self._header_info(root, invoice, mapper, filename)

        # Informação do Fornecedor
        self._supplier_party(root, session, invoice)

        # Informação do Cliente
        self._customer_party(root, invoice)

        # Informação de Entrega
        self._add_delivery(root, invoice)

        # Totais de Impostos
        self._tax_total(root, session, invoice.invoice_header)

        # Totais Monetários
        self._legal_monetary_total(root, invoice.invoice_header)

        # Linhas da Fatura
        self._invoice_lines(root, session, invoice)

        logger.debug(f'XML para {invoice.invoiceNumber} construído (em memória).')
        return root

    def _header_info(self, parent: etree._Element, invoice: SalesInvoice, mapper: BaseMapper, filename: str) -> None:  # noqa: PLR6301
        """
        Trata dos elementos gerais do cabeçalho da fatura.
        """
        logger.info(f'Adicionar cabeçalho da fatura {invoice.invoiceNumber}.')

        # Identificador da especificação CIUS-PT. Este valor é fixo.
        etree.SubElement(parent, f'{{{NS_CBC}}}CustomizationID').text = NS_ESPAP

        # ID do Documento (obrigatório)
        etree.SubElement(parent, f'{{{NS_CBC}}}ID').text = filename

        # Data de Emissão (obrigatório)
        etree.SubElement(parent, f'{{{NS_CBC}}}IssueDate').text = invoice.invoiceDate.strftime('%Y-%m-%d')

        # Data de Vencimento (opcional)
        if (
            invoice.invoice_header.dueDateCalculationStartDate
            and invoice.invoice_header.dueDateCalculationStartDate != DEFAULT_LEGACY_DATE
        ):
            etree.SubElement(
                parent, f'{{{NS_CBC}}}DueDate'
            ).text = invoice.invoice_header.dueDateCalculationStartDate.strftime('%Y-%m-%d')

        # Tipo de Documento (obrigatório)
        # 380 = Fatura | 381 = Nota de Crédito | etc.
        etree.SubElement(parent, f'{{{NS_CBC}}}InvoiceTypeCode').text = (
            '380' if invoice.category == InvoiceType.INVOICE else '381'
        )

        # Moeda do Documento (obrigatório)
        etree.SubElement(parent, f'{{{NS_CBC}}}DocumentCurrencyCode').text = invoice.currency

        # Mapeamentos específicos do cliente

        # Referência do Comprador (opcional)
        buyer_reference = mapper.get_buyer_reference(invoice)

        if buyer_reference:
            etree.SubElement(parent, f'{{{NS_CBC}}}BuyerReference').text = buyer_reference

        # Referência do Pedido (opcional)
        order_reference = mapper.get_order_reference(invoice)

        if order_reference:
            order_ref = etree.SubElement(parent, f'{{{NS_CAC}}}OrderReference')
            etree.SubElement(order_ref, f'{{{NS_CBC}}}ID').text = order_reference['order_number']

        # Referência de Documento Adicional (opcional)
        additional_doc_ref = mapper.get_additional_document_reference(invoice)

        if additional_doc_ref:
            additional_ref = etree.SubElement(parent, f'{{{NS_CAC}}}AdditionalDocumentReference')
            etree.SubElement(
                additional_ref, f'{{{NS_CBC}}}ID', {'schemeID': additional_doc_ref.get('schemeID')}
            ).text = invoice.invoiceNumber
            etree.SubElement(additional_ref, f'{{{NS_CBC}}}DocumentTypeCode').text = additional_doc_ref.get('type_code')
            etree.SubElement(additional_ref, f'{{{NS_CBC}}}DocumentDescription').text = additional_doc_ref.get(
                'description'
            )
            attachment = etree.SubElement(additional_ref, f'{{{NS_CAC}}}Attachment')
            etree.SubElement(
                attachment,
                f'{{{NS_CBC}}}EmbeddedDocumentBinaryObject',
                {
                    'mimeCode': 'application/pdf',
                    'filename': additional_doc_ref.get('file_name'),
                },
            ).text = additional_doc_ref.get('pdf_base64')

        # Referência à Fatura Original (obrigatório para notas de crédito/débito)
        if invoice.category == InvoiceType.CREDIT_NOTE and invoice.sourceDocumentNumber.strip():  # noqa: PLC1901
            self._billing_reference(parent, invoice)

    def _billing_reference(self, parent: etree._Element, invoice: SalesInvoice) -> None:  # noqa: PLR6301
        """
        Adiciona a referência à fatura original, obrigatório para notas de crédito/débito (BG-3).
        """

        # Criação do Bloco BG-3
        billing_ref = etree.SubElement(parent, f'{{{NS_CAC}}}BillingReference')
        inv_doc_ref = etree.SubElement(billing_ref, f'{{{NS_CAC}}}InvoiceDocumentReference')

        # BT-25: Número da fatura original
        etree.SubElement(inv_doc_ref, f'{{{NS_CBC}}}ID').text = invoice.sourceDocumentNumber

        # BT-26: Data da fatura original (opcional)
        etree.SubElement(inv_doc_ref, f'{{{NS_CBC}}}IssueDate').text = invoice.sourceDocumentDate.strftime('%Y-%m-%d')

    def _supplier_party(self, parent: etree._Element, session: Session, invoice: SalesInvoice) -> None:
        """Adiciona o bloco de informação do Fornecedor (a sua empresa)."""
        logger.debug('Adicionar o bloco do Fornecedor (AccountingSupplierParty)...')

        # Carrega os dados do fornecedor
        supplier = self.company_repo.find_with_address(
            session=session, company_filters={'company': invoice.company}, address_filters={'isDefault': NoYes.YES}
        )

        # Cria o nó principal do fornecedor
        supplier_party = etree.SubElement(parent, f'{{{NS_CAC}}}AccountingSupplierParty')
        party = etree.SubElement(supplier_party, f'{{{NS_CAC}}}Party')

        # Nome do Fornecedor
        party_name = etree.SubElement(party, f'{{{NS_CAC}}}PartyName')
        etree.SubElement(party_name, f'{{{NS_CBC}}}Name').text = supplier[0].companyName.strip()

        # Morada Postal do Fornecedor
        full_address = ' '.join(
            filter(
                None,
                [
                    supplier[0].addresses[0].addressLine1.strip(),
                    supplier[0].addresses[0].addressLine2.strip(),
                    supplier[0].addresses[0].addressLine3.strip(),
                ],
            )
        )

        postal_address = etree.SubElement(party, f'{{{NS_CAC}}}PostalAddress')
        etree.SubElement(postal_address, f'{{{NS_CBC}}}StreetName').text = full_address
        etree.SubElement(postal_address, f'{{{NS_CBC}}}CityName').text = supplier[0].addresses[0].city.strip()
        etree.SubElement(postal_address, f'{{{NS_CBC}}}PostalZone').text = supplier[0].addresses[0].postalCode.strip()
        country = etree.SubElement(postal_address, f'{{{NS_CAC}}}Country')
        etree.SubElement(country, f'{{{NS_CBC}}}IdentificationCode').text = supplier[0].addresses[0].country.strip()

        # Informação Fiscal do Fornecedor (NIF)
        party_tax_scheme = etree.SubElement(party, f'{{{NS_CAC}}}PartyTaxScheme')
        # NIF precedido do código do país
        etree.SubElement(party_tax_scheme, f'{{{NS_CBC}}}CompanyID').text = supplier[0].intraCommunityVatNumber.strip()
        tax_scheme = etree.SubElement(party_tax_scheme, f'{{{NS_CAC}}}TaxScheme')
        etree.SubElement(tax_scheme, f'{{{NS_CBC}}}ID').text = 'VAT'

        # Informação Legal do Fornecedor
        party_legal_entity = etree.SubElement(party, f'{{{NS_CAC}}}PartyLegalEntity')
        # Nome de registo (firma)
        etree.SubElement(party_legal_entity, f'{{{NS_CBC}}}RegistrationName').text = supplier[0].companyName.strip()

    def _customer_party(self, parent: etree._Element, invoice: SalesInvoice) -> None:  # noqa: PLR6301
        """Adiciona o bloco de informação do Cliente."""
        logger.debug(f'Adicionar o bloco do Cliente para a fatura {invoice.invoiceNumber}')

        # Primeiro, uma verificação de segurança.
        if not invoice.customer:
            logger.error(f'Fatura {invoice.invoiceNumber} não tem cliente associado. A saltar o bloco do cliente.')
            # Poderíamos levantar um erro aqui para impedir o envio de uma fatura inválida.
            raise ValueError(f'Dados do cliente em falta para a fatura {invoice.invoiceNumber}')

        # Cria o nó principal do cliente
        customer_party = etree.SubElement(parent, f'{{{NS_CAC}}}AccountingCustomerParty')
        party = etree.SubElement(customer_party, f'{{{NS_CAC}}}Party')

        # Nome do Cliente (vem do objeto relacionado)
        full_name = ' '.join(
            filter(
                None,
                [
                    invoice.invoice_header.billToCustomerName1.strip(),
                    invoice.invoice_header.billToCustomerName2.strip(),
                ],
            )
        )
        party_name = etree.SubElement(party, f'{{{NS_CAC}}}PartyName')
        etree.SubElement(party_name, f'{{{NS_CBC}}}Name').text = full_name

        # Morada Postal do Cliente
        full_address = ' '.join(
            filter(
                None,
                [
                    invoice.invoice_header.billToCustomerAddresses[0],
                    invoice.invoice_header.billToCustomerAddresses[1],
                    invoice.invoice_header.billToCustomerAddresses[2],
                ],
            )
        )

        postal_address = etree.SubElement(party, f'{{{NS_CAC}}}PostalAddress')
        etree.SubElement(postal_address, f'{{{NS_CBC}}}StreetName').text = full_address
        etree.SubElement(
            postal_address, f'{{{NS_CBC}}}CityName'
        ).text = invoice.invoice_header.billToCustomerCity.strip()
        etree.SubElement(
            postal_address, f'{{{NS_CBC}}}PostalZone'
        ).text = invoice.invoice_header.billToCustomerPostalCode.strip()
        country = etree.SubElement(postal_address, f'{{{NS_CAC}}}Country')
        etree.SubElement(
            country, f'{{{NS_CBC}}}IdentificationCode'
        ).text = invoice.invoice_header.billToCustomerCountry.strip()

        # Informação Fiscal do Cliente (NIF)
        if invoice.billToCustomer != invoice.invoice_header.businessPartner:
            vat_number = invoice.customer.business_partner.europeanUnionVatNumber.strip()
        else:
            vat_number = invoice.billToCustomerEuropeanUnionVatNumber.strip()

        party_tax_scheme = etree.SubElement(party, f'{{{NS_CAC}}}PartyTaxScheme')
        etree.SubElement(party_tax_scheme, f'{{{NS_CBC}}}CompanyID').text = vat_number
        tax_scheme = etree.SubElement(party_tax_scheme, f'{{{NS_CAC}}}TaxScheme')
        etree.SubElement(tax_scheme, f'{{{NS_CBC}}}ID').text = 'VAT'

        # Informação Legal do Cliente
        party_legal_entity = etree.SubElement(party, f'{{{NS_CAC}}}PartyLegalEntity')
        etree.SubElement(party_legal_entity, f'{{{NS_CBC}}}RegistrationName').text = full_name

    def _add_delivery(self, parent: etree._Element, invoice: SalesInvoice) -> None:  # noqa: PLR6301
        """Adiciona o bloco da Morada de Entrega (BG-15), obrigatório em Portugal."""
        logger.debug(f'Adicionar o bloco de Entrega para a fatura {invoice.invoiceNumber}')

        # Bloco Principal <cac:Delivery>
        delivery = etree.SubElement(parent, f'{{{NS_CAC}}}Delivery')

        delivery_location = etree.SubElement(delivery, f'{{{NS_CAC}}}DeliveryLocation')
        address = etree.SubElement(delivery_location, f'{{{NS_CAC}}}Address')

        # Morada de entrega do Cliente
        full_address = ' '.join(
            filter(
                None,
                [invoice.addressLine[0], invoice.addressLine[1], invoice.addressLine[2]],
            )
        )

        etree.SubElement(address, f'{{{NS_CBC}}}StreetName').text = full_address
        etree.SubElement(address, f'{{{NS_CBC}}}CityName').text = invoice.shipToCustomerCity.strip()
        etree.SubElement(address, f'{{{NS_CBC}}}PostalZone').text = invoice.shipToCustomerPostalCode.strip()
        country = etree.SubElement(address, f'{{{NS_CAC}}}Country')
        etree.SubElement(country, f'{{{NS_CBC}}}IdentificationCode').text = invoice.shipToCustomerCountry.strip()

    def _legal_monetary_total(self, parent: etree._Element, invoice: CustomerInvoiceHeader) -> None:  # noqa: PLR6301
        """Adiciona o bloco de totais monetários do documento."""
        logger.debug(f'A adicionar totais para a fatura {invoice.invoiceNumber}')

        total_block = etree.SubElement(parent, f'{{{NS_CAC}}}LegalMonetaryTotal')

        # Cria o atributo para moeda
        currency_attr = {'currencyID': invoice.currency}

        # Soma dos valores das linhas (sem impostos e sem descontos/encargos a nível de documento)
        etree.SubElement(
            total_block, f'{{{NS_CBC}}}LineExtensionAmount', currency_attr
        ).text = Conversions.format_monetary(
            invoice.totalAmountExcludingTax  # Mapeia para AMTNOT_0
        )

        # Total do documento sem impostos (depois de descontos/encargos a nível de documento)
        etree.SubElement(
            total_block, f'{{{NS_CBC}}}TaxExclusiveAmount', currency_attr
        ).text = Conversions.format_monetary(
            invoice.totalAmountExcludingTax  # Mapeia para AMTNOT_0
        )

        # Total do documento com impostos
        etree.SubElement(
            total_block, f'{{{NS_CBC}}}TaxInclusiveAmount', currency_attr
        ).text = Conversions.format_monetary(
            invoice.totalAmountIncludingTax  # Mapeia para AMTATI_0
        )

        # Total a Pagar (geralmente igual ao total com impostos, mas pode ser diferente se houver pré-pagamentos)
        if invoice.dueDateCalculationStartDate and invoice.dueDateCalculationStartDate != DEFAULT_LEGACY_DATE:
            etree.SubElement(
                total_block, f'{{{NS_CBC}}}PayableAmount', currency_attr
            ).text = Conversions.format_monetary(
                invoice.totalAmountIncludingTax  # Mapeia para AMTATI_0
            )

    @staticmethod
    def _aggregate_taxes(invoice_taxes: list[SalesInvoiceTax]) -> dict[tuple[str, Decimal], dict[str, Decimal]]:
        """
        Agrega uma lista de registos de imposto por categoria e taxa CIUS-PT.

        Recebe a lista de impostos lida da base de dados e a sumariza para garantir
        que haja apenas uma entrada por combinação de (código_categoria_cius, taxa_percentual).

        Args:
            invoice_taxes: Uma lista de objetos SalesInvoiceTax.

        Returns:
            Um dicionário onde a chave é uma tupla (cius_code, rate) e o valor
            é um dicionário com os totais {'taxable_amount': ..., 'tax_amount': ...}.
        """

        # Dicionário para acumular os subtotais.
        # O defaultdict cria automaticamente uma nova entrada se a chave não existir.
        aggregated_subtotals = defaultdict(lambda: {'taxable_amount': Decimal('0'), 'tax_amount': Decimal('0')})

        for tax_record in invoice_taxes:
            # Converte o código interno para o código de categoria CIUS ('NOR', 'RED', 'INT', etc.)
            cius_code = Generics.get_enum_name(TaxLevelCode, int(tax_record.rate))

            # A chave de agregação é a combinação do código CIUS e da taxa percentual
            aggregation_key = (cius_code, tax_record.rate)

            # Acumule os valores
            # Se a chave ('NOR', Decimal('23.00')) já existir, ele soma.
            # Se não existir, o defaultdict cria-a com os valores iniciais de 0.
            aggregated_subtotals[aggregation_key]['taxable_amount'] += tax_record.taxBasis
            aggregated_subtotals[aggregation_key]['tax_amount'] += tax_record.taxAmount

        # Converte de volta para um dicionário normal (opcional, mas mais limpo)
        return dict(aggregated_subtotals)

    def _tax_total(self, parent: etree._Element, session: Session, invoice: CustomerInvoiceHeader) -> None:
        """
        Adiciona o bloco de resumo de impostos (TaxTotal) a partir dos dados já
        agregados da tabela SalesInvoiceTax (SVCRVAT).

        Args:
            parent: O elemento XML pai onde o bloco será adicionado.
            invoice_taxes: Uma lista de objetos SalesInvoiceTax, cada um representando
                           um subtotal por taxa de imposto.
        """

        # Buscas as taxas de IVA aplicadas na fatura
        invoice_taxes = self.invoice_repo.fetch_taxes_for_invoice(session=session, invoice_number=invoice.invoiceNumber)

        if not invoice_taxes:
            logger.warning('Nenhum dado de imposto encontrado para a fatura. Saltar o bloco TaxTotal.')
            return

        logger.debug(f'Adicionar totais de impostos para a fatura {invoice.invoiceNumber}')

        # Cria o atributo para moeda
        currency_attr = {'currencyID': invoice.currency}

        # Calcula o valor total do imposto
        total_tax_amount = sum(tax.taxAmount for tax in invoice_taxes if tax.taxAmount is not None)

        # Bloco Principal <cac:TaxTotal>
        tax_total_block = etree.SubElement(parent, f'{{{NS_CAC}}}TaxTotal')

        # Valor total de todos os impostos na fatura
        etree.SubElement(tax_total_block, f'{{{NS_CBC}}}TaxAmount', currency_attr).text = Conversions.format_monetary(
            Decimal(total_tax_amount)
        )

        # Subtotal por Taxa de IVA

        # Calcula o subtotal por taxa de IVA
        tax_subtotals = self._aggregate_taxes(invoice_taxes)

        # Este bloco <cac:TaxSubtotal> pode repetir-se para cada taxa de IVA diferente.
        for (cius_code, rate), totals in tax_subtotals.items():
            tax_subtotal_block = etree.SubElement(tax_total_block, f'{{{NS_CAC}}}TaxSubtotal')

            # Base tributável para esta taxa (valor sobre o qual o imposto incide)
            etree.SubElement(
                tax_subtotal_block, f'{{{NS_CBC}}}TaxableAmount', currency_attr
            ).text = Conversions.format_monetary(totals['taxable_amount'])

            # Valor do imposto para esta taxa
            etree.SubElement(
                tax_subtotal_block, f'{{{NS_CBC}}}TaxAmount', currency_attr
            ).text = Conversions.format_monetary(totals['tax_amount'])

            # Categoria do Imposto
            tax_category = etree.SubElement(tax_subtotal_block, f'{{{NS_CAC}}}TaxCategory')

            etree.SubElement(tax_category, f'{{{NS_CBC}}}ID').text = cius_code

            # Percentagem da taxa
            etree.SubElement(tax_category, f'{{{NS_CBC}}}Percent').text = Conversions.format_monetary(rate)

            # Esquema do Imposto (geralmente "VAT")
            tax_scheme = etree.SubElement(tax_category, f'{{{NS_CAC}}}TaxScheme')
            etree.SubElement(tax_scheme, f'{{{NS_CBC}}}ID').text = 'VAT'

    def _invoice_lines(self, parent: etree._Element, session: Session, invoice: SalesInvoice) -> None:
        """
        Busca e adiciona todas as linhas da fatura (<cac:InvoiceLine>) ao XML.
        """
        logger.debug(f'Adicionar linhas para a fatura {invoice.invoiceNumber}')

        invoice_details = self.invoice_repo.fetch_details_for_invoice(
            session=session, invoice_number=invoice.invoiceNumber
        )

        for detail in invoice_details:
            # Bloco Principal <cac:InvoiceLine>
            line_item = etree.SubElement(parent, f'{{{NS_CAC}}}InvoiceLine')

            # ID da Linha
            etree.SubElement(line_item, f'{{{NS_CBC}}}ID').text = str(int(detail.lineNumber / 1000))

            # Quantidade Faturada
            etree.SubElement(line_item, f'{{{NS_CBC}}}InvoicedQuantity', unitCode='C62').text = str(
                str(Conversions.convert_value(detail.quantityInSalesUnit, precision=2))
            )

            # Valor Líquido da Linha (sem impostos)
            etree.SubElement(
                line_item, f'{{{NS_CBC}}}LineExtensionAmount', {'currencyID': invoice.currency}
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
                price, f'{{{NS_CBC}}}PriceAmount', {'currencyID': invoice.currency}
            ).text = Conversions.format_monetary(detail.netPrice)

    def process_pending_invoices(self, invoice_id: str | None = None) -> None:
        """
        O método principal do serviço. Orquestra todo o fluxo de processamento.
        """
        logger.info('Serviço de processamento de faturas iniciado.')

        # Obtém uma sessão da base de dados usando o nosso gestor
        with db.get_db() as session:
            try:
                # Busca as faturas pendentes
                invoices_to_process = self.invoice_repo.fetch_pending_invoices(
                    session=session,
                    invoice_number=invoice_id,
                )

                if not invoices_to_process:
                    logger.info('Nenhuma fatura pendente encontrada para processamento.')
                    return

                # Itera e processa cada fatura
                for invoice in invoices_to_process:
                    try:
                        # Define o nome do ficheiro XML
                        filename = ''.join(c for c in invoice.invoiceNumber if c.isalnum())

                        # Constrói o XML para a fatura atual
                        invoice_xml_tree = self._build_cius_pt_xml(
                            session=session, invoice=invoice, mapper=self.mapper, filename=filename
                        )

                        logger.info(f'Gerar o ficheiro XML para a fatura {invoice.invoiceNumber} como {filename}.xml')

                        # Cria o ficheiro XML
                        save_xml_file = XMLHandler.save_xml_to_file(
                            xml_tree=invoice_xml_tree,
                            filename=f'{filename}.xml',
                        )

                        # Atualiza o estado da fatura para "Pendente"
                        self.control_service.mark_as_generated(
                            session=session, invoice_number=invoice.invoiceNumber, file_path=str(save_xml_file)
                        )

                    except Exception as e:
                        # Se algo correu mal com ESTA fatura, registamos o erro
                        # e continuamos para a próxima.
                        logger.error(f'Falha ao processar a fatura {invoice.invoiceNumber}: {e}')

                        # É crucial registar o erro na tabela de controlo
                        self.control_service.log_processing_error(
                            session=session, invoice_number=invoice.invoiceNumber, error=e
                        )

                    # Se tudo correu bem, faz commit da transação
                    session.commit()
                    logger.info('Processamento concluído com sucesso.')

            except Exception:
                logger.exception('Ocorreu um erro crítico durante o processamento. Fazer rollback...')
                if 'session' in locals():
                    session.rollback()  # Garante que nenhuma alteração parcial é guardada
