import argparse
import logging

from core.config.logging import setup_logging
from core.services.invoice_processor import InvoiceProcessorService
from core.services.saphety_service import SaphetyApiClient
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
    parser = argparse.ArgumentParser(description='Ferramenta de execução sob demanda para o envio de faturas CIUS-PT.')

    # Adicionamos um argumento opcional '--invoice'.
    # Se ele for fornecido, a nossa lógica só processará essa fatura.
    parser.add_argument(
        '--invoice',
        type=str,
        required=False,
        help="Opcional. O ID da fatura específica a ser processada (ex: 'FAT/2024/001').",
    )

    args = parser.parse_args()

    if args.invoice:
        main_logger.info(f'Execução por demanda iniciada para a fatura: {args.invoice}')
    else:
        main_logger.info('Execução por demanda iniciada para as faturas pendentes.')

    # Executa a lógica de negócio
    try:
        # Chama o mapper específico para o cliente se for o caso
        customer_mapper = Generics.get_customer_mapper()

        # Injeta o mapper para criar o serviço com o comportamento correto
        processor = InvoiceProcessorService(customer_mapper=customer_mapper)

        main_logger.info('Processar faturas pendentes')
        processor.process_pending_invoices(invoice_id=args.invoice)

    except Exception:
        main_logger.exception('Ocorreu um erro crítico durante a execução por demanda.')
        # Opcionalmente, pode retornar um código de erro para o sistema que o chamou
        # import sys
        # sys.exit(1)

    try:
        # Cria o serviço de envio de faturas
        saphety_client = SaphetyApiClient()

        main_logger.info('Enviar faturas para Saphety')
        saphety_client.send_pending_invoices(invoice_id=args.invoice)

    except Exception:
        main_logger.exception('Ocorreu um erro na fase de envio.')

    main_logger.info('Execução concluída com sucesso.')


if __name__ == '__main__':
    main()
