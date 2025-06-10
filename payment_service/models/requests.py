from datetime import datetime

from pydantic import BaseModel, Field, validator


class PaymentCreate(BaseModel):
    account_number: str = Field(
        ..., description="Account number", min_length=10, max_length=10
    )
    amount: float = Field(..., description="Amount", gt=0)
    period: str = Field(..., description="Period", pattern=r"^\d{4}-\d{2}$")
    card_number: str = Field(
        ..., description="Card number", min_length=16, max_length=16
    )
    card_holder: str = Field(
        ..., description="Card holder", min_length=1, max_length=255
    )
    card_expiration_date: str = Field(
        ..., description="Card expiration date", pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    card_cvv: str = Field(..., description="Card CVV", min_length=3, max_length=4)
    inn_receiver: str = Field(
        ..., description="INN receiver", min_length=12, max_length=12
    )

    @validator("account_number")
    def validate_account_number(cls, v):
        if not v.isdigit() or len(v) != 10:
            raise ValueError("Account number must be exactly 10 digits")
        return v

    @validator("period")
    def validate_period(cls, v):
        try:
            datetime.strptime(v, "%Y-%m")
        except ValueError:
            raise ValueError("Period must be in YYYY-MM format")
        return v
