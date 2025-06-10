from datetime import datetime

from pydantic import BaseModel, Field


def validate_date_format(date_str: str) -> str:
    """Validate date in YYYY-MM-DD format with comprehensive checks."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")

        year, month, day = map(int, date_str.split("-"))

        if not (1800 < year < 2200):
            raise ValueError("Year must be between 1800 and 2200")

        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12")

        days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        if day > days_in_month[month - 1]:
            raise ValueError(f"Day {day} is invalid for month {month}")

        return date_str
    except ValueError as e:
        raise ValueError(f"Invalid date format or value: {e}")


class PaymentRequest(BaseModel):
    amount: float = Field(..., description="Amount", gt=0)
    card_number: str = Field(
        ..., description="The number of the card", min_length=16, max_length=16
    )
    card_holder: str = Field(
        ..., description="The holder of the card", min_length=1, max_length=255
    )
    card_expiration_date: str = Field(
        ...,
        description="The expiration date of the card in the format YYYY-MM-DD",
        min_length=10,
        max_length=10,
        validators=[lambda v: validate_date_format(v)],
    )
    card_cvv: str = Field(
        ..., description="The CVV of the card", min_length=3, max_length=4
    )
    inn_receiver: str = Field(
        ..., description="Receiver inn", min_length=12, max_length=12
    )
