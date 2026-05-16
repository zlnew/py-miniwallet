from datetime import datetime
from decimal import Decimal
from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class DTO(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class AccountData(DTO):
    id: int
    name: str
    balance: Decimal


class TransactionData(DTO):
    id: int
    account_id: int
    type: str
    amount: Decimal
    created_at: datetime
