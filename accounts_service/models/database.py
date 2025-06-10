import os
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres")
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME")

DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    account_number = Column(String(10), unique=True, index=True, nullable=False)
    address_id = Column(Integer, nullable=False)
    provider_id = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))


class UserAddress(Base):
    __tablename__ = "user_addresses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    region = Column(String, nullable=False)
    city = Column(String, nullable=False)
    street = Column(String, nullable=False)
    house = Column(String, nullable=False)
    apartment = Column(String, nullable=False)
    residents_count = Column(Integer, nullable=False)
    area = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))


class Provider(Base):
    __tablename__ = "providers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    inn = Column(String, nullable=False, unique=True)
    ogrn = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
