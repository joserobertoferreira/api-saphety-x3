import argparse
import logging
import sys

from core.config.logging import setup_logging
from core.services.invoice_processor import InvoiceProcessorService
from core.services.saphety_integration_service import SaphetyApiIntegrationService
from core.services.saphety_service import SaphetyApiService
from core.utils.generics import Generics


def main():
    """
    Ponto de entrada principal para a execução via linha de comando (CLI).
    Configura logging, interpreta argumentos e executa a lógica de negócio.
    """

    # Configura o sistema de logging, tal como no serviço
    setup_logging()

    main_logger = logging.getLogger(__name__)

    # Configura o parser de argumentos da linha de comando
    parser = argparse.ArgumentParser(
        description='Ferramenta de execução sob demanda para o envio de faturas para Saphety.',
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Só pode haver uma ação principal por execução.
    action_group = parser.add_mutually_exclusive_group()

    # Argumento opcional '--invoice'.
    # Se ele for fornecido, a nossa lógica só processará essa fatura.
    action_group.add_argument(
        '--invoice',
        type=str,
        metavar='INVOICE_ID',
        help="Opcional. O ID da fatura específica a ser processada (ex: 'FAT/2024/001').",
    )

    # Argumento opcional '--check'
    # Se ele for fornecido, será feita a verificação do estado para essa fatura.
    action_group.add_argument(
        '--check',
        nargs='?',
        const='CHECK_ALL',
        default=None,
        type=str,
        metavar='INVOICE_ID',
        required=False,
        help='Mode verificação:\n'
        '--check: Verifica o status de todas as faturas.\n'
        '--check INVOICE_ID: Verifica o status de uma fatura específica.',
    )

    try:
        args = parser.parse_args()
    except SystemExit as e:
        # argparse usa o código de saída 2 para erros de argumento.
        # Um código 0 significa um sys.exit() normal (ex: de --help).
        if e.code != 0:
            main_logger.error('Erro ao interpretar os argumentos da linha de comando. Verifique a sintaxe.')
            # O erro já foi impresso no console pelo argparse, aqui apenas logamos.

        # Garantimos que o script termine com o código de erro apropriado.
        # Isso encerra a aplicação de forma controlada após o logging.
        sys.exit(e.code)

    try:
        # Lógica de execução baseada no grupo de ações

        # Cenário 1: Modo de Verificação foi ativado (--check ou --check <ID>)
        if args.check is not None:
            if args.check == 'CHECK_ALL':
                main_logger.info('Modo de verificação de status ativado para TODAS as faturas.')
            else:
                main_logger.info(f'Modo de verificação de status ativado para a fatura: {args.check}')

            integration_service = SaphetyApiIntegrationService()

            # Supondo que seu método `verify_invoice_status` aceite um ID opcional
            integration_service.verify_invoice_status(invoice_id=args.check)

        # Cenário 2: Modo de Processamento/Envio de fatura única foi ativado
        elif args.invoice:
            main_logger.info(f'Modo de processamento e envio para a fatura específica: {args.invoice}')

            customer_mapper = Generics.get_customer_mapper()
            processor = InvoiceProcessorService(customer_mapper=customer_mapper)
            processor.process_pending_invoices(invoice_id=args.invoice)
            main_logger.info(f'Processamento concluído para a fatura {args.invoice}.')

            saphety_service = SaphetyApiService()
            saphety_service.send_pending_invoices(invoice_id=args.invoice)
            main_logger.info(f'Tentativa de envio concluída para a fatura {args.invoice}.')

        # Cenário 3: Nenhum argumento foi passado, comportamento padrão
        else:
            main_logger.info('Modo padrão: processar e enviar todas as faturas pendentes.')

            customer_mapper = Generics.get_customer_mapper()
            processor = InvoiceProcessorService(customer_mapper=customer_mapper)
            processor.process_pending_invoices()
            main_logger.info('Processamento de faturas pendentes concluído.')

            saphety_service = SaphetyApiService()
            saphety_service.send_pending_invoices()
            main_logger.info('Envio de faturas pendentes concluído.')

        main_logger.info('Execução concluída com sucesso.')

    except Exception:
        main_logger.exception('Ocorreu um erro crítico durante a execução por demanda.')
        sys.exit(1)

    main_logger.info('Execução concluída com sucesso.')


if __name__ == '__main__':
    main()
