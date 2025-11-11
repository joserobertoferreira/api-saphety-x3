import logging

from core.config.logging import setup_logging
from core.config.settings import SCHEDULING_CHECK_STATUS, SCHEDULING_PROCESS
from core.scheduler.scheduler import Scheduler
from core.services.invoice_processor import InvoiceProcessorService
from core.services.saphety_integration_service import SaphetyApiIntegrationService
from core.services.saphety_service import SaphetyApiService
from core.utils.generics import Generics


def job_process():
    """
    Job 1: Define um ciclo de trabalho completo: primeiro processa, depois envia.
    Esta função será chamada pelo scheduler a cada intervalo.
    """

    logger = logging.getLogger(__name__)
    logger.info('[JOB: ProcessSend] Iniciar ciclo de processamento e envio...')

    # Executa a lógica de negócio
    try:
        # Chama o mapper específico para o cliente se for o caso
        customer_mapper = Generics.get_customer_mapper()

        # Cria uma instância do serviço de processamento de faturas
        processor = InvoiceProcessorService(customer_mapper=customer_mapper)

        # Processa as faturas pendentes
        processor.process_pending_invoices()

        logger.info('[JOB: ProcessSend] Processamento de faturas pendentes concluído.')
    except Exception:
        logger.exception(
            '[JOB: ProcessSend] Ocorreu um erro na fase de processamento. O ciclo continuará na fase de envio.'
        )

    try:
        # Cria o serviço de envio de faturas
        saphety_client = SaphetyApiService()

        # Envia as faturas pendentes
        saphety_client.send_pending_invoices()

        logger.info('[JOB: ProcessSend] Envio de faturas pendentes concluído.')
    except Exception:
        logger.exception('[JOB: ProcessSend] Ocorreu um erro na fase de envio.')


def job_check_status():
    """
    Job 2: Ciclo de verificação de status das faturas já enviadas.
    """
    logger = logging.getLogger(__name__)
    logger.info('[JOB: CheckStatus] Iniciando ciclo de verificação de status...')

    try:
        integration_service = SaphetyApiIntegrationService()
        integration_service.verify_invoice_status()
        logger.info('[JOB: CheckStatus] Verificação de status concluída com sucesso.')
    except Exception:
        logger.exception('[JOB: CheckStatus] Ocorreu um erro durante a verificação de status.')

    logger.info('[JOB: CheckStatus] Ciclo concluído.')


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
        scheduler_service = Scheduler()

        # Adiciona os jobs ao agendador com base na configuração
        if SCHEDULING_PROCESS['ENABLED']:
            scheduler_service.add_job(
                name='ProcessSendCycle',
                job_function=job_process,
                config=SCHEDULING_PROCESS,
            )

        if SCHEDULING_CHECK_STATUS['ENABLED']:
            scheduler_service.add_job(
                name='CheckStatusCycle', job_function=job_check_status, config=SCHEDULING_CHECK_STATUS
            )

        # Inicia o serviço. Esta chamada irá bloquear e executar indefinidamente.
        scheduler_service.start()

    except Exception:
        main_logger.exception('O serviço encontrou um erro fatal e vai ser encerrado.')


if __name__ == '__main__':
    main()
