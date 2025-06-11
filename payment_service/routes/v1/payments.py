import logging
import os
from datetime import datetime, timezone

import jwt
import requests
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models.database import Account, Bill, Payment, PaymentBill, User, get_db
from models.requests import PaymentCreate
from models.responses import PaymentResponse
from sqlalchemy.orm import Session

logger = logging.getLogger("payment_service.routes")
router = APIRouter()
security = HTTPBearer()
PAYMENT_MOCK_SERVICE_URL = os.getenv(
    "PAYMENT_MOCK_SERVICE_URL", "http://payment-mock-service:8000"
)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    logger.info(f"Creating payment for user {current_user}, account {payment_data.account_number}, period {payment_data.period}")
    
    account = (
        db.query(Account)
        .join(User, Account.user_id == User.id)
        .filter(Account.account_number == payment_data.account_number, User.keycloack_id == current_user)
        .first()
    )
    if not account:
        logger.error(f"Account not found: {payment_data.account_number} for user {current_user}")
        raise HTTPException(status_code=404, detail="Account not found")
    
    bills = (
        db.query(Bill)
        .filter(Bill.account_id == account.id, 
                Bill.period == payment_data.period + '-01',
                Bill.status_type != 'paid')
        .all()
    )
    if not bills:
        logger.warning(f"No unpaid bills found for account {payment_data.account_number}, period {payment_data.period}")
        raise HTTPException(status_code=404, detail="No unpaid bills found for this period")
    
    total_amount = sum([bill.amount for bill in bills])
    logger.info(f"Found {len(bills)} unpaid bills, total amount: {total_amount}")

    if abs(payment_data.amount - total_amount) > 0.01:
        logger.error(f"Payment amount mismatch: {payment_data.amount} vs {total_amount}")
        raise HTTPException(
            status_code=400, detail=f"Payment amount {payment_data.amount} must match total bill amount {total_amount}"
        )

    payment = Payment(
        account_id=account.id,
        amount=payment_data.amount,
        status="pending",
    )
    db.add(payment)
    db.flush() 

    for bill in bills:
        payment_bill = PaymentBill(
            payment_id=payment.id,
            bill_id=bill.id
        )
        db.add(payment_bill)

    logger.info(f"Created payment {payment.id} with {len(bills)} linked bills")

    try:
        mock_payment_data = {
            "amount": payment_data.amount,
            "card_number": payment_data.card_number,
            "card_holder": payment_data.card_holder,
            "card_expiration_date": payment_data.card_expiration_date,
            "card_cvv": payment_data.card_cvv,
            "inn_receiver": payment_data.inn_receiver,
        }
        
        logger.info(f"Calling payment mock service for payment {payment.id}")
        response = requests.post(
            f"{PAYMENT_MOCK_SERVICE_URL}/api/v1/payments/", json=mock_payment_data
        )

        if response.status_code != 200:
            logger.error(f"Payment mock service failed with status {response.status_code}")
            payment.status = "failed"
            db.commit()
            raise HTTPException(status_code=400, detail="Payment failed")

        mock_response = response.json()

        if mock_response.get("status") == "success":
            logger.info(f"Payment {payment.id} successful, updating bills status")
            payment.status = "completed"
            payment.paid_at = datetime.now(timezone.utc)
            
            for bill in bills:
                bill.status_type = "paid"
               
            db.commit()
            logger.info(f"Payment {payment.id} completed successfully")

            return PaymentResponse(
                id=payment.id,
                payment_id=str(payment.id),
                account_number=payment_data.account_number,
                amount=payment_data.amount,
                period=payment_data.period,
                status="completed",
                created_at=payment.created_at,
                completed_at=payment.paid_at,
            )
        else:
            logger.error(f"Payment {payment.id} failed: {mock_response.get('message', 'Unknown error')}")
            payment.status = "failed"
            db.commit()
            raise HTTPException(
                status_code=400,
                detail=f"Payment failed: {mock_response.get('message', 'Unknown error')}",
            )

    except requests.RequestException as e:
        logger.error(f"Payment service unavailable for payment {payment.id}: {str(e)}")
        payment.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=500, detail=f"Payment service unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Internal error for payment {payment.id}: {str(e)}")
        payment.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
