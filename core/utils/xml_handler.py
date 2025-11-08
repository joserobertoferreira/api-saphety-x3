import logging
from pathlib import Path

import lxml.etree as etree  # noqa: PLR0402

from core.config.settings import OUTPUT_DIRECTORY

# Configurar logging
logger = logging.getLogger(__name__)


class XMLHandler:
    def __init__(self):
        pass

    @staticmethod
    def save_xml_to_file(xml_tree: etree._Element, filename: str) -> Path:
        """
        Guarda uma árvore XML num ficheiro na pasta de saída configurada.

        Args:
            xml_tree: A árvore de elementos lxml a ser guardada.
            invoice_number: O número da fatura, usado para nomear o ficheiro.

        Returns:
            O caminho (Path object) para o ficheiro que foi criado.

        Raises:
            IOError: Se ocorrer um problema ao escrever o ficheiro.
        """

        # Constrói o caminho completo para o ficheiro de saída
        output_path = OUTPUT_DIRECTORY / filename

        logger.debug(f'Guardar o XML da fatura {filename} em: {output_path}')

        try:
            # Converte a árvore para bytes com a formatação desejada
            xml_bytes = etree.tostring(xml_tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')

            # Escreve os bytes no ficheiro
            with open(output_path, 'wb') as f:
                f.write(xml_bytes)

            logger.info(f'Ficheiro XML para a fatura {filename} gerado com sucesso.')
            return output_path

        except Exception as e:
            logger.exception(f'Falha ao guardar o ficheiro XML para a fatura {filename}.')
            # Relança a exceção para que o processo principal possa fazer rollback
            raise IOError(f'Não foi possível escrever o ficheiro {output_path}: {e}') from e

    @staticmethod
    def check_for_xml_files(filename: str | None = None) -> list[Path]:
        """
        Verifica a existência de ficheiros XML na pasta de saída.

        Args:
            filename (str | None, optional): Nome específico do ficheiro a verificar. Defaults to None.

        Returns:
            list[Path]: Lista de caminhos para os ficheiros XML encontrados.
        """
        xml_files = []

        if filename:
            file_path = OUTPUT_DIRECTORY / filename
            if file_path.exists() and file_path.suffix == '.xml':
                xml_files.append(file_path)
                logger.debug(f'Ficheiro XML encontrado: {file_path}')
            else:
                logger.debug(f'Ficheiro XML não encontrado: {file_path}')
        else:
            for file in OUTPUT_DIRECTORY.glob('*.xml'):
                xml_files.append(file)
                logger.debug(f'Ficheiro XML encontrado: {file}')

        return xml_files
