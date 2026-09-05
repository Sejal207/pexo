"""0002_pipeline5_salary_rule_engine_schema

Revision ID: 0002_pipeline5
Revises: 0001_pipeline4
Create Date: 2026-09-05 23:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0002_pipeline5"
down_revision = "0001_pipeline4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Postgres ENUM types, defensively (IF NOT EXISTS) — declared in
    # core/enums.py since Pipeline 4 but not created until now.
    enums = [
        ("rule_category", "('BASIC', 'ALLOWANCE', 'GROSS', 'DEDUCTION', 'EMPLOYER_CONTRIBUTION', 'NET')"),
        ("computation_type", "('FIXED', 'PERCENTAGE', 'FORMULA')"),
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

    # 2. Salary Rule — a reusable computation step. percentage_of_rule_code is
    # a strict self-referencing FK (schema.sql): PERCENTAGE rules always take
    # a percentage of another rule's already-computed value, never a bare
    # "contract_wage" sentinel (see model docstring for how Wage-based rules
    # are expressed instead).
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS payroll.salary_rule (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            code VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(150) NOT NULL,
            category rule_category NOT NULL,
            computation_type computation_type NOT NULL,
            fixed_amount NUMERIC(12, 2),
            percentage_of_rule_code VARCHAR(50) REFERENCES payroll.salary_rule(code) ON DELETE SET NULL,
            percentage_value NUMERIC(6, 3),
            formula_expression TEXT,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_salary_rule_computation_fields CHECK (
                (computation_type = 'FIXED' AND fixed_amount IS NOT NULL) OR
                (computation_type = 'PERCENTAGE' AND percentage_of_rule_code IS NOT NULL AND percentage_value IS NOT NULL) OR
                (computation_type = 'FORMULA' AND formula_expression IS NOT NULL)
            )
        );
        """
    )

    # 3. Salary Structure Rule — M2M, salary_structure <-> salary_rule, with a
    # per-structure sequence (rules run in this order within a structure).
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS payroll.salary_structure_rule (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            salary_structure_id UUID NOT NULL REFERENCES payroll.salary_structure(id) ON DELETE CASCADE,
            salary_rule_id UUID NOT NULL REFERENCES payroll.salary_rule(id) ON DELETE RESTRICT,
            sequence INTEGER NOT NULL,
            CONSTRAINT uq_ssr_structure_rule UNIQUE (salary_structure_id, salary_rule_id),
            CONSTRAINT uq_ssr_structure_sequence UNIQUE (salary_structure_id, sequence)
        );
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_ssr_structure_seq "
        "ON payroll.salary_structure_rule(salary_structure_id, sequence);"
    )

    # 4. Payslip Line — one rule's computed contribution to a payslip.
    # salary_rule_code is a denormalized text snapshot on purpose: historical
    # payslips stay accurate even if a rule is later renamed/deleted.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS payroll.payslip_line (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            payslip_id UUID NOT NULL REFERENCES payroll.payslip(id) ON DELETE CASCADE,
            salary_rule_id UUID REFERENCES payroll.salary_rule(id) ON DELETE SET NULL,
            salary_rule_code VARCHAR(50) NOT NULL,
            sequence INTEGER NOT NULL,
            amount NUMERIC(12, 2) NOT NULL,
            computation_detail JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_payslip_line_payslip "
        "ON payroll.payslip_line(payslip_id, sequence);"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS payroll.payslip_line CASCADE;")
    op.execute("DROP TABLE IF EXISTS payroll.salary_structure_rule CASCADE;")
    op.execute("DROP TABLE IF EXISTS payroll.salary_rule CASCADE;")
    op.execute("DROP TYPE IF EXISTS computation_type CASCADE;")
    op.execute("DROP TYPE IF EXISTS rule_category CASCADE;")
