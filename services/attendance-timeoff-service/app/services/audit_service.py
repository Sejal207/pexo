"""
AuditService: thin wrapper that writes a row to audit_log for every sensitive
mutation (attendance manual corrections). Mirrors hr-service's AuditService.
"""
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def log(
        self,
        *,
        user_id: Optional[UUID],
        entity_name: str,
        entity_id: UUID,
        action: str,
        field_changes: Optional[dict[str, Any]] = None,
        reason: Optional[str] = None,
    ) -> AuditLog:
        """Write a single audit_log row. Does NOT commit — caller owns the transaction."""
        entry = AuditLog(
            user_id=user_id,
            entity_name=entity_name,
            entity_id=entity_id,
            action=action,
            field_changes=field_changes,
            reason=reason,
        )
        self.db.add(entry)
        return entry
