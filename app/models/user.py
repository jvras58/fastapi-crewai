from typing import TYPE_CHECKING

from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils.base_model import AbstractBaseModel

if TYPE_CHECKING:
    from app.models.assignment import Assignment
    from app.models.processed_data import ProcessedData


class User(AbstractBaseModel):
    """
    Representa a tabela Usuário no banco de dados.
    """

    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, name='id')
    display_name: Mapped[str] = mapped_column(name='str_display_name')
    username: Mapped[str] = mapped_column(name='str_username')
    password: Mapped[str] = mapped_column(name='str_password')
    email: Mapped[str] = mapped_column(name='str_email')

    assignments: Mapped[list['Assignment']] = relationship(
        back_populates='user', lazy='subquery'
    )
    processed_data_entries: Mapped[list['ProcessedData']] = relationship(
        back_populates='user', lazy='subquery'
    )
    __table_args__ = (
        Index('idx_user_username', username, unique=True),
        Index('idx_user_email', email, unique=True),
    )
