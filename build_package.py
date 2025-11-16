import argparse
import shutil
import sys
from pathlib import Path


def main():  # noqa: PLR0914, PLR0915
    """
    Script para criar um pacote de deploy limpo para um cliente específico.
    """
    # Configuração dos Argumentos da Linha de Comando
    parser = argparse.ArgumentParser(description='Cria um pacote de deploy para um cliente específico.')
    parser.add_argument('-c', '--customer', required=True, help="O nome do perfil do cliente (ex: 'mop').")
    args = parser.parse_args()
    customer_profile = args.customer

    # Configuração dos Caminhos
    project_root = Path(__file__).resolve().parent
    deploy_root = project_root / 'build'
    deploy_package_path = deploy_root / customer_profile

    print('=' * 50)
    print(f'Criar pacote de deploy para o cliente: {customer_profile}')
    print('=' * 50)

    # Limpeza
    if deploy_package_path.exists():
        print(f'Limpar a pasta de deploy anterior: {deploy_package_path}')
        # shutil.rmtree é a forma robusta de apagar uma pasta e todo o seu conteúdo
        shutil.rmtree(deploy_package_path)

    print('Criar nova pasta de deploy...')
    deploy_package_path.mkdir(parents=True)

    # Cópia dos Ficheiros e Pastas

    # Defina aqui as pastas dentro de 'core' que você NÃO quer copiar.
    # Ex: ['tests', 'docs_internos']
    core_folders_to_exclude: list[str] = ['output']

    # 1. Copia o código do 'core'
    print("1. Copiar a pasta 'core'...")
    source_core = project_root / 'core'
    dest_core = deploy_package_path / 'core'

    exclude_set: set[str] = set(core_folders_to_exclude)

    def ignore_core_folders(directory: str, contents: list[str]) -> list[str]:
        """
        Função de ignore para shutil.copytree.

        Args:
            directory: O caminho do diretório que está a ser percorrido.
            contents: A lista de nomes de ficheiros/pastas dentro desse diretório.

        Returns:
            Uma lista de nomes de ficheiros/pastas a serem ignorados.
        """
        ignored_items: list[str] = []

        # Otimização: Só aplicamos a lógica se estivermos no diretório 'core' raiz
        if Path(directory) == source_core:
            for item in contents:
                # Se um item na pasta 'core' estiver na nossa lista de exclusão
                if item in exclude_set:
                    ignored_items.append(item)
                    print(f'   - ignorar a pasta: {item}')

        # Adiciona os padrões de sempre (__pycache__, etc.)
        default_ignores = shutil.ignore_patterns('__pycache__', '*.pyc')
        ignored_items.extend(default_ignores(directory, contents))

        return ignored_items

    # shutil.copytree lida com a cópia recursiva e ignora padrões
    if core_folders_to_exclude:
        ignore_function = ignore_core_folders
    else:
        ignore_function = shutil.ignore_patterns('__pycache__', '*.pyc')

    shutil.copytree(source_core, dest_core, ignore=ignore_function)

    # 2. Copia os scripts de execução da raiz
    print('2. Copiar scripts de execução...')
    for script_name in ['run_cli.py', 'run_service.py']:
        shutil.copy(project_root / script_name, deploy_package_path)

    # 3. Copia os ficheiros de dependências
    print('3. Copiar ficheiros de requisitos...')
    shutil.copy(project_root / 'requirements.txt', deploy_package_path)

    # 4. Copia a customização do cliente
    print(f"4. Copiar a customização do cliente '{customer_profile}'...")
    source_customer_path = project_root / 'customer_mappers' / customer_profile
    dest_customer_path = deploy_package_path / 'customer_mappers'

    if not source_customer_path.is_dir():
        print(f"ERRO: A pasta de customização '{source_customer_path}' não foi encontrada.", file=sys.stderr)
        sys.exit(1)

    shutil.copytree(source_customer_path, dest_customer_path, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))

    # 5. (Opcional) Copia o mapper 'default'
    print("5. Copiar o mapper 'default'...")
    source_default_path = project_root / 'customer_mappers' / 'default'
    dest_default_path = deploy_package_path / 'customer_mappers' / 'default'
    shutil.copytree(source_default_path, dest_default_path, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))

    # 6. Copia o ficheiro .env.example
    print('6. Copiar o ficheiro .env.example...')
    source_env_example = project_root / '.env.example'
    if source_env_example.is_file():
        shutil.copy(source_env_example, deploy_package_path / '.env')
    else:
        print("AVISO: Ficheiro '.env.example' não encontrado.")

    print('\n' + '-' * 50)
    print(f"Pacote de deploy para '{customer_profile}' criado com sucesso em:")
    print(str(deploy_package_path))
    print('-' * 50)
    print('Próximos passos:')
    print(f"1. Edite o ficheiro '.env' dentro da pasta '{deploy_package_path}'.")
    print(f"2. Copie a pasta '{deploy_package_path}' para o servidor.")


if __name__ == '__main__':
    main()
