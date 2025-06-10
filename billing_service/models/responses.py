from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ServiceResponse(BaseModel):
    service_name: str
    cost_per_unit: float
    units: float
    total_cost: float


class BillResponse(BaseModel):
    account_number: str
    period: str
    total_amount: float
    status: str
    created_at: datetime
    paid_at: Optional[datetime]
    services: List[ServiceResponse]