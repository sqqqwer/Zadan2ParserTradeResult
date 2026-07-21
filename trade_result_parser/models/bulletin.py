from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class Bulletin(BaseModel):
    __tablename__ = "bulletin"

    exchange_product_id: Mapped[str]
    exchange_product_name: Mapped[str]
    oil_id: Mapped[str]
    delivery_basis_id: Mapped[str]
    delivery_basis_name: Mapped[str]
    delivery_type_id: Mapped[str]
    volume: Mapped[Decimal]
    total: Mapped[Decimal]
    count: Mapped[int]
    date: Mapped[datetime]
    created_on: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_on: Mapped[datetime | None] = mapped_column(onupdate=func.now())

    __table_args__ = (
        CheckConstraint("count > 0", name="count_above_zero"),
        CheckConstraint("date >= '2023-01-01'", name="date_from_2023"),
        UniqueConstraint(
            "exchange_product_id", "date", name="exchange_product_id_date_unique"
        ),
    )
