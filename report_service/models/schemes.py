from datetime import datetime
from pydantic import BaseModel, Field


# • ФИО и адрес плательщика
# • Период оплаты
# • Таблица с услугами и суммами
# • Итоговая сумма
# • Дата формирования


class AddressRequest(BaseModel):
    region: str = Field(...)
    city: str = Field(...)
    street: str = Field(...)
    house: str = Field(...)
    apartment: str = Field(...)
    residents_count: int = Field(..., ge=0)
    area: float = Field(..., ge=0)


class ReceiptDataRequest(BaseModel):
    first_name: str = Field(...)
    last_name: str = Field(...)
    middle_name: str = Field(...)
    address: AddressRequest = Field(...)
    paid_at: datetime = Field(...)
    amount: float = Field(...)
    # created_at: datetime