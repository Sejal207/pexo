"""
SQLAlchemy-side declarations for Postgres ENUM types that already exist in the DB.
create_type=False → Alembic will NOT try to CREATE TYPE; they already exist from schema.sql.
"""
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

EmploymentStatusEnum = PgEnum(
    "ACTIVE", "INACTIVE", "TERMINATED", "ON_LEAVE",
    name="employment_status",
    create_type=False,
)

ContractTypeEnum = PgEnum(
    "PERMANENT", "FIXED_TERM", "PROBATION", "INTERN",
    name="contract_type",
    create_type=False,
)

WageTypeEnum = PgEnum(
    "MONTHLY", "HOURLY",
    name="wage_type",
    create_type=False,
)

ContractStatusEnum = PgEnum(
    "DRAFT", "ACTIVE", "EXPIRED", "CANCELLED",
    name="contract_status",
    create_type=False,
)

ScheduleTypeEnum = PgEnum(
    "FULL_TIME", "PART_TIME", "FLEXIBLE",
    name="schedule_type",
    create_type=False,
)

DayOfWeekEnum = PgEnum(
    "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN",
    name="day_of_week",
    create_type=False,
)

AuditActionEnum = PgEnum(
    "CREATE", "UPDATE", "DELETE", "APPROVE", "REFUSE",
    name="audit_action",
    create_type=False,
)
