"""0001_pipeline4_payrun_payslip_schema

Revision ID: 0001_pipeline4
Revises:
Create Date: 2026-09-05 22:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_pipeline4"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Extensions & Schema (schema itself is also created defensively by
    # env.py's do_run_migrations, before this migration body runs).
    op.execute("CREATE SCHEMA IF NOT EXISTS payroll;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # 2. Postgres ENUM types, defensively (IF NOT EXISTS). rule_category and
    # computation_type back salary_rule, which Pipeline 5's own migration
    # will create tables for — not created here to keep this migration
    # scoped to Pipeline 4 (payrun wizard -> payslip creation).
    enums = [
        ("payrun_status", "('DRAFT', 'COMPUTED', 'VALIDATED', 'PAID', 'CANCELLED')"),
        ("payslip_status", "('DRAFT', 'COMPUTED', 'VALIDATED', 'PAID', 'ERROR')"),
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

    # 3. Salary Structure — minimal here (a named bundle of rules); Pipeline 5
    # adds salary_rule / salary_structure_rule on top of this same table.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS payroll.salary_structure (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(150) NOT NULL,
            code VARCHAR(50) UNIQUE NOT NULL,
            description TEXT,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )

    # 4. Payrun — the batch. salary_structure_id is in-schema (real FK);
    # created_by_user_id is cross-schema (app_user lives in gateway) so it
    # stays a plain UUID with no FK, per the project's cross-service rule.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS payroll.payrun (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(150) NOT NULL,
            period_start DATE NOT NULL,
            period_end DATE NOT NULL,
            salary_structure_id UUID NOT NULL REFERENCES payroll.salary_structure(id) ON DELETE RESTRICT,
            status payrun_status NOT NULL DEFAULT 'DRAFT',
            created_by_user_id UUID,
            computed_at TIMESTAMPTZ,
            validated_at TIMESTAMPTZ,
            paid_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_payrun_period_range CHECK (period_end >= period_start)
        );
        """
    )

    # 5. Payslip — associative entity realizing Payrun <-> Employee. employee_id
    # and contract_id are cross-schema (hr-service owns both) so they stay
    # plain UUIDs with no FK, snapshotted at payrun-creation time.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS payroll.payslip (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            payrun_id UUID NOT NULL REFERENCES payroll.payrun(id) ON DELETE CASCADE,
            employee_id UUID NOT NULL,
            contract_id UUID NOT NULL,
            period_start DATE NOT NULL,
            period_end DATE NOT NULL,
            worked_days NUMERIC(6, 2),
            status payslip_status NOT NULL DEFAULT 'DRAFT',
            gross_amount NUMERIC(12, 2),
            net_amount NUMERIC(12, 2),
            has_warning BOOLEAN NOT NULL DEFAULT FALSE,
            warning_notes TEXT,
            pdf_url TEXT,
            sent_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT uq_payslip_payrun_employee UNIQUE (payrun_id, employee_id)
        );
        """
    )

    # 6. Audit Log — same shape as hr-service / attendance-timeoff-service,
    # replicated per-schema per the project's isolated-schema architecture.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS payroll.audit_log (
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

    # 7. Indexes.
    op.execute("CREATE INDEX IF NOT EXISTS idx_payrun_period ON payroll.payrun(period_start, period_end);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_payslip_employee ON payroll.payslip(employee_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_payslip_payrun ON payroll.payslip(payrun_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_entity ON payroll.audit_log(entity_name, entity_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON payroll.audit_log(created_at DESC);")

    # 8. updated_at trigger function + triggers (salary_structure, payslip only
    # — payrun has no updated_at column, matching schema.sql).
    op.execute(
        """
        CREATE OR REPLACE FUNCTION payroll.set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    for table in ["salary_structure", "payslip"]:
        op.execute(
            f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_{table}_updated_at'
                ) THEN
                    CREATE TRIGGER trg_{table}_updated_at
                    BEFORE UPDATE ON payroll.{table}
                    FOR EACH ROW EXECUTE FUNCTION payroll.set_updated_at();
                END IF;
            END$$;
            """
        )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_payslip_updated_at ON payroll.payslip;")
    op.execute("DROP TRIGGER IF EXISTS trg_salary_structure_updated_at ON payroll.salary_structure;")
    op.execute("DROP FUNCTION IF EXISTS payroll.set_updated_at();")
    op.execute("DROP TABLE IF EXISTS payroll.audit_log CASCADE;")
    op.execute("DROP TABLE IF EXISTS payroll.payslip CASCADE;")
    op.execute("DROP TABLE IF EXISTS payroll.payrun CASCADE;")
    op.execute("DROP TABLE IF EXISTS payroll.salary_structure CASCADE;")

    enums = ["audit_action", "payslip_status", "payrun_status"]
    for enum_name in enums:
        op.execute(f"DROP TYPE IF EXISTS {enum_name} CASCADE;")
