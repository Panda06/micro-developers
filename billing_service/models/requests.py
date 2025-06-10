from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class BillRequest(BaseModel):
    account_number: str = Field(
        ..., description="Account number", min_length=10, max_length=10
    )
    period: Optional[str] = Field(
        None, description="Period in YYYY-MM format", pattern=r"^\d{4}-\d{2}$"
    )

    @validator("account_number")
    def validate_account_number(cls, v):
        if not v.isdigit() or len(v) != 10:
            raise ValueError("Account number must be exactly 10 digits")
        return v

    @validator("period")
    def validate_period(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, "%Y-%m")
        except ValueError:
            raise ValueError("Period must be in YYYY-MM format")
        return v


class PayBillRequest(BaseModel):
    payment_id: int = Field(..., description="Payment ID")
