from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class Address(BaseModel):
    region: str = Field(..., description="Region")
    city: str = Field(..., description="City")
    street: str = Field(..., description="Street")
    house: str = Field(..., description="House")
    apartment: str = Field(..., description="Apartment")


class ServiceRequest(BaseModel):
    service_name: str = Field(...)
    cost_per_unit: float = Field(...)
    units: float = Field(...)
    total_cost: float = Field(...)


class BillRequest(BaseModel):
    first_name: str = Field(...)
    last_name: str = Field(...)
    middle_name: str = Field(...)
    account_number: str = Field(...)
    period: str = Field(...)
    total_amount: float = Field(...)
    status: str = Field(...)
    created_at: datetime = Field(...)
    paid_at: Optional[datetime] = Field(...)
    services: List[ServiceRequest]
    address: Address