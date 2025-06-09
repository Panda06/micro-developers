from typing import List, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models.database import Account, UserAddress, Provider, get_db
from models.requests import AccountCreate, SetActiveRequest
from models.responses import AccountResponse
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


@router.post("/", response_model=AccountResponse)
async def add_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    existing = (
        db.query(Account)
        .filter(
            Account.account_number == account.account_number,
            Account.user_id == current_user,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400, detail="Account with this number already exists"
        )

    address_data = account.address
    new_address = UserAddress(
        user_id=current_user,
        region=address_data.region,
        city=address_data.city,
        street=address_data.street,
        house=address_data.house,
        apartment=address_data.apartment,
        residents_count=address_data.residents_count,
        area=address_data.area,
    )
    address_existing = db.query(UserAddress).filter(
        UserAddress.region == address_data.region,
        UserAddress.city == address_data.city,
        UserAddress.street == address_data.street,
        UserAddress.house == address_data.house,
        UserAddress.apartment == address_data.apartment
    ).first()
    
    if not address_existing:
        db.add(new_address)
        db.flush()
        address_id = new_address.id
    else:
        address_id = address_existing.id

    user_accounts_count = (
        db.query(Account).filter(Account.user_id == current_user).count()
    )
    is_first_account = user_accounts_count == 0

    db_account = Account(
        account_number=account.account_number,
        user_id=current_user,
        address_id=address_id,
        provider_id=account.provider_id,
        is_active=is_first_account,
    )

    db.add(db_account)
    db.commit()
    db.refresh(db_account)

    return db_account


@router.get("/", response_model=List[AccountResponse])
async def get_accounts(
    db: Session = Depends(get_db), current_user: int = Depends(get_current_user)
):
    accounts = db.query(Account).filter(Account.user_id == current_user).all()
    return accounts


@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == current_user)
        .first()
    )

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    was_active = account.is_active
    db.delete(account)

    if was_active:
        other_account = (
            db.query(Account)
            .filter(Account.user_id == current_user, Account.id != account_id)
            .first()
        )
        if other_account:
            other_account.is_active = True

    db.commit()

    return {"message": "Account deleted successfully"}


@router.put("/set-active")
async def set_active_account(
    request: SetActiveRequest,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    new_active = (
        db.query(Account)
        .filter(Account.id == request.account_id, Account.user_id == current_user)
        .first()
    )

    if not new_active:
        raise HTTPException(status_code=404, detail="Account not found")

    db.query(Account).filter(Account.user_id == current_user).update(
        {"is_active": False}
    )

    new_active.is_active = True
    db.commit()

    return {"message": "Active account updated successfully"}


@router.get("/active", response_model=Optional[AccountResponse])
async def get_active_account(
    db: Session = Depends(get_db), current_user: int = Depends(get_current_user)
):
    active_account = (
        db.query(Account)
        .filter(Account.user_id == current_user, Account.is_active == True)
        .first()
    )

    return active_account

@router.get('/providers')
async def get_providers(
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    providers = db.query(Provider).all()
    return providers

