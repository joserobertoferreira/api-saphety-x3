import logging
import time
from datetime import datetime
from typing import Any, Callable, Dict, Optional

import schedule


class Scheduler:
    """
    Class to manage scheduled execution of a job function in specific time windows.
    """

    def __init__(self, job_function: Callable[[], None], config: Dict[str, Any]):
        """
        Initializes the Scheduler.

        Args:
            job_function: The function to be executed periodically.
                  Should not take any arguments.
            config: A dictionary containing the scheduling configuration,
                usually coming from config.SCHEDULING.
        """

        self.job_function = job_function
        self.config = config
        self.window_closed_timestamp: Optional[datetime] = None
        self.logger = logging.getLogger(__name__)

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
            self.logger.error(f'Formato ou chave de hora inválida na configuração: {e}')
            return False

        if start <= end:
            # Normal window (e.g., 09:00 to 17:00)
            return start <= now <= end
        else:
            # In case the window spans midnight (e.g., 22:00 to 06:00)
            return now >= start or now <= end

    def _should_run(self) -> bool:
        """
        Establish if the execution should occur based on the rules
        """
        if not self.config.get('ENABLED', False):
            return False

        if not self.is_within_time_window():
            return False

        return True

    def _scheduled_job(self):
        """
        Wrapper to execute the main job function with error handling.
        It's check if the conditions (`should_run`) are met before executing.
        """
        if self._should_run():
            try:
                self.logger.info('Janela de execução ativa. Iniciar o job...')
                self.job_function()
                self.logger.info('Job executado com sucesso.')
            except Exception:
                self.logger.exception('Ocorreu um erro não tratado durante a execução do job.')
        else:
            self.logger.info('Execução não permitida no momento (configuração ou horário inválido)')

    def start(self):
        """
        Start the scheduler with the defined configurations.
        """
        if not self.config.get('ENABLED', False):
            self.logger.info('Agendamento desativado nas configurações. O serviço não será iniciado.')
            return

        # Scheduler periodic job
        interval = self.config.get('INTERVAL_MINUTES', 60)

        self.logger.info(f"""Agendamento configurado:
        - Janela de execução: {self.config.get('START_TIME', '00:00')} às {self.config.get('END_TIME', '23:59')}
        - Intervalo: {interval} minutos
        - Agendamento {'ativo' if self.config.get('ENABLED', False) else 'inativo'}
        """)

        schedule.every(interval).minutes.do(self._scheduled_job)

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info('Recebido sinal de interrupção. Encerrar o serviço...')
        except Exception as e:
            self.logger.error(f'Erro inesperado no scheduler: {e}')
            raise
