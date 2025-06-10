import random
import uuid

from fastapi import APIRouter
from models.requests import PaymentRequest
from models.responses import PaymentResponse

router = APIRouter()


@router.post("/")
async def create_payment(payment: PaymentRequest):
    payment_id = str(uuid.uuid4())
    if random.random() < 0.95:
        return PaymentResponse(
            id=payment_id, status="success", message="Payment successful"
        )
    else:
        return PaymentResponse(id=payment_id, status="failed", message="Payment failed")
