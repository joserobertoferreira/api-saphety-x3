import logging

import lxml.etree as etree  # noqa: PLR0402

from database.database import db
from repositories.invoice_repository import SalesInvoiceRepository

logger = logging.getLogger(__name__)


class InvoiceProcessorService:
    """
    Serviço responsável por processar faturas pendentes,
    gerar o XML CIUS-PT e coordenar o envio.
    """

    def __init__(self):
        pass

    def _build_cius_pt_xml(self, invoice) -> etree._Element:  # noqa: PLR6301
        """
        Constrói a árvore XML para uma única fatura.
        (Esta é uma implementação inicial e muito simplificada).

        Args:
            invoice: O objeto SalesInvoice com os dados do cliente já carregados.

        Returns:
            Um objeto ElementTree representando o XML da fatura.
        """
        logger.info(f'A construir o XML para a fatura: {invoice.invoiceNumber}')

        # --- Definição dos Namespaces (crucial para CIUS-PT) ---
        # Estes são os namespaces padrão para UBL 2.1
        NSMAP = {
            None: 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        }

        # --- Criação do Elemento Raiz ---
        root = etree.Element('Invoice', nsmap=NSMAP)

        # --- Preenchimento do Cabeçalho (Exemplos) ---
        # Nota: etree.SubElement(parent, '{namespace}TagName')
        etree.SubElement(root, '{cbc}ID').text = invoice.invoiceNumber
        etree.SubElement(root, '{cbc}IssueDate').text = invoice.invoiceDate.strftime('%Y-%m-%d')

        # ... aqui entraria a lógica complexa para adicionar os dados do fornecedor,
        # cliente, linhas, totais, etc., extraídos do objeto `invoice`.

        logger.debug(f'XML para {invoice.invoiceNumber} construído (em memória).')
        return root

    def process_pending_invoices(self, specific_invoice_id: str | None = None):
        """
        O método principal do serviço. Orquestra todo o fluxo de processamento.
        """
        logger.info('Serviço de processamento de faturas iniciado.')

        # Obtém uma sessão da base de dados usando o nosso gestor
        with db.get_db() as session:
            try:
                # Inicializa o repositório com a sessão ativa
                repo = SalesInvoiceRepository()

                # 1. Busca as faturas pendentes
                invoices_to_process = repo.fetch_pending_invoices(session=session, invoice_number=specific_invoice_id)

                if not invoices_to_process:
                    logger.info('Nenhuma fatura pendente encontrada para processamento.')
                    return

                # 2. Itera e processa cada fatura
                for invoice in invoices_to_process:
                    # 3. Constrói o XML para a fatura atual
                    invoice_xml_tree = self._build_cius_pt_xml(invoice)

                    # Converte a árvore XML para uma string de bytes para visualização/gravação
                    xml_bytes = etree.tostring(
                        invoice_xml_tree, pretty_print=True, xml_declaration=True, encoding='UTF-8'
                    )

                    # 4. (Ação Temporária) Imprime o XML gerado para verificação
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
