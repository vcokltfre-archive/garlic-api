# pyright: reportIncompatibleVariableOverride=false
# pyright: reportGeneralTypeIssues=false

from datetime import datetime
from typing import Optional

from ormar import BigInteger, DateTime, Model, String

from .metadata import database, metadata


class User(Model):
    class Meta:
        metadata = metadata
        database = database
        tablename = "users"

    id: int = BigInteger(primary_key=True, autoincrement=False)
    username: str = String(max_length=255, nullable=False)
    discriminator: str = String(max_length=255, nullable=False)
    wallet: int = BigInteger(default=0, nullable=False)
    bank: int = BigInteger(default=0, nullable=False)
    bank_size: int = BigInteger(default=250, nullable=False)
    flags: int = BigInteger(default=0, nullable=False)
    created_at: datetime = DateTime(default=datetime.utcnow, nullable=False)
    updated_at: datetime = DateTime(default=datetime.utcnow, nullable=False)
    last_daily: Optional[datetime] = DateTime(nullable=True)
    last_weekly: Optional[datetime] = DateTime(nullable=True)
    last_monthly: Optional[datetime] = DateTime(nullable=True)
