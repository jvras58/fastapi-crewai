"""
IMPORTANTE
Para contornar o problema de não encontrar a definição da classe a que o relacionamento
definido nas clausulas relationship(...), Cada classe do mapeamento deve ser declarada
na inicialização do módulo inteiro do Models.

Ref: https://stackoverflow.com/questions/9088957/sqlalchemy-cannot-find-a-class-name
"""
from apps.models.assignment import Assignment  # noqa F401
from apps.models.authorization import Authorization  # noqa F401
from apps.models.processed_text import ProcessedText  # noqa F401
from apps.models.role import Role  # noqa F401
from apps.models.transaction import Transaction  # noqa F401
from apps.models.user import User  # noqa F401
