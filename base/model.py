from sqlmodel import Field, SQLModel
from uuid import UUID
from uuid6 import uuid7
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

silicon_valley_tz = ZoneInfo("America/Los_Angeles")


def date_now():
    return datetime.now().astimezone(silicon_valley_tz)


class ModelBase(SQLModel):
    id: UUID = Field(
        default_factory=uuid7,
        primary_key=True,
        index=True,
        nullable=False,
    )
    create_time: Optional[datetime] = Field(default_factory=date_now)
    modify_time: Optional[datetime] = Field(default_factory=date_now)
    deleted: bool = Field(default=False)
