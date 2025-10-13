"""Database Schema Introspection Tool for CrewAI agents."""

from crewai.tools import tool
from sqlalchemy import create_engine, inspect

from apps.packpage.settings import get_settings


@tool('db_schema_inspector')
def db_schema_inspector(table_name: str = None) -> str:
    """
    Use esta ferramenta para descobrir a estrutura das tabelas do banco de dados.
    Retorna informações sobre colunas, tipos e relacionamentos.

    Args:
        table_name (str, optional): Nome específico da tabela para inspecionar.
                                   Se não fornecido, lista todas as tabelas.

    Returns:
        str: Estrutura das tabelas em formato texto.
    """
    settings = get_settings()
    engine = create_engine(settings.DB_URL)
    inspector = inspect(engine)

    try:
        if table_name:
            if table_name not in inspector.get_table_names():
                return (
                    f'Tabela "{table_name}" não encontrada. '
                    f'Tabelas disponíveis: {", ".join(inspector.get_table_names())}'
                )

            columns = inspector.get_columns(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            indexes = inspector.get_indexes(table_name)

            result = f'=== ESTRUTURA DA TABELA: {table_name} ===\n\n'
            result += 'COLUNAS:\n'
            for col in columns:
                nullable = '' if col['nullable'] else ' NOT NULL'
                default = (
                    f" DEFAULT {col['default']}" if col.get('default') else ''
                )
                result += (
                    f'  - {col["name"]}: {col["type"]}{nullable}{default}\n'
                )

            if foreign_keys:
                result += '\nCHAVES ESTRANGEIRAS:\n'
                for fk in foreign_keys:
                    result += (
                        f'  - {fk["constrained_columns"]} -> '
                        f'{fk["referred_table"]}.{fk["referred_columns"]}\n'
                    )

            if indexes:
                result += '\nÍNDICES:\n'
                for idx in indexes:
                    result += f'  - {idx["name"]}: {idx["column_names"]}\n'

            return result
        else:
            table_names = inspector.get_table_names()
            result = '=== TABELAS DISPONÍVEIS ===\n\n'

            for table in table_names:
                result += f'- {table}\n'

                if 'paint' in table.lower():
                    columns = inspector.get_columns(table)
                    result += '  Colunas principais:\n'
                    for col in columns[:5]:
                        result += f'    {col["name"]} ({col["type"]})\n'
                    if len(columns) > 5:
                        result += (
                            f'    ... e mais {len(columns) - 5} colunas\n'
                        )
                    result += '\n'

            return result

    except Exception as e:
        return f'Erro ao inspecionar banco: {str(e)}'
    finally:
        engine.dispose()
