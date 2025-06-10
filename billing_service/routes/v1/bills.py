from datetime import datetime, timezone
from typing import List, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models.database import Bill, Service, get_db
from models.requests import BillRequest
from models.responses import BillResponse, ServiceResponse
from sqlalchemy.orm import Session

router = APIRouter()
security = HTTPBearer()


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


@router.get("/", response_model=BillResponse)
async def get_bills(
    bill_request: BillRequest,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    bills = (
        db.query(Bill)
        .filter(
            Bill.account_number == bill_request.account_number,
            Bill.period == bill_request.period,
        )
        .all()
    )

    if not bills:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    services = db.query(Service).filter(Service.id.in_([bill.service_id for bill in bills])).all()
    services_dict = {service.id: service for service in services}

    services_responses = []
    for bill in bills:
        services_responses.append(ServiceResponse(
            service_name=services_dict[bill.service_id].service_name,
            cost_per_unit=services_dict[bill.service_id].cost_per_unit,
            units=bill.units,
            total_cost=bill.amount
        ))

    return BillResponse(
        account_number=bill_request.account_number,
        period=bill_request.period,
        amount=sum([bill.amount for bill in bills]),
        status=bills[0].status,
        created_at=bills[0].created_at,
        paid_at=bills[0].paid_at,
        services=services_responses
    )
