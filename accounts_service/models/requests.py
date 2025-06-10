from pydantic import BaseModel, Field, validator

class Address(BaseModel):
    region: str = Field(..., description="Region")
    city: str = Field(..., description="City")
    street: str = Field(..., description="Street")
    house: str = Field(..., description="House")
    apartment: str = Field(..., description="Apartment")
    residents_count: int = Field(..., description="Residents count")
    area: float = Field(..., description="Area")
    
    @validator('area')
    def validate_area(cls, v):
        if v <= 0:
            raise ValueError('Area must be positive')
        return v
    
    @validator('residents_count')
    def validate_residents_count(cls, v):
        if v <= 0:
            raise ValueError('Residents count must be positive')
        return v

class AccountCreate(BaseModel):
    account_number: str
    address: Address
    provider_id: int
    
    @validator('account_number')
    def validate_account_number(cls, v):
        if not v.isdigit() or len(v) != 10:
            raise ValueError('Account number must be exactly 10 digits')
        return v

class SetActiveRequest(BaseModel):
    account_id: int 
