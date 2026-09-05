from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogOut(BaseModel):
    id: UUID
    user_id: Optional[UUID] = None
    entity_name: str
    entity_id: UUID
    action: str
    field_changes: Optional[Any] = None
    reason: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
