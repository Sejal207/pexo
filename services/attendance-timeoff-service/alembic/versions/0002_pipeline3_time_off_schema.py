"""0002_pipeline3_time_off_schema

Revision ID: 0002_pipeline3
Revises: 0001_pipeline2
Create Date: 2026-09-05 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0002_pipeline3"
down_revision = "0001_pipeline2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Postgres ENUM types, defensively (IF NOT EXISTS).
    enums = [
        ("timeoff_unit", "('DAYS', 'HOURS')"),
        ("approval_status", "('PENDING', 'APPROVED', 'REFUSED')"),
        ("request_status", "('DRAFT', 'SUBMITTED', 'APPROVED', 'REFUSED', 'CANCELLED')"),
    ]
    for enum_name, enum_values in enums:
        op.execute(
            f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{enum_name}') THEN
                    CREATE TYPE {enum_name} AS ENUM {enum_values};
                END IF;
            END$$;
            """
        )

    # 2. Time Off Type — a policy, owned entirely by this service/schema.
    #    payroll_work_entry_code is additive beyond schema.sql (see model docstring).
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance_timeoff.time_off_type (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(100) UNIQUE NOT NULL,
            unit timeoff_unit NOT NULL DEFAULT 'DAYS',
            requires_allocation BOOLEAN NOT NULL DEFAULT TRUE,
            requires_approval BOOLEAN NOT NULL DEFAULT TRUE,
            affects_payroll BOOLEAN NOT NULL DEFAULT FALSE,
            color VARCHAR(20),
            payroll_work_entry_code VARCHAR(50),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )

    # 3. Time Off Allocation — employee_id is a plain UUID (no FK): the
    #    employee record lives in hr-service's schema, not this one.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance_timeoff.time_off_allocation (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            employee_id UUID NOT NULL,
            time_off_type_id UUID NOT NULL REFERENCES attendance_timeoff.time_off_type(id) ON DELETE RESTRICT,
            allocated_amount NUMERIC(6, 2) NOT NULL,
            taken_amount NUMERIC(6, 2) NOT NULL DEFAULT 0,
            remaining_amount NUMERIC(6, 2) GENERATED ALWAYS AS (allocated_amount - taken_amount) STORED,
            valid_from DATE NOT NULL,
            valid_to DATE NOT NULL,
            approval_status approval_status NOT NULL DEFAULT 'PENDING',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_allocation_valid_range CHECK (valid_to >= valid_from),
            CONSTRAINT ck_allocation_taken_within_bounds
                CHECK (taken_amount >= 0 AND taken_amount <= allocated_amount)
        );
        """
    )

    # 4. Time Off Request — employee_id and approved_by_user_id are plain
    #    UUIDs (no FK): employee lives in hr-service, reviewer in api-gateway.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance_timeoff.time_off_request (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            employee_id UUID NOT NULL,
            time_off_type_id UUID NOT NULL REFERENCES attendance_timeoff.time_off_type(id) ON DELETE RESTRICT,
            allocation_id UUID REFERENCES attendance_timeoff.time_off_allocation(id) ON DELETE SET NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            duration NUMERIC(6, 2) NOT NULL,
            status request_status NOT NULL DEFAULT 'DRAFT',
            approved_by_user_id UUID,
            approved_at TIMESTAMPTZ,
            reason TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_request_date_range CHECK (end_date >= start_date)
        );
        """
    )

    # 5. Indexes.
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_allocation_employee_type "
        "ON attendance_timeoff.time_off_allocation(employee_id, time_off_type_id);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_request_employee_status "
        "ON attendance_timeoff.time_off_request(employee_id, status);"
    )

    # 6. updated_at triggers (reuses the function created in 0001).
    for table in ["time_off_allocation", "time_off_request"]:
        op.execute(
            f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_{table}_updated_at'
                ) THEN
                    CREATE TRIGGER trg_{table}_updated_at
                    BEFORE UPDATE ON attendance_timeoff.{table}
                    FOR EACH ROW EXECUTE FUNCTION attendance_timeoff.set_updated_at();
                END IF;
            END$$;
            """
        )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_time_off_request_updated_at ON attendance_timeoff.time_off_request;")
    op.execute("DROP TRIGGER IF EXISTS trg_time_off_allocation_updated_at ON attendance_timeoff.time_off_allocation;")
    op.execute("DROP TABLE IF EXISTS attendance_timeoff.time_off_request CASCADE;")
    op.execute("DROP TABLE IF EXISTS attendance_timeoff.time_off_allocation CASCADE;")
    op.execute("DROP TABLE IF EXISTS attendance_timeoff.time_off_type CASCADE;")
    op.execute("DROP TYPE IF EXISTS request_status CASCADE;")
    op.execute("DROP TYPE IF EXISTS approval_status CASCADE;")
    op.execute("DROP TYPE IF EXISTS timeoff_unit CASCADE;")
