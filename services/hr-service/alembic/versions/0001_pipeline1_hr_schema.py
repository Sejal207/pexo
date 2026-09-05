"""0001_pipeline1_hr_schema

Revision ID: 0001_pipeline1
Revises: 
Create Date: 2026-09-05 14:58:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_pipeline1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Extensions & Schema
    op.execute("CREATE SCHEMA IF NOT EXISTS hr;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")

    # 2. Postgres ENUM Types (Create if not exists helper in PL/pgSQL)
    enums = [
        ("employment_status", "('ACTIVE', 'INACTIVE', 'TERMINATED', 'ON_LEAVE')"),
        ("contract_type", "('PERMANENT', 'FIXED_TERM', 'PROBATION', 'INTERN')"),
        ("wage_type", "('MONTHLY', 'HOURLY')"),
        ("contract_status", "('DRAFT', 'ACTIVE', 'EXPIRED', 'CANCELLED')"),
        ("schedule_type", "('FULL_TIME', 'PART_TIME', 'FLEXIBLE')"),
        ("day_of_week", "('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN')"),
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

    # 3. Department Table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS hr.department (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(150) NOT NULL,
            parent_department_id UUID REFERENCES hr.department(id) ON DELETE SET NULL,
            manager_employee_id UUID,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )

    # 4. Job Position Table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS hr.job_position (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(150) NOT NULL,
            department_id UUID REFERENCES hr.department(id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )

    # 5. Working Schedule Table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS hr.working_schedule (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(150) NOT NULL,
            schedule_type schedule_type NOT NULL DEFAULT 'FULL_TIME',
            total_weekly_hours NUMERIC(6, 2) NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )

    # 6. Working Schedule Line Table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS hr.working_schedule_line (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            working_schedule_id UUID NOT NULL REFERENCES hr.working_schedule(id) ON DELETE CASCADE,
            day day_of_week NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            break_minutes INTEGER NOT NULL DEFAULT 0,
            CONSTRAINT uq_schedule_day_start UNIQUE (working_schedule_id, day, start_time),
            CONSTRAINT ck_end_after_start CHECK (end_time > start_time)
        );
        """
    )

    # 7. Employee Table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS hr.employee (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            employee_code VARCHAR(30) UNIQUE NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            phone VARCHAR(20),
            date_of_birth DATE,
            gender VARCHAR(20),
            date_joined DATE NOT NULL,
            date_exit DATE,
            address_line VARCHAR(255),
            city VARCHAR(100),
            state VARCHAR(100),
            pincode VARCHAR(12),
            profile_image_url TEXT,
            department_id UUID REFERENCES hr.department(id) ON DELETE SET NULL,
            job_position_id UUID REFERENCES hr.job_position(id) ON DELETE SET NULL,
            manager_id UUID REFERENCES hr.employee(id) ON DELETE SET NULL,
            default_working_schedule_id UUID REFERENCES hr.working_schedule(id) ON DELETE SET NULL,
            employment_status employment_status NOT NULL DEFAULT 'ACTIVE',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_employee_date_exit CHECK (date_exit IS NULL OR date_exit >= date_joined)
        );
        """
    )

    # 8. Add manager_employee_id FK to department
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_department_manager'
            ) THEN
                ALTER TABLE hr.department
                ADD CONSTRAINT fk_department_manager
                FOREIGN KEY (manager_employee_id) REFERENCES hr.employee(id) ON DELETE SET NULL;
            END IF;
        END$$;
        """
    )

    # 9. Employee Bank Account Table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS hr.employee_bank_account (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            employee_id UUID NOT NULL REFERENCES hr.employee(id) ON DELETE CASCADE,
            account_holder_name VARCHAR(150) NOT NULL,
            account_number VARCHAR(50) NOT NULL,
            ifsc_code VARCHAR(15),
            bank_name VARCHAR(150),
            is_primary BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_employee_primary_bank
        ON hr.employee_bank_account (employee_id)
        WHERE is_primary = TRUE;
        """
    )

    # 10. Contract Table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS hr.contract (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            employee_id UUID NOT NULL REFERENCES hr.employee(id) ON DELETE CASCADE,
            contract_type contract_type NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            wage_amount NUMERIC(12, 2) NOT NULL,
            wage_type wage_type NOT NULL DEFAULT 'MONTHLY',
            salary_structure_id UUID NOT NULL,
            working_schedule_id UUID REFERENCES hr.working_schedule(id) ON DELETE SET NULL,
            department_id UUID REFERENCES hr.department(id) ON DELETE SET NULL,
            job_position_id UUID REFERENCES hr.job_position(id) ON DELETE SET NULL,
            status contract_status NOT NULL DEFAULT 'DRAFT',
            signed_date DATE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_contract_date_range CHECK (end_date IS NULL OR end_date >= start_date)
        );
        """
    )

    # 11. Overlap Exclusion Constraint on Contract
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_active_contract_no_overlap'
            ) THEN
                ALTER TABLE hr.contract
                ADD CONSTRAINT uq_active_contract_no_overlap
                EXCLUDE USING gist (
                    employee_id WITH =,
                    daterange(start_date, COALESCE(end_date, 'infinity'::date), '[]') WITH &&
                ) WHERE (status = 'ACTIVE');
            END IF;
        END$$;
        """
    )

    # 12. Audit Log Table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS hr.audit_log (
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

    # 13. Indexes
    op.execute("CREATE INDEX IF NOT EXISTS idx_employee_department ON hr.employee(department_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_employee_status ON hr.employee(employment_status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_contract_employee ON hr.contract(employee_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_contract_status ON hr.contract(status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_contract_dates ON hr.contract(start_date, end_date);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_entity ON hr.audit_log(entity_name, entity_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON hr.audit_log(created_at DESC);")

    # 14. Trigger function for updated_at
    op.execute(
        """
        CREATE OR REPLACE FUNCTION hr.set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    for table in ["department", "working_schedule", "employee", "contract"]:
        op.execute(
            f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_{table}_updated_at'
                ) THEN
                    CREATE TRIGGER trg_{table}_updated_at
                    BEFORE UPDATE ON hr.{table}
                    FOR EACH ROW EXECUTE FUNCTION hr.set_updated_at();
                END IF;
            END$$;
            """
        )


def downgrade() -> None:
    for table in ["contract", "employee", "working_schedule", "department"]:
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON hr.{table};")
    op.execute("DROP FUNCTION IF EXISTS hr.set_updated_at();")
    op.execute("DROP TABLE IF EXISTS hr.audit_log CASCADE;")
    op.execute("DROP TABLE IF EXISTS hr.contract CASCADE;")
    op.execute("DROP TABLE IF EXISTS hr.employee_bank_account CASCADE;")
    op.execute("ALTER TABLE IF EXISTS hr.department DROP CONSTRAINT IF EXISTS fk_department_manager;")
    op.execute("DROP TABLE IF EXISTS hr.employee CASCADE;")
    op.execute("DROP TABLE IF EXISTS hr.working_schedule_line CASCADE;")
    op.execute("DROP TABLE IF EXISTS hr.working_schedule CASCADE;")
    op.execute("DROP TABLE IF EXISTS hr.job_position CASCADE;")
    op.execute("DROP TABLE IF EXISTS hr.department CASCADE;")
    
    enums = ["employment_status", "contract_type", "wage_type", "contract_status", "schedule_type", "day_of_week", "audit_action"]
    for enum_name in enums:
        op.execute(f"DROP TYPE IF EXISTS {enum_name} CASCADE;")
