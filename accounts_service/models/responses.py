from datetime import datetime

from pydantic import BaseModel


class AccountResponse(BaseModel):
    id: int
    account_number: str
    address: str
    owner_name: str
    area: float
    residents_count: int
    management_company: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
