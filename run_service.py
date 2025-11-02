import logging

from config.logging import setup_logging
from config.settings import SCHEDULING
from scheduler.scheduler import Scheduler
from services.invoice_processor import InvoiceProcessorService


def main():
    """
    Ponto de entrada principal para o serviço agendado.
    Configura o logging e inicia o agendador.
    """
    setup_logging()

    main_logger = logging.getLogger(__name__)
    main_logger.info('Iniciar aplicação...')

    # Cria uma instância do serviço de processamento de faturas
    processor = InvoiceProcessorService()

    # Crie a instância do serviço de agendamento
    scheduler_service = Scheduler(
        job_function=processor.process_pending_invoices,
        config=SCHEDULING,
    )

    # Inicia o serviço. Esta chamada irá bloquear e executar indefinidamente.
    scheduler_service.start()

    main_logger.info('Aplicação encerrada.')


if __name__ == '__main__':
    main()
