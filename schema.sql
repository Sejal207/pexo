
-- Conventions:
--   - Primary keys: UUID (gen_random_uuid()) for all entities
--   - Money fields: NUMERIC(12,2)
--   - Hour/day fields: NUMERIC(6,2)
--   - All tables carry created_at / updated_at (auto-managed via trigger)
--   - Soft business-state via explicit ENUM types, not free-text strings
--   - Every FK has an explicit ON DELETE policy — never left implicit
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";      -- for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "btree_gist";    -- for exclusion constraints (contract overlap)

-- ---------------------------------------------------------------------
-- Generic updated_at trigger
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- ENUM TYPES
-- =====================================================================
CREATE TYPE role_name              AS ENUM ('EMPLOYEE','HR_MANAGER','HR_PAYROLL_USER','HR_PAYROLL_MANAGER','ADMIN');
CREATE TYPE employment_status      AS ENUM ('ACTIVE','INACTIVE','TERMINATED','ON_LEAVE');
CREATE TYPE contract_type          AS ENUM ('PERMANENT','FIXED_TERM','PROBATION','INTERN');
CREATE TYPE wage_type              AS ENUM ('MONTHLY','HOURLY');
CREATE TYPE contract_status        AS ENUM ('DRAFT','ACTIVE','EXPIRED','CANCELLED');
CREATE TYPE schedule_type          AS ENUM ('FULL_TIME','PART_TIME','FLEXIBLE');
CREATE TYPE day_of_week            AS ENUM ('MON','TUE','WED','THU','FRI','SAT','SUN');
CREATE TYPE attendance_status      AS ENUM ('PRESENT','ABSENT','LATE','HALF_DAY','ON_LEAVE','MISSING_CHECKOUT');
CREATE TYPE timeoff_unit           AS ENUM ('DAYS','HOURS');
CREATE TYPE approval_status        AS ENUM ('PENDING','APPROVED','REFUSED');
CREATE TYPE request_status         AS ENUM ('DRAFT','SUBMITTED','APPROVED','REFUSED','CANCELLED');
CREATE TYPE rule_category          AS ENUM ('BASIC','ALLOWANCE','GROSS','DEDUCTION','EMPLOYER_CONTRIBUTION','NET');
CREATE TYPE computation_type       AS ENUM ('FIXED','PERCENTAGE','FORMULA');
CREATE TYPE payrun_status          AS ENUM ('DRAFT','COMPUTED','VALIDATED','PAID','CANCELLED');
CREATE TYPE payslip_status         AS ENUM ('DRAFT','COMPUTED','VALIDATED','PAID','ERROR');
CREATE TYPE audit_action           AS ENUM ('CREATE','UPDATE','DELETE','APPROVE','REFUSE');

-- =====================================================================
-- 1. AUTH & ROLES  (User <-> Role is many-to-many)
-- =====================================================================
CREATE TABLE app_user (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email             VARCHAR(255) NOT NULL UNIQUE,
  password_hash     VARCHAR(255) NOT NULL,
  is_active         BOOLEAN NOT NULL DEFAULT TRUE,
  employee_id       UUID UNIQUE,                 -- FK added after employee table exists; NULL = admin-only account
  last_login_at     TIMESTAMPTZ,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_app_user_updated BEFORE UPDATE ON app_user
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE role (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name              role_name NOT NULL UNIQUE,
  description       TEXT
);

-- M2M: app_user <-> role
CREATE TABLE user_role (
  user_id           UUID NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
  role_id           UUID NOT NULL REFERENCES role(id) ON DELETE RESTRICT,
  assigned_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, role_id)
);

