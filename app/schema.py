from decimal import Decimal

from pydantic import BaseModel, Field, PositiveInt


class AccountCreateRequest(BaseModel):
    name: str = Field(max_length=100)
    balance: Decimal = Field(default=Decimal("0.0"), ge=0)


class AccountUpdateRequest(BaseModel):
    name: str = Field(max_length=100)


class TransactionGetRequest(BaseModel):
    account_id: PositiveInt


class TopUpRequest(BaseModel):
    account_id: PositiveInt
    amount: Decimal = Field(gt=0)


class TransferRequest(BaseModel):
    from_account_id: PositiveInt
    to_account_id: PositiveInt
    amount: Decimal = Field(gt=0)
