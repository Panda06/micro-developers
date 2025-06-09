import os
from datetime import datetime, timezone

import jwt
import requests
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models.database import Account, Bill, Payment, get_db
from models.requests import PaymentCreate
from models.responses import PaymentResponse
from sqlalchemy.orm import Session

router = APIRouter()
security = HTTPBearer()
PAYMENT_MOCK_SERVICE_URL = os.getenv(
    "PAYMENT_MOCK_SERVICE_URL", "http://payment-mock-service:8000"
)
BILLING_SERVICE_URL = os.getenv("BILLING_SERVICE_URL", "http://billing-service:8000")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    account = (
        db.query(Account)
        .filter(Account.account_number == payment_data.account_number)
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.user_id != current_user:
        raise HTTPException(status_code=403, detail="Access denied")

    bill = (
        db.query(Bill)
        .filter(Bill.account_id == account.id, Bill.period == payment_data.period)
        .first()
    )
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    if bill.status == "paid":
        raise HTTPException(status_code=400, detail="Bill already paid")

    if payment_data.amount > bill.total_amount:
        raise HTTPException(
            status_code=400, detail="Payment amount must match bill amount"
        )

    payment = Payment(
        bill_id=bill.id,
        account_id=account.id,
        amount=payment_data.amount,
        status="pending",
    )
    db.add(payment)
    db.flush()

    try:
        mock_payment_data = {
            "amount": payment_data.amount,
            "card_number": payment_data.card_number,
            "card_holder": payment_data.card_holder,
            "card_expiration_date": payment_data.card_expiration_date,
            "card_cvv": payment_data.card_cvv,
            "inn_receiver": payment_data.inn_receiver,
        }
        # TODO: replace hardcoded url
        response = requests.post(
            f"{PAYMENT_MOCK_SERVICE_URL}/api/v1/payments/", json=mock_payment_data
        )

        if response.status_code != 200:
            payment.status = "failed"
            db.commit()
            raise HTTPException(status_code=400, detail="Payment failed")

        mock_response = response.json()

        if mock_response.get("status") == "success":
            payment.status = "completed"
            payment.completed_at = datetime.now(timezone.utc)
            response = requests.post(
                f"{BILLING_SERVICE_URL}/api/v1/bills/{bill.id}/pay",
                json={"payment_id": payment.id},
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, detail="Billing service unavailable"
                )

            return PaymentResponse(
                id=payment.id,
                payment_id=str(payment.id),
                account_number=payment_data.account_number,
                amount=payment_data.amount,
                period=payment_data.period,
                status="completed",
                created_at=payment.created_at,
                completed_at=payment.completed_at,
            )
        else:
            payment.status = "failed"
            db.commit()
            raise HTTPException(
                status_code=400,
                detail=f"Payment failed: {mock_response.get('message', 'Unknown error')}",
            )

    except requests.RequestException as e:
        payment.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=500, detail=f"Payment service unavailable: {str(e)}"
        )
    except Exception as e:
        payment.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
