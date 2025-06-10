from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PaymentResponse(BaseModel):
    id: int
    payment_id: str
    account_number: str
    amount: float
    period: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
