"""
SQLAlchemy-side declarations for Postgres ENUM types that already exist in the
DB (created by this service's own Alembic migrations). create_type=False ->
Alembic's autogenerate will not try to CREATE TYPE for these; migrations
create them via raw SQL, defensively (IF NOT EXISTS).

rule_category / computation_type back the salary_rule table, which is
Pipeline 5's own migration to create — declared here now only so the
SalaryRule model (mapped in this same Base.metadata) resolves cleanly.
"""
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

PayrunStatusEnum = PgEnum(
    "DRAFT", "COMPUTED", "VALIDATED", "PAID", "CANCELLED",
    name="payrun_status",
    create_type=False,
)

PayslipStatusEnum = PgEnum(
    "DRAFT", "COMPUTED", "VALIDATED", "PAID", "ERROR",
    name="payslip_status",
    create_type=False,
)

RuleCategoryEnum = PgEnum(
    "BASIC", "ALLOWANCE", "GROSS", "DEDUCTION", "EMPLOYER_CONTRIBUTION", "NET",
    name="rule_category",
    create_type=False,
)

ComputationTypeEnum = PgEnum(
    "FIXED", "PERCENTAGE", "FORMULA",
    name="computation_type",
    create_type=False,
)

AuditActionEnum = PgEnum(
    "CREATE", "UPDATE", "DELETE", "APPROVE", "REFUSE",
    name="audit_action",
    create_type=False,
)
