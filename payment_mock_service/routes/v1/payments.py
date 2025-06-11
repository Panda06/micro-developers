import logging
import random
import uuid

from fastapi import APIRouter
from models.requests import PaymentRequest
from models.responses import PaymentResponse

logger = logging.getLogger("payment_mock_service.routes")
router = APIRouter()


@router.post("/")
async def create_payment(payment: PaymentRequest):
    logger.info(f"Processing mock payment for amount {payment.amount}, card ending {payment.card_number[-4:]}")
    
    payment_id = str(uuid.uuid4())
    
    if random.random() < 0.95:
        logger.info(f"Mock payment {payment_id} successful")
        return PaymentResponse(
            id=payment_id, status="success", message="Payment successful"
        )
    else:
        logger.warning(f"Mock payment {payment_id} failed (simulated failure)")
        return PaymentResponse(id=payment_id, status="failed", message="Payment failed")
