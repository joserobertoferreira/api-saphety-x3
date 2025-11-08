import logging

from core.config.logging import setup_logging
from core.config.settings import SCHEDULING
from core.scheduler.scheduler import Scheduler
from core.services.invoice_processor import InvoiceProcessorService
from core.services.saphety_service import SaphetyApiClient
from core.utils.generics import Generics


def job_cycle():
    """
    Define um ciclo de trabalho completo: primeiro processa, depois envia.
    Esta função será chamada pelo scheduler a cada intervalo.
    """

    logger = logging.getLogger(__name__)

    # Executa a lógica de negócio
    try:
        # Chama o mapper específico para o cliente se for o caso
        customer_mapper = Generics.get_customer_mapper()

        # Cria uma instância do serviço de processamento de faturas
        processor = InvoiceProcessorService(customer_mapper=customer_mapper)

        # Processa as faturas pendentes
        processor.process_pending_invoices()

    except Exception:
        logger.exception('Ocorreu um erro na fase de processamento. O ciclo continuará na fase de envio.')

    try:
        # Cria o serviço de envio de faturas
        saphety_client = SaphetyApiClient()

        # Envia as faturas pendentes
        saphety_client.send_pending_invoices()

    except Exception:
        logger.exception('Ocorreu um erro na fase de envio.')


def main():
    """
    Ponto de entrada principal para o serviço agendado.
    Configura o logging e inicia o agendador.
    """
    setup_logging()

    main_logger = logging.getLogger(__name__)

    try:
        main_logger.info('Iniciar aplicação em modo agendado...')

        # Crie a instância do serviço de agendamento
        scheduler_service = Scheduler(
            job_function=job_cycle,
            config=SCHEDULING,
        )

        # Inicia o serviço. Esta chamada irá bloquear e executar indefinidamente.
        scheduler_service.start()

    except Exception:
        main_logger.exception('O serviço encontrou um erro fatal e vai ser encerrado.')


if __name__ == '__main__':
    main()
