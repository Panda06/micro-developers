from typing import List, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models.database import Account, User, UserAddress, Provider, UserProfile, get_db
from models.requests import AccountCreate, SetActiveRequest
from models.responses import AccountResponse
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger("accounts_service.routes")
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
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/", response_model=AccountResponse)
async def add_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    logger.info(f"Creating account for user {current_user}")
    
    existing = (
        db.query(Account)
        .join(User, Account.user_id == User.id)
        .filter(
            Account.account_number == account.account_number,
            User.keycloack_id == current_user,
            Account.is_deleted == False,
        )
        .first()
    )

    if existing:
        logger.error(f"Account with this number already exists: {account.account_number}")
        raise HTTPException(
            status_code=409, detail="Account with this number already exists"
        )
    
    user = db.query(User).filter(User.keycloack_id == current_user).first()
    if not user:
        logger.error(f"User not found: {current_user}")
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user.id
    
    address_data = account.address
    new_address = UserAddress(
        user_id=user_id,
        region=address_data.region,
        city=address_data.city,
        street=address_data.street,
        house=address_data.house,
        flat=address_data.apartment,
        residents_counts=address_data.residents_count,
        area=address_data.area,
    )
    address_existing = db.query(UserAddress).filter(
        UserAddress.region == address_data.region,
        UserAddress.city == address_data.city,
        UserAddress.street == address_data.street,
        UserAddress.house == address_data.house,
        UserAddress.flat == address_data.apartment
    ).first()
    
    if not address_existing:
        logger.info(f"Adding new address to db {address_data.street}")
        db.add(new_address)
        db.flush()
        address_id = new_address.id
    else:
        address_id = address_existing.id

    user_accounts_count = (
        db.query(Account).filter(Account.user_id == user_id, Account.is_deleted == False).count()
    )
    is_first_account = user_accounts_count == 0

    db_account = Account(
        account_number=account.account_number,
        user_id=user_id,
        address_id=address_id,
        provider_id=account.provider_id,
        is_active=is_first_account,
        is_deleted=False,
    )

    db.add(db_account)
    db.commit()
    db.refresh(db_account)

    logger.info(f"Account created successfully: {db_account.account_number}")
    account_data = (
        db.query(Account, UserAddress, UserProfile, Provider)
        .join(UserAddress, Account.address_id == UserAddress.id)
        .join(UserProfile, Account.user_id == UserProfile.user_id)
        .join(Provider, Account.provider_id == Provider.id)
        .filter(Account.id == db_account.id, Account.is_deleted == False)
        .first()
    )
    
    account, address, profile, provider = account_data
    address_str = f"{address.city}, {address.street}, {address.house}, кв. {address.flat}"
    owner_name = f"{profile.last_name} {profile.first_name} {profile.middle_name}"
    
    return AccountResponse(
        id=account.id,
        account_number=account.account_number,
        address=address_str,
        owner_name=owner_name,
        area=address.area,
        residents_count=address.residents_counts,
        management_company=provider.name,
        is_active=account.is_active,
        created_at=account.created_at
    )


@router.get("/", response_model=List[AccountResponse])
async def get_accounts(
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    logger.info(f"Getting accounts for user {current_user}")
    
    accounts_data = (
        db.query(Account, UserAddress, UserProfile, Provider)
        .join(UserAddress, Account.address_id == UserAddress.id)
        .join(UserProfile, Account.user_id == UserProfile.user_id)
        .join(Provider, Account.provider_id == Provider.id)
        .join(User, Account.user_id == User.id)
        .filter(User.keycloack_id == current_user, Account.is_deleted == False)
        .all()
    )
    
    result = []
    for account, address, profile, provider in accounts_data:
        address_str = f"{address.city}, {address.street}, {address.house}, кв. {address.flat}"
        owner_name = f"{profile.last_name} {profile.first_name} {profile.middle_name}"
        
        result.append(AccountResponse(
            id=account.id,
            account_number=account.account_number,
            address=address_str,
            owner_name=owner_name,
            area=address.area,
            residents_count=address.residents_counts,
            management_company=provider.name,
            is_active=account.is_active,
            created_at=account.created_at
        ))
    
    logger.info(f"Found {len(result)} accounts for user {current_user}")
    return result


@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    account = (
        db.query(Account)
        .join(User, Account.user_id == User.id)
        .filter(Account.id == account_id, 
                User.keycloack_id == current_user,
                Account.is_deleted == False
                )
        .first()
    )

    if not account:
        logger.error(f"Account not found: {account_id}")
        raise HTTPException(status_code=404, detail="Account not found")

    was_active = account.is_active
    
    account.is_deleted = True
    account.is_active = False

    if was_active:
        other_account = (
            db.query(Account)
            .filter(Account.user_id == account.user_id, 
                   Account.id != account_id,
                   Account.is_deleted == False)
            .first()
        )
        if other_account:
            other_account.is_active = True

    db.commit()
    logger.info(f"Account {account_id} deleted successfully")
    return {"message": "Account deleted successfully"}


@router.put("/set-active")
async def set_active_account(
    request: SetActiveRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    logger.info(f"Setting account {request.account_id} active")
    new_active = (
        db.query(Account).
        join(User, Account.user_id == User.id)
        .filter(Account.id == request.account_id, 
               User.keycloack_id == current_user,
               Account.is_deleted == False)
        .first()
    )

    if not new_active:
        raise HTTPException(status_code=404, detail="Account not found")

    db.query(Account).filter(Account.user_id == new_active.user_id, Account.is_deleted == False).update(
        {"is_active": False}
    )

    new_active.is_active = True
    db.commit()

    return {"message": "Active account updated successfully"}


@router.get("/active", response_model=Optional[AccountResponse])
async def get_active_account(
    db: Session = Depends(get_db), current_user: str = Depends(get_current_user)
):
    account_data = (
        db.query(Account, UserAddress, UserProfile, Provider)
        .join(UserAddress, Account.address_id == UserAddress.id)
        .join(UserProfile, Account.user_id == UserProfile.user_id)
        .join(Provider, Account.provider_id == Provider.id)
        .join(User, Account.user_id == User.id)
        .filter(User.keycloack_id == current_user, Account.is_active == True, Account.is_deleted == False)
        .first()
    )

    if not account_data:
        return None
        
    account, address, profile, provider = account_data
    address_str = f"{address.city}, {address.street}, {address.house}, кв. {address.flat}"
    owner_name = f"{profile.last_name} {profile.first_name} {profile.middle_name}"
    
    return AccountResponse(
        id=account.id,
        account_number=account.account_number,
        address=address_str,
        owner_name=owner_name,
        area=address.area,
        residents_count=address.residents_counts,
        management_company=provider.name,
        is_active=account.is_active,
        created_at=account.created_at
    )

@router.get('/providers')
async def get_providers(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    providers = db.query(Provider).all()
    return providers


@router.get('/has-access')
async def has_access_to_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    account = db.query(Account).join(User, Account.user_id == User.id).filter(
        Account.id == account_id, 
        User.keycloack_id == current_user,
        Account.is_deleted == False
    ).first()
    if account is None:
        raise HTTPException(status_code=403, detail="Access denied")
    return {"has_access": True}