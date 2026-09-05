"""0001_pipeline2_attendance_schema

Revision ID: 0001_pipeline2
Revises:
Create Date: 2026-09-05 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_pipeline2"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Extensions & schema.
    op.execute("CREATE SCHEMA IF NOT EXISTS attendance_timeoff;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # 2. Postgres ENUM types. attendance_status is owned by this service;
    #    audit_action is shared across services (also created defensively by
    #    hr-service's migration) — IF NOT EXISTS makes either migration order
    #    safe to run first.
    enums = [
        ("attendance_status", "('PRESENT', 'ABSENT', 'LATE', 'HALF_DAY', 'ON_LEAVE', 'MISSING_CHECKOUT')"),
        ("audit_action", "('CREATE', 'UPDATE', 'DELETE', 'APPROVE', 'REFUSE')"),
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

    # 3. Attendance table.
    #    employee_id and corrected_by_user_id are plain UUIDs (no FK): the
    #    referenced rows live in hr-service's and api-gateway's own schemas.
    #    overtime_hours is additive beyond schema.sql's attendance table — see
    #    the model docstring for why it is persisted.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance_timeoff.attendance (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            employee_id UUID NOT NULL,
            work_date DATE NOT NULL,
            check_in TIMESTAMPTZ,
            check_out TIMESTAMPTZ,
            worked_hours NUMERIC(6, 2),
            overtime_hours NUMERIC(6, 2),
            status attendance_status NOT NULL DEFAULT 'PRESENT',
            is_manual_correction BOOLEAN NOT NULL DEFAULT FALSE,
            corrected_by_user_id UUID,
            correction_reason TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT uq_attendance_employee_date UNIQUE (employee_id, work_date),
            CONSTRAINT ck_attendance_checkout_after_checkin
                CHECK (check_out IS NULL OR check_in IS NULL OR check_out > check_in)
        );
        """
    )

    # 4. Audit log table (per-service, mirrors hr.audit_log).
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance_timeoff.audit_log (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID,
            entity_name VARCHAR(100) NOT NULL,
            entity_id UUID NOT NULL,
            action audit_action NOT NULL,
            field_changes JSONB,
            reason TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )

    # 5. Indexes.
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_attendance_employee_date "
        "ON attendance_timeoff.attendance(employee_id, work_date);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_attendance_audit_log_entity "
        "ON attendance_timeoff.audit_log(entity_name, entity_id);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_attendance_audit_log_created_at "
        "ON attendance_timeoff.audit_log(created_at DESC);"
    )

    # 6. updated_at trigger.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION attendance_timeoff.set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_trigger WHERE tgname = 'trg_attendance_updated_at'
            ) THEN
                CREATE TRIGGER trg_attendance_updated_at
                BEFORE UPDATE ON attendance_timeoff.attendance
                FOR EACH ROW EXECUTE FUNCTION attendance_timeoff.set_updated_at();
            END IF;
        END$$;
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_attendance_updated_at ON attendance_timeoff.attendance;")
    op.execute("DROP FUNCTION IF EXISTS attendance_timeoff.set_updated_at();")
    op.execute("DROP TABLE IF EXISTS attendance_timeoff.audit_log CASCADE;")
    op.execute("DROP TABLE IF EXISTS attendance_timeoff.attendance CASCADE;")
    op.execute("DROP TYPE IF EXISTS attendance_status CASCADE;")
