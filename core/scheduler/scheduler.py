import logging
import time
from datetime import datetime
from typing import Any, Callable

import schedule

logger = logging.getLogger(__name__)


class Job:
    """
    A data class to encapsulate the information of a scheduled job,
    including its function, configuration, and name.

    Args:
        name: The name of the job.
        function: The function to be executed for this job.
        config: A dictionary containing the scheduling configuration for this job.
    """

    def __init__(self, name: str, function: Callable, config: dict[str, Any]):
        self.name = name
        self.function = function
        self.config = config

    def is_within_time_window(self) -> bool:
        """
        Check if the current time is within the allowed window.
        Deal with windows that span midnight. (e.g., 22:00 to 06:00)
        """
        try:
            now = datetime.now().time()
            start = datetime.strptime(self.config['START_TIME'], '%H:%M').time()
            end = datetime.strptime(self.config['END_TIME'], '%H:%M').time()
        except ValueError as e:
            logger.error(f'Formato ou chave de hora inválida na configuração: {e}')
            return False

        if start <= end:
            # Normal window (e.g., 09:00 to 17:00)
            return start <= now <= end
        else:
            # In case the window spans midnight (e.g., 22:00 to 06:00)
            return now >= start or now <= end

    def should_run(self) -> bool:
        """
        Establish if the execution should occur based on the rules
        """
        if not self.config.get('ENABLED', False):
            return False

        if not self.is_within_time_window():
            return False

        return True


class Scheduler:
    """
    Class to manage scheduled execution of a job function in specific time windows.
    """

    def __init__(self):
        """
        A class to schedule and execute multiple jobs at independent intervals
        and time windows.

        Args:
            job_function: The function to be executed periodically.
              Should not take any arguments.
            config: A dictionary containing the scheduling configuration,
            usually coming from config.SCHEDULING.
        """

        self.jobs: list[Job] = []
        logger.info('Serviço de agendamento inicializado.')

    def add_job(self, name: str, job_function: Callable, config: dict[str, Any]):
        """Regista um novo job para ser executado pelo scheduler."""
        if not config.get('ENABLED', False):
            logger.warning(f"O Job '{name}' está desativado na configuração e não será agendado.")
            return

        job = Job(name, job_function, config)
        self.jobs.append(job)

        interval = job.config.get('INTERVAL_MINUTES', 60)
        logger.info(f"""Job '{name}' adicionado ao scheduler:
        - Janela de execução: {job.config.get('START_TIME', '00:00')} às {job.config.get('END_TIME', '23:59')}
        - Intervalo: {interval} minutos""")

    def _run_job_wrapper(self, job: Job):  # noqa: PLR6301
        """
        Wrapper que verifica as condições (`should_run`) antes de executar um job.
        """
        if job.should_run():
            logger.info(f"Janela de execução ativa para o job '{job.name}'. A iniciar...")
            try:
                job.function()
                logger.info(f"Job '{job.name}' executado com sucesso.")
            except Exception:
                logger.exception(f"Ocorreu um erro não tratado durante a execução do job '{job.name}'.")
        else:
            logger.debug(f"Saltar a execução do job '{job.name}' (fora da janela de tempo permitida).")

    def start(self):
        """
        Inicia o loop principal do agendador e configura todos os jobs registados.
        """
        if not self.jobs:
            logger.warning('Nenhum job foi agendado. O scheduler não irá iniciar.')
            return

        logger.info("Configurar os agendamentos para todos os jobs no motor 'schedule'...")

        for job in self.jobs:
            interval = job.config.get('INTERVAL_MINUTES', 60)

            # Usamos uma função lambda para garantir que o objeto 'job' correto
            # é passado para o wrapper no momento da execução.
            schedule.every(interval).minutes.do(lambda j=job: self._run_job_wrapper(j))

        logger.info('Scheduler iniciado. Pressione Ctrl+C para sair.')
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info('Sinal de interrupção recebido. Encerrar o scheduler...')
