"""Model for processed text by AI."""
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.core.utils.base_model import AbstractBaseModel

if TYPE_CHECKING:
    from apps.core.models.user import User


class ProcessedText(AbstractBaseModel):
    """Model for processed text by AI."""

    __tablename__ = 'processed_data'

    id: Mapped[int] = mapped_column(primary_key=True, name='id')
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'), name='user_id', nullable=False
    )
    input_text: Mapped[str] = mapped_column(index=True, name='input_text')
    processed_result: Mapped[str | None] = mapped_column(
        name='processed_result'
    )

    user: Mapped['User'] = relationship(
        back_populates='processed_text_entries', lazy='subquery'
    )
