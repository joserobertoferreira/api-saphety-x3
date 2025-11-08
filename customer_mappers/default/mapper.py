from core.mappers.base_mapper import BaseMapper


class DefaultMapper(BaseMapper):
    """
    Implementação padrão do mapper.

    Esta classe não contém nenhuma lógica de negócio customizada. Ela simplesmente
    herda e utiliza o comportamento padrão definido na `BaseMapper` para
    todas as operações.

    Serve como o "fallback" ou o comportamento base do sistema quando nenhum
    perfil de cliente específico é configurado.
    """

    pass
