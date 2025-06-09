from pydantic import BaseModel


class PaymentResponse(BaseModel):
    id: str
    status: str
    message: str
