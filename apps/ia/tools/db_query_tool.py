"""DB Query Tool for CrewAI agents."""

from crewai.tools import tool
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine

from apps.packpage.settings import get_settings


@tool('db_query')
def db_query_tool(query: str) -> str:
    """
    Use esta ferramenta para consultar o banco de dados SQL.
    Fornece resultados de queries SQL seguras.

    Args:
        query (str): A query SQL para executar no banco de dados.

    Returns:
        str: Resultados da query em formato texto.
    """
    settings = get_settings()
    engine = create_engine(settings.DB_URL)
    db = SQLDatabase(engine=engine)

    try:
        result = db.run_no_throw(query)
        return str(result) if result else "Nenhum resultado encontrado."
    except Exception as e:
        return f"Erro ao executar query: {str(e)}"
    finally:
        engine.dispose()
