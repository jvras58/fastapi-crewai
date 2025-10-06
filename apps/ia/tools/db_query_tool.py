"""DB Query Tool for CrewAI agents."""

import re

from crewai.tools import tool
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine

from apps.packpage.settings import get_settings

ALLOWED_TABLES = {
    'ia_documents',
    'ia_conversations',
    'ia_messages',
}

ALLOWED_VIEWS = {
    # TODO: Adicionar views conforme necessário
}

# Todas as entidades permitidas (tabelas + views)
ALLOWED_ENTITIES = ALLOWED_TABLES | ALLOWED_VIEWS


@tool('db_query')
def db_query_tool(query: str) -> str:
    """
    Use esta ferramenta para consultar o banco de dados SQL.
    Fornece resultados de queries SQL seguras apenas para tabelas e views específicas.
    Suporta queries com WITH (CTEs) e consultas a views.

    Tabelas permitidas: ia_documents, ia_conversations, ia_messages
    Views permitidas: (configure em ALLOWED_VIEWS)

    Args:
        query (str): A query SQL para executar no banco de dados.

    Returns:
        str: Resultados da query em formato texto.
    """
    if not _is_query_safe(query):
        return f"Erro: Query só pode acessar tabelas/views: {', '.join(ALLOWED_ENTITIES)}"

    settings = get_settings()
    engine = create_engine(settings.DB_URL)

    db = SQLDatabase(
        engine=engine,
        include_tables=list(ALLOWED_TABLES),
        view_support=True,
    )

    try:
        result = db.run_no_throw(query)
        return str(result) if result else 'Nenhum resultado encontrado.'
    except Exception as e:
        return f'Erro ao executar query: {str(e)}'
    finally:
        engine.dispose()


def _is_query_safe(query: str) -> bool:
    """
    Valida se a query só acessa entidades permitidas.
    Suporta WITH (CTEs) e views.

    Args:
        query: Query SQL para validar

    Returns:
        bool: True se a query é segura, False caso contrário
    """
    query_lower = query.lower()

    query_stripped = query_lower.strip()
    if not (
        query_stripped.startswith('select')
        or query_stripped.startswith('with')
    ):
        return False

    table_patterns = [
        r'\bfrom\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        r'\bjoin\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        r'\binner\s+join\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        r'\bleft\s+join\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        r'\bright\s+join\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        r'\bfull\s+join\s+([a-zA-Z_][a-zA-Z0-9_]*)',
    ]

    referenced_entities = set()

    for pattern in table_patterns:
        matches = re.findall(pattern, query_lower)
        referenced_entities.update(matches)

    for entity in referenced_entities:
        if entity and entity not in ALLOWED_ENTITIES:
            return False

    dangerous_keywords = [
        r'\binsert\b',
        r'\bupdate\b',
        r'\bdelete\b',
        r'\bdrop\b',
        r'\balter\b',
        r'\bcreate\b',
        r'\btruncate\b',
        r'\bexec\b',
    ]

    return all(
        not re.search(keyword, query_lower) for keyword in dangerous_keywords
    )
