"""
SQLAlchemy-side declarations for Postgres ENUM types that already exist in the DB
(created by this service's own Alembic migration). create_type=False -> Alembic's
autogenerate will not try to CREATE TYPE for these; the migration creates them via
raw SQL, defensively (IF NOT EXISTS), since audit_action is shared across services.
"""
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

AttendanceStatusEnum = PgEnum(
    "PRESENT", "ABSENT", "LATE", "HALF_DAY", "ON_LEAVE", "MISSING_CHECKOUT",
    name="attendance_status",
    create_type=False,
)

AuditActionEnum = PgEnum(
    "CREATE", "UPDATE", "DELETE", "APPROVE", "REFUSE",
    name="audit_action",
    create_type=False,
)

TimeoffUnitEnum = PgEnum(
    "DAYS", "HOURS",
    name="timeoff_unit",
    create_type=False,
)

ApprovalStatusEnum = PgEnum(
    "PENDING", "APPROVED", "REFUSED",
    name="approval_status",
    create_type=False,
)

RequestStatusEnum = PgEnum(
    "DRAFT", "SUBMITTED", "APPROVED", "REFUSED", "CANCELLED",
    name="request_status",
    create_type=False,
)
