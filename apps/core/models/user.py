"""Model for represents the User."""
from typing import TYPE_CHECKING

from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.packpage.base_model import AbstractBaseModel

if TYPE_CHECKING:
    from apps.core.models.assignment import Assignment
    from apps.ia.models.conversation import Conversation


class User(AbstractBaseModel):
    """
    Represents the User (Usuário) table in the database.
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
    conversations: Mapped[list['Conversation']] = relationship(
        'Conversation', back_populates='user', lazy='select'
    )
    __table_args__ = (
        Index('idx_user_username', username, unique=True),
        Index('idx_user_email', email, unique=True),
    )
