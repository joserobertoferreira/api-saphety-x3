import logging
from pprint import pprint

# Configure o logging para podermos ver as mensagens
from config.logging import setup_logging

# Importe o seu gestor de base de dados
from database.database import db

# Importe o repositório que queremos testar
from repositories.invoice_repository import SalesInvoiceRepository


def run_test():
    """
    Função principal de teste que executa a busca de faturas.
    """
    logger = logging.getLogger(__name__)
    logger.info('--- INICIANDO TESTE DO REPOSITÓRIO DE FATURAS ---')

    # `db` é o seu DatabaseManager inicializado em database.py
    if not db:
        logger.error('A conexão com a base de dados não foi inicializada. Verifique config/database.py.')
        return

    # O `with db.get_db() as session:` garante que a sessão é
    # criada e fechada corretamente. É a forma correta de usar o seu DatabaseManager.
    with db.get_db() as session:
        try:
            logger.info('Sessão da base de dados obtida. A criar instância do repositório...')

            # 1. Crie uma instância do repositório, passando a sessão ativa
            invoice_repo = SalesInvoiceRepository()

            # 2. Chame o método que queremos testar
            # Deixe o argumento em branco para buscar todas as faturas pendentes
            pending_invoices = invoice_repo.fetch_pending_invoices(session)

            # 3. Verifique e imprima os resultados
            if not pending_invoices:
                logger.warning('Nenhuma fatura pendente foi encontrada. O teste foi bem-sucedido, mas sem resultados.')
            else:
                logger.info(f'SUCESSO! Foram encontradas {len(pending_invoices)} faturas pendentes.')
                for i, inv in enumerate(pending_invoices):
                    print(f'\n--- INSPECIONANDO FATURA #{i + 1} ---')

                    # 1. Imprime os atributos carregados do objeto SalesInvoice
                    print("Atributos carregados em 'SalesInvoice':")
                    # O `inv.__dict__` contém o estado do objeto.
                    # Usamos `pprint` para formatar a saída de forma legível.
                    # Filtramos o item '_sa_instance_state' que é interno do SQLAlchemy.
                    invoice_data = {k: v for k, v in inv.__dict__.items() if not k.startswith('_')}
                    pprint(invoice_data)

                    # 2. Imprime os atributos carregados do objeto Customer relacionado
                    if inv.customer:
                        print("\nAtributos carregados em 'Customer' (relacionado):")
                        customer_data = {k: v for k, v in inv.customer.__dict__.items() if not k.startswith('_')}
                        pprint(customer_data)
                    else:
                        print("\nNenhum 'Customer' relacionado foi carregado.")

        except Exception:
            logger.exception('Ocorreu um erro durante o teste do repositório.')
            # O `with` statement garante que a sessão é fechada, mas não faz rollback.
            # Em código real, teríamos um rollback aqui.
            session.rollback()

    logger.info('--- TESTE CONCLUÍDO ---')


if __name__ == '__main__':
    # Configura o logging antes de qualquer outra coisa
    setup_logging()
    run_test()
