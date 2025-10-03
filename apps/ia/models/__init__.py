"""
IMPORTANTE
Para contornar o problema de não encontrar a definição da classe a que o relacionamento
definido nas clausulas relationship(...), Cada classe do mapeamento deve ser declarada
na inicialização do módulo inteiro do Models.

Ref: https://stackoverflow.com/questions/9088957/sqlalchemy-cannot-find-a-class-name
"""
from apps.ia.models.conversation import Conversation  # noqa F401
from apps.ia.models.document import Document  # noqa F401
from apps.ia.models.message import Message  # noqa F401