-- =====================================================================
-- 2. DEPARTMENT / JOB POSITION  (self-referencing department hierarchy)
-- =====================================================================
CREATE TABLE department (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name              VARCHAR(150) NOT NULL,
  parent_department_id UUID REFERENCES department(id) ON DELETE SET NULL,
  manager_employee_id  UUID,                      -- FK added after employee table exists
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_department_updated BEFORE UPDATE ON department
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE job_position (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title             VARCHAR(150) NOT NULL,
  department_id     UUID REFERENCES department(id) ON DELETE SET NULL,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- 3. WORKING SCHEDULE  (1 schedule -> many schedule lines)
-- =====================================================================
CREATE TABLE working_schedule (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name              VARCHAR(150) NOT NULL,
  schedule_type     schedule_type NOT NULL DEFAULT 'FULL_TIME',
  total_weekly_hours NUMERIC(6,2) NOT NULL DEFAULT 0,   -- kept in sync via app-layer recompute on line change
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_schedule_updated BEFORE UPDATE ON working_schedule
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE working_schedule_line (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  working_schedule_id UUID NOT NULL REFERENCES working_schedule(id) ON DELETE CASCADE,
  day               day_of_week NOT NULL,
  start_time        TIME NOT NULL,
  end_time          TIME NOT NULL,
  break_minutes     INT NOT NULL DEFAULT 0,
  CHECK (end_time > start_time),
  UNIQUE (working_schedule_id, day, start_time)   -- allows split shifts on same day, blocks exact dupes
);

-- =====================================================================
-- 4. EMPLOYEE  (central hub; self-referencing manager)
-- =====================================================================
CREATE TABLE employee (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_code     VARCHAR(30) NOT NULL UNIQUE,
  first_name        VARCHAR(100) NOT NULL,
  last_name         VARCHAR(100) NOT NULL,
  email             VARCHAR(255) NOT NULL UNIQUE,
  phone             VARCHAR(20),
  date_of_birth     DATE,
  gender            VARCHAR(20),
  date_joined       DATE NOT NULL,
  date_exit         DATE,
  address_line      VARCHAR(255),
  city              VARCHAR(100),
  state             VARCHAR(100),
  pincode           VARCHAR(12),
  profile_image_url TEXT,
  department_id     UUID REFERENCES department(id) ON DELETE SET NULL,
  job_position_id   UUID REFERENCES job_position(id) ON DELETE SET NULL,
  manager_id        UUID REFERENCES employee(id) ON DELETE SET NULL,   -- self-referencing
  default_working_schedule_id UUID REFERENCES working_schedule(id) ON DELETE SET NULL,
  employment_status employment_status NOT NULL DEFAULT 'ACTIVE',
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (date_exit IS NULL OR date_exit >= date_joined)
);
CREATE TRIGGER trg_employee_updated BEFORE UPDATE ON employee
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE INDEX idx_employee_department ON employee(department_id);
CREATE INDEX idx_employee_manager ON employee(manager_id);

-- Now that employee exists, wire the deferred FKs:
ALTER TABLE app_user
  ADD CONSTRAINT fk_app_user_employee FOREIGN KEY (employee_id) REFERENCES employee(id) ON DELETE SET NULL;
ALTER TABLE department
  ADD CONSTRAINT fk_department_manager FOREIGN KEY (manager_employee_id) REFERENCES employee(id) ON DELETE SET NULL;

-- Employee bank accounts (1 employee -> many accounts, one marked primary)
CREATE TABLE employee_bank_account (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_id       UUID NOT NULL REFERENCES employee(id) ON DELETE CASCADE,
  account_holder_name VARCHAR(150) NOT NULL,
  account_number    VARCHAR(50) NOT NULL,
  ifsc_code         VARCHAR(15),
  bank_name         VARCHAR(150),
  is_primary        BOOLEAN NOT NULL DEFAULT FALSE,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- Only one primary account per employee
CREATE UNIQUE INDEX uq_one_primary_account_per_employee
  ON employee_bank_account(employee_id) WHERE is_primary = TRUE;

-- =====================================================================
-- 5. SALARY STRUCTURE / SALARY RULE  (M2M with sequence attribute)
-- =====================================================================
CREATE TABLE salary_structure (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name              VARCHAR(150) NOT NULL,
  code              VARCHAR(50) NOT NULL UNIQUE,
  description       TEXT,
  is_active         BOOLEAN NOT NULL DEFAULT TRUE,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_structure_updated BEFORE UPDATE ON salary_structure
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE salary_rule (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code              VARCHAR(50) NOT NULL UNIQUE,     -- e.g. BASIC, HRA, PF, GROSS, NET — referenced by formulas
  name              VARCHAR(150) NOT NULL,
  category          rule_category NOT NULL,
  computation_type  computation_type NOT NULL,
  fixed_amount      NUMERIC(12,2),                   -- used when computation_type = FIXED
  percentage_of_rule_code VARCHAR(50) REFERENCES salary_rule(code) ON DELETE SET NULL, -- e.g. PF is % of BASIC
  percentage_value  NUMERIC(6,3),                     -- e.g. 12.000 (%)
  formula_expression TEXT,                            -- used when computation_type = FORMULA, references other codes
  is_active         BOOLEAN NOT NULL DEFAULT TRUE,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (
    (computation_type = 'FIXED'      AND fixed_amount IS NOT NULL) OR
    (computation_type = 'PERCENTAGE' AND percentage_of_rule_code IS NOT NULL AND percentage_value IS NOT NULL) OR
    (computation_type = 'FORMULA'    AND formula_expression IS NOT NULL)
  )
);

-- M2M: salary_structure <-> salary_rule, carrying per-structure sequence
CREATE TABLE salary_structure_rule (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  salary_structure_id UUID NOT NULL REFERENCES salary_structure(id) ON DELETE CASCADE,
  salary_rule_id    UUID NOT NULL REFERENCES salary_rule(id) ON DELETE RESTRICT,
  sequence          INT NOT NULL,
  UNIQUE (salary_structure_id, salary_rule_id),
  UNIQUE (salary_structure_id, sequence)             -- no two rules share a position in the same structure
);
CREATE INDEX idx_ssr_structure_seq ON salary_structure_rule(salary_structure_id, sequence);

-- =====================================================================
-- 6. CONTRACT  (1 employee -> many contracts over time; only one ACTIVE
--    contract may exist per employee at any given date)
-- =====================================================================
CREATE TABLE contract (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_id       UUID NOT NULL REFERENCES employee(id) ON DELETE CASCADE,
  contract_type     contract_type NOT NULL,
  start_date        DATE NOT NULL,
  end_date          DATE,                              -- NULL = open-ended
  wage_amount       NUMERIC(12,2) NOT NULL,
  wage_type         wage_type NOT NULL DEFAULT 'MONTHLY',
  salary_structure_id UUID NOT NULL REFERENCES salary_structure(id) ON DELETE RESTRICT,
  working_schedule_id UUID REFERENCES working_schedule(id) ON DELETE SET NULL,  -- overrides employee default if set
  department_id     UUID REFERENCES department(id) ON DELETE SET NULL,          -- snapshot at signing time
  job_position_id   UUID REFERENCES job_position(id) ON DELETE SET NULL,        -- snapshot at signing time
  status            contract_status NOT NULL DEFAULT 'DRAFT',
  signed_date       DATE,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (end_date IS NULL OR end_date >= start_date)
);
CREATE TRIGGER trg_contract_updated BEFORE UPDATE ON contract
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE INDEX idx_contract_employee_dates ON contract(employee_id, start_date, end_date);

-- CRITICAL INTEGRITY RULE: an employee cannot have two ACTIVE contracts
-- with overlapping date ranges. Enforced at the DB level, not just app code.
ALTER TABLE contract ADD CONSTRAINT excl_no_overlapping_active_contracts
  EXCLUDE USING gist (
    employee_id WITH =,
    daterange(start_date, COALESCE(end_date, 'infinity'::date), '[]') WITH &&
  ) WHERE (status = 'ACTIVE');

-- =====================================================================
-- 7. ATTENDANCE  (1 employee -> many attendance rows, 1 per work_date)
-- =====================================================================
CREATE TABLE attendance (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_id       UUID NOT NULL REFERENCES employee(id) ON DELETE CASCADE,
  work_date         DATE NOT NULL,
  check_in          TIMESTAMPTZ,
  check_out         TIMESTAMPTZ,
  worked_hours      NUMERIC(6,2),                     -- computed server-side from check_in/check_out
  status            attendance_status NOT NULL DEFAULT 'PRESENT',
  is_manual_correction BOOLEAN NOT NULL DEFAULT FALSE,
  corrected_by_user_id UUID REFERENCES app_user(id) ON DELETE SET NULL,
  correction_reason TEXT,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (employee_id, work_date),
  CHECK (check_out IS NULL OR check_in IS NULL OR check_out > check_in)
);
CREATE TRIGGER trg_attendance_updated BEFORE UPDATE ON attendance
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE INDEX idx_attendance_employee_date ON attendance(employee_id, work_date);

-- =====================================================================
-- 8. TIME OFF  (Employee <-> TimeOffType is M2M via allocation, which
--    carries balance attributes — an associative entity, not a bare join)
-- =====================================================================
CREATE TABLE time_off_type (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name              VARCHAR(100) NOT NULL UNIQUE,
  unit              timeoff_unit NOT NULL DEFAULT 'DAYS',
  requires_allocation BOOLEAN NOT NULL DEFAULT TRUE,
  requires_approval BOOLEAN NOT NULL DEFAULT TRUE,
  affects_payroll   BOOLEAN NOT NULL DEFAULT FALSE,
  color             VARCHAR(20),
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- M2M (associative entity): employee <-> time_off_type
CREATE TABLE time_off_allocation (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_id       UUID NOT NULL REFERENCES employee(id) ON DELETE CASCADE,
  time_off_type_id  UUID NOT NULL REFERENCES time_off_type(id) ON DELETE RESTRICT,
  allocated_amount  NUMERIC(6,2) NOT NULL,
  taken_amount      NUMERIC(6,2) NOT NULL DEFAULT 0,
  remaining_amount  NUMERIC(6,2) GENERATED ALWAYS AS (allocated_amount - taken_amount) STORED,
  valid_from        DATE NOT NULL,
  valid_to          DATE NOT NULL,
  approval_status   approval_status NOT NULL DEFAULT 'PENDING',
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (valid_to >= valid_from),
  CHECK (taken_amount >= 0 AND taken_amount <= allocated_amount)
);
CREATE TRIGGER trg_allocation_updated BEFORE UPDATE ON time_off_allocation
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE INDEX idx_allocation_employee_type ON time_off_allocation(employee_id, time_off_type_id);

CREATE TABLE time_off_request (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_id       UUID NOT NULL REFERENCES employee(id) ON DELETE CASCADE,
  time_off_type_id  UUID NOT NULL REFERENCES time_off_type(id) ON DELETE RESTRICT,
  allocation_id     UUID REFERENCES time_off_allocation(id) ON DELETE SET NULL,  -- which balance this draws from
  start_date        DATE NOT NULL,
  end_date          DATE NOT NULL,
  duration          NUMERIC(6,2) NOT NULL,             -- in the unit defined by time_off_type
  status            request_status NOT NULL DEFAULT 'DRAFT',
  approved_by_user_id UUID REFERENCES app_user(id) ON DELETE SET NULL,
  approved_at       TIMESTAMPTZ,
  reason            TEXT,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (end_date >= start_date)
);
CREATE TRIGGER trg_request_updated BEFORE UPDATE ON time_off_request
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE INDEX idx_request_employee_status ON time_off_request(employee_id, status);

-- =====================================================================
-- 9. PAYRUN / PAYSLIP  (Payrun <-> Employee is M2M, realized through
--    Payslip as a rich associative entity)
-- =====================================================================
CREATE TABLE payrun (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name              VARCHAR(150) NOT NULL,
  period_start      DATE NOT NULL,
  period_end        DATE NOT NULL,
  salary_structure_id UUID NOT NULL REFERENCES salary_structure(id) ON DELETE RESTRICT,
  status            payrun_status NOT NULL DEFAULT 'DRAFT',
  created_by_user_id UUID REFERENCES app_user(id) ON DELETE SET NULL,
  computed_at       TIMESTAMPTZ,
  validated_at      TIMESTAMPTZ,
  paid_at           TIMESTAMPTZ,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (period_end >= period_start)
);
CREATE INDEX idx_payrun_period ON payrun(period_start, period_end);

-- Associative entity for the Payrun <-> Employee M2M relationship
CREATE TABLE payslip (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  payrun_id         UUID NOT NULL REFERENCES payrun(id) ON DELETE CASCADE,
  employee_id       UUID NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
  contract_id       UUID NOT NULL REFERENCES contract(id) ON DELETE RESTRICT,  -- resolved active contract, snapshot
  period_start      DATE NOT NULL,
  period_end        DATE NOT NULL,
  worked_days       NUMERIC(6,2),
  status            payslip_status NOT NULL DEFAULT 'DRAFT',
  gross_amount      NUMERIC(12,2),
  net_amount        NUMERIC(12,2),
  has_warning       BOOLEAN NOT NULL DEFAULT FALSE,
  warning_notes     TEXT,
  pdf_url           TEXT,
  sent_at           TIMESTAMPTZ,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (payrun_id, employee_id)                      -- one payslip per employee per payrun — blocks duplicates
);
CREATE TRIGGER trg_payslip_updated BEFORE UPDATE ON payslip
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE INDEX idx_payslip_employee ON payslip(employee_id);
CREATE INDEX idx_payslip_payrun ON payslip(payrun_id);

CREATE TABLE payslip_line (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  payslip_id        UUID NOT NULL REFERENCES payslip(id) ON DELETE CASCADE,
  salary_rule_id    UUID REFERENCES salary_rule(id) ON DELETE SET NULL,
  salary_rule_code  VARCHAR(50) NOT NULL,               -- denormalized snapshot: historical payslips stay accurate
                                                          -- even if the rule is later renamed or deleted
  sequence          INT NOT NULL,
  amount            NUMERIC(12,2) NOT NULL,
  computation_detail JSONB,                              -- e.g. {"base":"BASIC","pct":12,"input_amount":30000}
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_payslip_line_payslip ON payslip_line(payslip_id, sequence);

-- =====================================================================
-- 10. AUDIT LOG  (cross-cutting — every sensitive action tracked)
-- =====================================================================
CREATE TABLE audit_log (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           UUID REFERENCES app_user(id) ON DELETE SET NULL,
  entity_name       VARCHAR(100) NOT NULL,
  entity_id         UUID NOT NULL,
  action            audit_action NOT NULL,
  field_changes     JSONB,
  reason            TEXT,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_entity ON audit_log(entity_name, entity_id);
CREATE INDEX idx_audit_user ON audit_log(user_id);

-- =====================================================================
-- SEED: default roles (safe to run once)
-- =====================================================================
INSERT INTO role (name, description) VALUES
  ('EMPLOYEE', 'Views own profile, attendance, leave, and payslips'),
  ('HR_MANAGER', 'Full CRUD on Employees, Contracts, Attendance, Time Off'),
  ('HR_PAYROLL_USER', 'HR Manager rights + create/read/update Payruns & Payslips'),
  ('HR_PAYROLL_MANAGER', 'Full CRUD on Payroll, Salary Structures, and Salary Rules'),
  ('ADMIN', 'Full system access')
ON CONFLICT (name) DO NOTHING;

-- =====================================================================
-- 21. REFRESH TOKENS  (opaque, hashed; supports rotation & revocation)
-- Added post-hoc for the login/refresh-cookie auth flow — not present in
-- the original schema pass. See refresh_token.sql for the standalone,
-- already-applied-safe version of this same DDL.
-- =====================================================================
CREATE TABLE IF NOT EXISTS refresh_token (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           UUID NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
  token_hash        VARCHAR(255) NOT NULL UNIQUE,
  expires_at        TIMESTAMPTZ NOT NULL,
  revoked_at        TIMESTAMPTZ,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_refresh_token_user ON refresh_token(user_id);
