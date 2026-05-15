from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .extensions import db

_DEFAULT_BALANCE = Decimal("0.0")


class Account(db.Model):
    __tablename__: str = "accounts"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    balance: Mapped[Decimal] = mapped_column(sa.Numeric(15, 2), default=Decimal("0.0"))

    def __init__(self, name: str, balance: Decimal = _DEFAULT_BALANCE) -> None:
        super().__init__()
        self.name = name
        self.balance = balance


class Transaction(db.Model):
    __tablename__: str = "transactions"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(sa.ForeignKey("accounts.id"))
    type: Mapped[str] = mapped_column(sa.String(20))
    amount: Mapped[Decimal] = mapped_column(sa.Numeric(15, 2))
    idempotency_key: Mapped[str | None] = mapped_column(
        sa.String(100), unique=True, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime, server_default=sa.func.now()
    )

    def __init__(
        self,
        account_id: int,
        type: str,
        amount: Decimal,
        idempotency_key: str | None = None,
    ) -> None:
        super().__init__()
        self.account_id = account_id
        self.type = type
        self.amount = amount
        self.idempotency_key = idempotency_key
