import logging

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models.database import Account, Bill, Service, get_db
from models.requests import PayBillRequest
from models.responses import BillResponse, ServiceResponse, UnpaidPeriodsResponse
from sqlalchemy.orm import Session

logger = logging.getLogger("billing_service.routes")
router = APIRouter()
security = HTTPBearer()


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


@router.get("/", response_model=BillResponse)
async def get_bill(
    account_number: str,
    period: str,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    logger.info(f"Getting bill for account {account_number}, period {period}")
    
    bills = (
        db.query(Bill)
        .join(Account, Account.id == Bill.account_id)
        .filter(
            Account.account_number == account_number,
            Bill.period == period,
        )
        .all()
    )

    if not bills:
        logger.warning(f"Bill not found for account {account_number}, period {period}")
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
    
    logger.info(f"Found {len(bills)} bills for account {account_number}, period {period}")
    return BillResponse(
        account_number=account_number,
        period=period,
        total_amount=sum([bill.amount for bill in bills]),
        status=bills[0].status_type,
        services=services_responses
    )

@router.get("/unpaid-periods", response_model=UnpaidPeriodsResponse)
async def get_not_paid_periods(
    account_number: str,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    logger.info(f"Getting unpaid periods for account {account_number}")

    account = db.query(Account).filter(Account.account_number == account_number).first()
    if not account:
        logger.error(f"Account not found: {account_number}")
        raise HTTPException(status_code=404, detail="Account not found")
    
    unpaid_periods = (
        db.query(Bill.period)
        .filter(
            Bill.account_id == account.id,
            Bill.status_type != "paid"
        )
        .distinct()
        .order_by(Bill.period)
        .all()
    )
    
    periods_list = [str(period[0]) for period in unpaid_periods]

    logger.info(f"Found {len(periods_list)} unpaid periods for account {account_number}")
    return UnpaidPeriodsResponse(
        account_number=account_number,
        unpaid_periods=periods_list
    )