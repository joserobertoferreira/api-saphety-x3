import argparse
import logging

from config.logging import setup_logging

# Importa a MESMA função de lógica de negócio que o serviço usa
# TODO: No futuro, virá de 'services.processor'
from run_service import process_pending_invoices


def main():
    """
    Main entry point for command-line (CLI) execution.
    Sets up logging, parses arguments, and runs the business logic.
    """
    setup_logging()

    main_logger = logging.getLogger(__name__)

    # Setup the command-line argument parser
    parser = argparse.ArgumentParser(description='Ferramenta de execução sob demanda para o envio de faturas CIUS-PT.')

    # The optional argument '--invoice', if provided, will limit processing to that specific invoice.
    parser.add_argument(
        '--invoice',
        type=str,
        required=False,
        help="Opcional. O ID da fatura específica a ser processada (ex: 'FAT-2024/001').",
    )

    args = parser.parse_args()

    # Execute the business logic
    try:
        if args.invoice:
            main_logger.info(f'Execução por demanda iniciada para a fatura específica: {args.invoice}')
            # TODO: Modificar a função `process_pending_invoices` para aceitar um argumento
            # process_pending_invoices(invoice_id=args.invoice)
            process_pending_invoices()  # Por enquanto, chamamos a versão simples
        else:
            main_logger.info('Execução por demanda iniciada para todas as faturas pendentes.')
            process_pending_invoices()

        main_logger.info('Execução concluída com sucesso.')

    except Exception:
        main_logger.exception('Ocorreu um erro crítico durante a execução por demanda.')
        # Opcionalmente, pode retornar um código de erro para o sistema que o chamou
        # import sys
        # sys.exit(1)


if __name__ == '__main__':
    main()
