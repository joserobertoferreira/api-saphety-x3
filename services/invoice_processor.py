import logging

import lxml.etree as etree  # noqa: PLR0402

from config.settings import NS_CAC, NS_CBC, NS_ROOT, NSMAP
from database.database import db
from repositories.invoice_repository import SalesInvoiceRepository
from utils.conversions import Conversions

logger = logging.getLogger(__name__)


class InvoiceProcessorService:
    """
    Serviço responsável por processar faturas pendentes,
    gerar o XML CIUS-PT e coordenar o envio.
    """

    def __init__(self):
        pass

    def _build_cius_pt_xml(self, invoice, session) -> etree._Element:
        """
        Constrói a árvore XML para uma única fatura.

        Args:
            invoice: O objeto SalesInvoice com os dados do cliente já carregados.
            session: A sessão do banco de dados.

        Returns:
            Um objeto ElementTree representando o XML da fatura.
        """
        logger.info(f'Construir o XML para a fatura: {invoice.invoiceNumber}')

        # Criação do Elemento Raiz
        root = etree.Element(f'{{{NS_ROOT}}}Invoice', nsmap=NSMAP)

        # Cabeçalho da Fatura
        self._header_info(root, invoice)

        # Informação do Fornecedor
        self._supplier_party(root, invoice)

        # Informação do Cliente
        self._customer_party(root, invoice)

        # Totais de Impostos
        self._tax_total(root, invoice)

        # Totais Monetários
        self._legal_monetary_total(root, invoice)

        # Linhas da Fatura
        self._invoice_lines(root, invoice, session)

        logger.debug(f'XML para {invoice.invoiceNumber} construído (em memória).')
        return root

    def _header_info(self, parent: etree._Element, invoice) -> None:  # noqa: PLR6301
        """
        Trata dos elementos gerais do cabeçalho da fatura.
        """
        logger.info(f'Adicionar cabeçalho da fatura {invoice.invoiceNumber}.')

        # ID do Documento (obrigatório)
        etree.SubElement(parent, f'{{{NS_CBC}}}ID').text = invoice.invoiceNumber

        # Data de Emissão (obrigatório)
        etree.SubElement(parent, f'{{{NS_CBC}}}IssueDate').text = invoice.invoiceDate.strftime('%Y-%m-%d')

        # Tipo de Documento (obrigatório)
        # 380 = Fatura | 381 = Nota de Crédito | etc.
        # TODO: A sua lógica precisa de determinar o tipo correto. Vamos assumir 380 por agora.
        etree.SubElement(parent, f'{{{NS_CBC}}}InvoiceTypeCode').text = '380'

        # Moeda do Documento (obrigatório)
        etree.SubElement(parent, f'{{{NS_CBC}}}DocumentCurrencyCode').text = invoice.currency

    def _supplier_party(self, parent: etree._Element, invoice):  # noqa: PLR6301
        """Adiciona o bloco de informação do Fornecedor (a sua empresa)."""
        logger.debug('A adicionar o bloco do Fornecedor (AccountingSupplierParty)...')

        # Cria o nó principal do fornecedor
        supplier_party = etree.SubElement(parent, f'{{{NS_CAC}}}AccountingSupplierParty')
        party = etree.SubElement(supplier_party, f'{{{NS_CAC}}}Party')

        # Nome do Fornecedor
        party_name = etree.SubElement(party, f'{{{NS_CAC}}}PartyName')
        etree.SubElement(party_name, f'{{{NS_CBC}}}Name').text = 'NOME DA SUA EMPRESA'  # TODO: Obter da config

        # Morada Postal do Fornecedor
        postal_address = etree.SubElement(party, f'{{{NS_CAC}}}PostalAddress')
        etree.SubElement(postal_address, f'{{{NS_CBC}}}StreetName').text = 'A SUA RUA, Nº'
        etree.SubElement(postal_address, f'{{{NS_CBC}}}CityName').text = 'A SUA CIDADE'
        etree.SubElement(postal_address, f'{{{NS_CBC}}}PostalZone').text = 'SEU CÓDIGO-POSTAL'
        country = etree.SubElement(postal_address, f'{{{NS_CAC}}}Country')
        etree.SubElement(country, f'{{{NS_CBC}}}IdentificationCode').text = 'PT'

        # Informação Fiscal do Fornecedor (NIF)
        party_tax_scheme = etree.SubElement(party, f'{{{NS_CAC}}}PartyTaxScheme')
        # NIF precedido do código do país
        etree.SubElement(party_tax_scheme, f'{{{NS_CBC}}}CompanyID').text = 'PT500000000'  # TODO: Obter da config
        tax_scheme = etree.SubElement(party_tax_scheme, f'{{{NS_CAC}}}TaxScheme')
        etree.SubElement(tax_scheme, f'{{{NS_CBC}}}ID').text = 'VAT'

        # Informação Legal do Fornecedor
        party_legal_entity = etree.SubElement(party, f'{{{NS_CAC}}}PartyLegalEntity')
        # Nome de registo (firma)
        etree.SubElement(party_legal_entity, f'{{{NS_CBC}}}RegistrationName').text = 'NOME DA SUA EMPRESA, LDA'
        # Matrícula na conservatória
        etree.SubElement(party_legal_entity, f'{{{NS_CBC}}}CompanyID').text = '500000000'

    def _customer_party(self, parent: etree._Element, invoice) -> None:  # noqa: PLR6301
        """Adiciona o bloco de informação do Cliente."""
        logger.debug(f'A adicionar o bloco do Cliente para a fatura {invoice.invoiceNumber}')

        # Primeiro, uma verificação de segurança.
        if not invoice.customer:
            logger.error(f'Fatura {invoice.invoiceNumber} não tem cliente associado. A saltar o bloco do cliente.')
            # Poderíamos levantar um erro aqui para impedir o envio de uma fatura inválida.
            raise ValueError(f'Dados do cliente em falta para a fatura {invoice.invoiceNumber}')

        # Cria o nó principal do cliente
        customer_party = etree.SubElement(parent, f'{{{NS_CAC}}}AccountingCustomerParty')
        party = etree.SubElement(customer_party, f'{{{NS_CAC}}}Party')

        # Nome do Cliente (vem do objeto relacionado)
        party_name = etree.SubElement(party, f'{{{NS_CAC}}}PartyName')
        etree.SubElement(party_name, f'{{{NS_CBC}}}Name').text = invoice.customer.customerName

        # Morada Postal do Cliente
        # TODO: Precisamos de um repositório/serviço para buscar a morada do cliente
        # Por agora, usaremos placeholders, mas o ideal seria ter uma relação
        # invoice.customer.address ou um método repo.find_address_for_customer().
        postal_address = etree.SubElement(party, f'{{{NS_CAC}}}PostalAddress')
        etree.SubElement(postal_address, f'{{{NS_CBC}}}StreetName').text = 'RUA DO CLIENTE'  # Placeholder
        etree.SubElement(postal_address, f'{{{NS_CBC}}}CityName').text = 'CIDADE DO CLIENTE'  # Placeholder
        etree.SubElement(postal_address, f'{{{NS_CBC}}}PostalZone').text = 'CODIGO-POSTAL CLIENTE'  # Placeholder
        country = etree.SubElement(postal_address, f'{{{NS_CAC}}}Country')
        etree.SubElement(country, f'{{{NS_CBC}}}IdentificationCode').text = 'PT'  # Placeholder

        # Informação Fiscal do Cliente (NIF)
        # O NIF completo (ex: PT501234567) deve vir da tabela BPARTNER.
        # Vamos assumir que temos a relação Customer <-> BusinessPartner a funcionar.
        nif = 'PT999999990'  # Valor por defeito para "Consumidor Final"
        if invoice.customer.business_partner and invoice.customer.business_partner.europeanUnionVatNumber:
            nif = invoice.customer.business_partner.europeanUnionVatNumber.strip()

        party_tax_scheme = etree.SubElement(party, f'{{{NS_CAC}}}PartyTaxScheme')
        etree.SubElement(party_tax_scheme, f'{{{NS_CBC}}}CompanyID').text = nif
        tax_scheme = etree.SubElement(party_tax_scheme, f'{{{NS_CAC}}}TaxScheme')
        etree.SubElement(tax_scheme, f'{{{NS_CBC}}}ID').text = 'VAT'

        # Informação Legal do Cliente
        party_legal_entity = etree.SubElement(party, f'{{{NS_CAC}}}PartyLegalEntity')
        etree.SubElement(party_legal_entity, f'{{{NS_CBC}}}RegistrationName').text = invoice.customer.customerName

    def _legal_monetary_total(self, parent: etree._Element, invoice) -> None:  # noqa: PLR6301
        """Adiciona o bloco de totais monetários do documento."""
        logger.debug(f'A adicionar totais para a fatura {invoice.invoiceNumber}')

        total_block = etree.SubElement(parent, f'{{{NS_CAC}}}LegalMonetaryTotal')

        # Soma dos valores das linhas (sem impostos e sem descontos/encargos a nível de documento)
        # O LineExtensionAmount a nível de documento é a soma dos LineExtensionAmount de cada linha.
        # Vamos assumir que corresponde ao total s/imposto por agora.
        etree.SubElement(total_block, f'{{{NS_CBC}}}LineExtensionAmount').text = Conversions.format_monetary(
            invoice.invoice_header.totalAmountExcludingTax  # Mapeia para AMTNOT_0
        )

        # Total do documento sem impostos (depois de descontos/encargos a nível de documento)
        etree.SubElement(total_block, f'{{{NS_CBC}}}TaxExclusiveAmount').text = Conversions.format_monetary(
            invoice.invoice_header.totalAmountExcludingTax  # Mapeia para AMTNOT_0
        )

        # Total do documento com impostos
        etree.SubElement(total_block, f'{{{NS_CBC}}}TaxInclusiveAmount').text = Conversions.format_monetary(
            invoice.invoice_header.totalAmountIncludingTax  # Mapeia para AMTATI_0
        )

        # Total a Pagar (geralmente igual ao total com impostos, mas pode ser diferente se houver pré-pagamentos)
        etree.SubElement(total_block, f'{{{NS_CBC}}}PayableAmount').text = Conversions.format_monetary(
            invoice.invoice_header.totalAmountIncludingTax  # Mapeia para AMTATI_0
        )

        # Outros campos opcionais como AllowanceTotalAmount (total de descontos),
        # ChargeTotalAmount (total de encargos), PrepaidAmount (valor pré-pago)
        # podem ser adicionados aqui se existirem nos seus dados.

    def _tax_total(self, parent: etree._Element, invoice) -> None:  # noqa: PLR6301
        """
        Adiciona o bloco de resumo de impostos (TaxTotal).
        Esta é uma versão simplificada que assume uma única taxa de IVA para todo o documento.
        """
        logger.debug(f'Adicionar totais de impostos para a fatura {invoice.invoiceNumber}')

        # Calcula o valor total do imposto
        total_tax_amount = (
            invoice.invoice_header.totalAmountIncludingTax - invoice.invoice_header.totalAmountExcludingTax
        )

        # --- Bloco Principal <cac:TaxTotal> ---
        tax_total_block = etree.SubElement(parent, f'{{{NS_CAC}}}TaxTotal')

        # Valor total de todos os impostos na fatura
        etree.SubElement(tax_total_block, f'{{{NS_CBC}}}TaxAmount').text = Conversions.format_monetary(total_tax_amount)

        # --- Subtotal por Taxa de IVA ---
        # No futuro, este bloco <cac:TaxSubtotal> pode repetir-se para cada taxa de IVA diferente.
        tax_subtotal_block = etree.SubElement(tax_total_block, f'{{{NS_CAC}}}TaxSubtotal')

        # Base tributável para esta taxa (valor sobre o qual o imposto incide)
        etree.SubElement(tax_subtotal_block, f'{{{NS_CBC}}}TaxableAmount').text = Conversions.format_monetary(
            invoice.invoice_header.totalAmountExcludingTax
        )
        # Valor do imposto para esta taxa
        etree.SubElement(tax_subtotal_block, f'{{{NS_CBC}}}TaxAmount').text = Conversions.format_monetary(
            total_tax_amount
        )

        # Categoria do Imposto
        tax_category = etree.SubElement(tax_subtotal_block, f'{{{NS_CAC}}}TaxCategory')

        # Código da categoria do imposto (ex: "S" para Standard/Normal)
        # TODO: A sua lógica precisa de determinar o código correto.
        etree.SubElement(tax_category, f'{{{NS_CBC}}}ID').text = 'S'

        # Percentagem da taxa
        # TODO: A sua lógica precisa de calcular ou obter a percentagem correta.
        # Vamos assumir 23% por agora.
        etree.SubElement(tax_category, f'{{{NS_CBC}}}Percent').text = '23.00'

        # Esquema do Imposto (geralmente "VAT")
        tax_scheme = etree.SubElement(tax_category, f'{{{NS_CAC}}}TaxScheme')
        etree.SubElement(tax_scheme, f'{{{NS_CBC}}}ID').text = 'VAT'

    def _invoice_lines(self, parent: etree._Element, invoice, session):  # noqa: PLR6301
        """
        Busca e adiciona todas as linhas da fatura (<cac:InvoiceLine>) ao XML.
        """
        logger.debug(f'Adicionar linhas para a fatura {invoice.invoiceNumber}')

        repo = SalesInvoiceRepository()
        invoice_details = repo.fetch_details_for_invoice(session=session, invoice_number=invoice.invoiceNumber)

        for detail in invoice_details:
            # --- Bloco Principal <cac:InvoiceLine> ---
            line_item = etree.SubElement(parent, f'{{{NS_CAC}}}InvoiceLine')

            # ID da Linha
            etree.SubElement(line_item, f'{{{NS_CBC}}}ID').text = str(detail.lineNumber)

            # Quantidade Faturada
            etree.SubElement(
                line_item,
                f'{{{NS_CBC}}}InvoicedQuantity',
                unitCode='C62',  # Código para "unidade". TODO: Mapear a sua unidade
            ).text = str(detail.quantityInSalesUnit)

            # Valor Líquido da Linha (sem impostos)
            etree.SubElement(line_item, f'{{{NS_CBC}}}LineExtensionAmount').text = Conversions.format_monetary(
                detail.lineAmountExcludingTax
            )

            # --- Detalhes do Item <cac:Item> ---
            item = etree.SubElement(line_item, f'{{{NS_CAC}}}Item')
            etree.SubElement(item, f'{{{NS_CBC}}}Name').text = detail.productDescriptionUserLanguage

            # Imposto do Item
            tax_category = etree.SubElement(item, f'{{{NS_CAC}}}ClassifiedTaxCategory')
            # TODO: Mapear o seu `detail.taxCode1` para o código CIUS-PT ('S', 'Z', etc.) e a percentagem
            etree.SubElement(tax_category, f'{{{NS_CBC}}}ID').text = 'S'  # Exemplo
            etree.SubElement(tax_category, f'{{{NS_CBC}}}Percent').text = '23.00'  # Exemplo
            tax_scheme = etree.SubElement(tax_category, f'{{{NS_CAC}}}TaxScheme')
            etree.SubElement(tax_scheme, f'{{{NS_CBC}}}ID').text = 'VAT'

            # --- Preço do Item <cac:Price> ---
            price = etree.SubElement(line_item, f'{{{NS_CAC}}}Price')
            etree.SubElement(price, f'{{{NS_CBC}}}PriceAmount').text = Conversions.format_monetary(
                detail.netPrice, num_decimals=5
            )

    def process_pending_invoices(self, invoice_id: str | None = None):
        """
        O método principal do serviço. Orquestra todo o fluxo de processamento.
        """
        logger.info('Serviço de processamento de faturas iniciado.')

        # Obtém uma sessão da base de dados usando o nosso gestor
        with db.get_db() as session:
            try:
                # Inicializa o repositório com a sessão ativa
                repo = SalesInvoiceRepository()

                # Define as colunas a buscar (pode ser ajustado conforme necessário)
                invoice_cols = [
                    'invoiceNumber',
                    'invoiceDate',
                    'billToCustomer',
                    'currency',
                ]

                invoice_header_cols = ['totalAmountExcludingTax', 'totalAmountIncludingTax']

                customer_cols = ['customerCode', 'customerName', 'ciusType']

                # Busca as faturas pendentes
                invoices_to_process = repo.fetch_pending_invoices(
                    session=session,
                    invoice_number=invoice_id,
                    invoice_cols=invoice_cols,
                    invoice_header_cols=invoice_header_cols,
                    customer_cols=customer_cols,
                )

                if not invoices_to_process:
                    logger.info('Nenhuma fatura pendente encontrada para processamento.')
                    return

                # Itera e processa cada fatura
                for invoice in invoices_to_process:
                    # 3. Constrói o XML para a fatura atual
                    invoice_xml_tree = self._build_cius_pt_xml(invoice, session)

                    # Converte a árvore XML para uma string de bytes para visualização/gravação
                    xml_bytes = etree.tostring(
                        invoice_xml_tree, pretty_print=True, xml_declaration=True, encoding='UTF-8'
                    )

                    # (Ação Temporária) Imprime o XML gerado para verificação
                    logger.info(f'--- XML Gerado para a Fatura {invoice.invoiceNumber} ---')
                    print(xml_bytes.decode('utf-8'))  # .decode() para imprimir como texto

                    # TODO (Próximos Passos):
                    # - Gravar o `xml_bytes` num ficheiro.
                    # - Enviar o `xml_bytes` via API.
                    # - Inserir/Atualizar o registo na tabela de controlo.

                # Se tudo correu bem, faz commit da transação
                # (útil quando começarmos a fazer escritas na BD)
                session.commit()
                logger.info('Processamento concluído com sucesso.')

            except Exception:
                logger.exception('Ocorreu um erro crítico durante o processamento. A fazer rollback...')
                session.rollback()  # Garante que nenhuma alteração parcial é guardada
