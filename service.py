import logging

from config.logging import setup_logging
from config.settings import SCHEDULING
from scheduler.scheduler import Scheduler

# TODO: Importe a sua função de lógica de negócio principal aqui
# from services.processor import process_pending_invoices


# --- Função de Lógica de Negócio (Placeholder) ---
# ATENÇÃO: Esta é uma função temporária. No futuro, você irá substituí-la
# pela importação da sua função real que faz o trabalho pesado.
def process_pending_invoices():
    """
    Função principal que busca faturas pendentes, gera o XML e as envia.
    (Esta é uma implementação de exemplo/placeholder)
    """
    # Usamos o logger que já foi configurado pelo setup_logging()
    logger = logging.getLogger(__name__)
    logger.info('A executar a lógica de processamento de faturas...')
    #
    # AQUI ENTRARIA O SEU CÓDIGO REAL:
    # 1. Conectar à BD com SQLAlchemy
    # 2. Fazer a query por faturas pendentes
    # 3. Loop sobre as faturas
    # 4.    Gerar o XML com lxml
    # 5.    Enviar com requests
    # 6.    Atualizar o status na BD
    #
    logger.info('Lógica de processamento concluída (exemplo).')


def main():
    """
    Main entry point for the scheduled service.
    Sets up logging and starts the scheduler.
    """
    setup_logging()

    main_logger = logging.getLogger(__name__)
    main_logger.info('Iniciar aplicação...')

    # Create the scheduler service instance, injecting the business logic and configuration
    scheduler_service = Scheduler(
        job_function=process_pending_invoices,  # A "partitura"
        config=SCHEDULING,  # As "regras"
    )

    # Start the service. This call will block and run indefinitely.
    scheduler_service.start()

    main_logger.info('Aplicação encerrada.')


if __name__ == '__main__':
    main()
