import argparse
import logging

# 1. Importações da sua estrutura de projeto
from config.logging import setup_logging

# Importa a MESMA função de lógica de negócio que o serviço usa
# TODO: No futuro, virá de 'services.processor'
from services.invoice_processor import InvoiceProcessorService


# --- Função Principal da CLI ---
def main():
    """
    Ponto de entrada principal para a execução via linha de comando (CLI).
    Configura logging, interpreta argumentos e executa a lógica de negócio.
    """
    # 2. Configura o sistema de logging, tal como no serviço
    setup_logging()

    main_logger = logging.getLogger(__name__)

    # 3. Configura o parser de argumentos da linha de comando
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

    # 4. Executa a lógica de negócio
    try:
        processor = InvoiceProcessorService()

        processor.process_pending_invoices(invoice_id=args.invoice)

        # if args.invoice:
        #     main_logger.info(f'Execução por demanda iniciada para a fatura específica: {args.invoice}')
        #     # TODO: Modificar a função `process_pending_invoices` para aceitar um argumento
        #     # process_pending_invoices(invoice_id=args.invoice)
        #     process_pending_invoices()  # Por enquanto, chamamos a versão simples
        # else:
        #     main_logger.info('Execução por demanda iniciada para todas as faturas pendentes.')
        #     process_pending_invoices()

        main_logger.info('Execução concluída com sucesso.')

    except Exception:
        main_logger.exception('Ocorreu um erro crítico durante a execução por demanda.')
        # Opcionalmente, pode retornar um código de erro para o sistema que o chamou
        # import sys
        # sys.exit(1)


# --- Ponto de Execução ---
if __name__ == '__main__':
    main()
