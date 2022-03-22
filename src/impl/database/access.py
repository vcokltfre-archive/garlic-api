# pyright: reportIncompatibleVariableOverride=false
# pyright: reportGeneralTypeIssues=false

from datetime import datetime

from ormar import BigInteger, DateTime, Model

from .metadata import database, metadata


class AccessKey(Model):
    class Meta:
        metadata = metadata
        database = database
        tablename = "access_keys"

    id: int = BigInteger(primary_key=True)
    user_id: int = BigInteger(nullable=False)
    valid_from: datetime = DateTime(nullable=False)
    valid_until: datetime = DateTime(nullable=False)
