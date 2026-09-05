-- =====================================================================
-- PeoplePay360 — Comprehensive Seed & Dummy Data Script
-- Built for PostgreSQL 15+ / Neon DB
-- Clean 001/002 UUID IDs, E001..E005 Employee Codes, Password@123
-- =====================================================================

BEGIN;

-- ---------------------------------------------------------------------
-- 0. CLEANUP (TRUNCATE ALL DATA RESPECTING FK CONSTRAINTS)
-- ---------------------------------------------------------------------
TRUNCATE 
  audit_log, payslip_line, payslip, payrun, time_off_request, 
  time_off_allocation, time_off_type, attendance, contract, 
  salary_structure_rule, salary_rule, salary_structure, 
  employee_bank_account, user_role, app_user, employee, 
  job_position, department, working_schedule_line, working_schedule 
RESTART IDENTITY CASCADE;

-- ---------------------------------------------------------------------
-- 1. WORKING SCHEDULES & SCHEDULE LINES
-- ---------------------------------------------------------------------
INSERT INTO working_schedule (id, name, schedule_type, total_weekly_hours)
VALUES 
  ('00000000-0000-0000-0001-000000000001', 'Standard Full-Time (40h)', 'FULL_TIME', 40.00),
  ('00000000-0000-0000-0001-000000000002', 'Flexible Part-Time (20h)', 'PART_TIME', 20.00);

INSERT INTO working_schedule_line (id, working_schedule_id, day, start_time, end_time, break_minutes)
VALUES
  -- Standard 40h (Mon-Fri 09:00 - 18:00 with 60 min break = 8h/day)
  (gen_random_uuid(), '00000000-0000-0000-0001-000000000001', 'MON', '09:00:00', '18:00:00', 60),
  (gen_random_uuid(), '00000000-0000-0000-0001-000000000001', 'TUE', '09:00:00', '18:00:00', 60),
  (gen_random_uuid(), '00000000-0000-0000-0001-000000000001', 'WED', '09:00:00', '18:00:00', 60),
  (gen_random_uuid(), '00000000-0000-0000-0001-000000000001', 'THU', '09:00:00', '18:00:00', 60),
  (gen_random_uuid(), '00000000-0000-0000-0001-000000000001', 'FRI', '09:00:00', '18:00:00', 60),
  -- Part-time 20h (Mon-Fri 09:00 - 13:00 with 0 min break = 4h/day)
  (gen_random_uuid(), '00000000-0000-0000-0001-000000000002', 'MON', '09:00:00', '13:00:00', 0),
  (gen_random_uuid(), '00000000-0000-0000-0001-000000000002', 'TUE', '09:00:00', '13:00:00', 0),
  (gen_random_uuid(), '00000000-0000-0000-0001-000000000002', 'WED', '09:00:00', '13:00:00', 0),
  (gen_random_uuid(), '00000000-0000-0000-0001-000000000002', 'THU', '09:00:00', '13:00:00', 0),
  (gen_random_uuid(), '00000000-0000-0000-0001-000000000002', 'FRI', '09:00:00', '13:00:00', 0);

-- ---------------------------------------------------------------------
-- 2. DEPARTMENTS
-- ---------------------------------------------------------------------
INSERT INTO department (id, name, parent_department_id)
VALUES 
  ('d0000000-0000-0000-0000-000000000001', 'Engineering', NULL),
  ('d0000000-0000-0000-0000-000000000002', 'Software Development', 'd0000000-0000-0000-0000-000000000001'),
  ('d0000000-0000-0000-0000-000000000003', 'Quality Assurance', 'd0000000-0000-0000-0000-000000000001'),
  ('d0000000-0000-0000-0000-000000000004', 'Human Resources', NULL),
  ('d0000000-0000-0000-0000-000000000005', 'Finance & Payroll', NULL);

-- ---------------------------------------------------------------------
-- 3. JOB POSITIONS
-- ---------------------------------------------------------------------
INSERT INTO job_position (id, title, department_id)
VALUES
  ('00000000-0000-0000-0000-000000000001', 'Engineering Lead', 'd0000000-0000-0000-0000-000000000001'),
  ('00000000-0000-0000-0000-000000000002', 'Senior Software Engineer', 'd0000000-0000-0000-0000-000000000002'),
  ('00000000-0000-0000-0000-000000000003', 'QA Automation Engineer', 'd0000000-0000-0000-0000-000000000003'),
  ('00000000-0000-0000-0000-000000000004', 'HR Manager', 'd0000000-0000-0000-0000-000000000004'),
  ('00000000-0000-0000-0000-000000000005', 'Payroll Specialist', 'd0000000-0000-0000-0000-000000000005');

-- ---------------------------------------------------------------------
-- 4. EMPLOYEES (IDs like e000...001 and Employee Codes E001..E005)
-- ---------------------------------------------------------------------
INSERT INTO employee (
  id, employee_code, first_name, last_name, email, phone, date_of_birth, gender,
  date_joined, department_id, job_position_id, default_working_schedule_id, employment_status
) VALUES
  ('e0000000-0000-0000-0000-000000000001', 'E001', 'Alice', 'Smith', 'alice.smith@peoplepay360.com', '+15550101', '1988-03-15', 'Female', '2022-01-10', 'd0000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000004', '00000000-0000-0000-0001-000000000001', 'ACTIVE'),
  ('e0000000-0000-0000-0000-000000000002', 'E002', 'Bob', 'Johnson', 'bob.johnson@peoplepay360.com', '+15550102', '1990-07-22', 'Male', '2022-03-01', 'd0000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000005', '00000000-0000-0000-0001-000000000001', 'ACTIVE'),
  ('e0000000-0000-0000-0000-000000000003', 'E003', 'Charlie', 'Davis', 'charlie.davis@peoplepay360.com', '+15550103', '1985-11-05', 'Male', '2021-06-15', 'd0000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0001-000000000001', 'ACTIVE'),
  ('e0000000-0000-0000-0000-000000000004', 'E004', 'David', 'Miller', 'david.miller@peoplepay360.com', '+15550104', '1993-02-18', 'Male', '2023-01-09', 'd0000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0001-000000000001', 'ACTIVE'),
  ('e0000000-0000-0000-0000-000000000005', 'E005', 'Eva', 'Wilson', 'eva.wilson@peoplepay360.com', '+15550105', '1995-09-30', 'Female', '2023-05-20', 'd0000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0001-000000000001', 'ACTIVE');

-- Set Manager Relationships
UPDATE employee SET manager_id = 'e0000000-0000-0000-0000-000000000003' WHERE id IN ('e0000000-0000-0000-0000-000000000004', 'e0000000-0000-0000-0000-000000000005');

UPDATE department SET manager_employee_id = 'e0000000-0000-0000-0000-000000000001' WHERE id = 'd0000000-0000-0000-0000-000000000004';
UPDATE department SET manager_employee_id = 'e0000000-0000-0000-0000-000000000002' WHERE id = 'd0000000-0000-0000-0000-000000000005';
UPDATE department SET manager_employee_id = 'e0000000-0000-0000-0000-000000000003' WHERE id IN ('d0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000002', 'd0000000-0000-0000-0000-000000000003');

-- ---------------------------------------------------------------------
-- 5. APP USERS & USER ROLES (Password for all users: Password@123)
-- ---------------------------------------------------------------------
INSERT INTO app_user (id, email, password_hash, is_active, employee_id)
VALUES
  ('a0000000-0000-0000-0000-000000000000', 'admin@peoplepay360.com', crypt('Password@123', gen_salt('bf')), TRUE, NULL),
  ('a0000000-0000-0000-0000-000000000001', 'alice.hr@peoplepay360.com', crypt('Password@123', gen_salt('bf')), TRUE, 'e0000000-0000-0000-0000-000000000001'),
  ('a0000000-0000-0000-0000-000000000002', 'bob.payroll@peoplepay360.com', crypt('Password@123', gen_salt('bf')), TRUE, 'e0000000-0000-0000-0000-000000000002'),
  ('a0000000-0000-0000-0000-000000000003', 'charlie.lead@peoplepay360.com', crypt('Password@123', gen_salt('bf')), TRUE, 'e0000000-0000-0000-0000-000000000003'),
  ('a0000000-0000-0000-0000-000000000004', 'david.dev@peoplepay360.com', crypt('Password@123', gen_salt('bf')), TRUE, 'e0000000-0000-0000-0000-000000000004'),
  ('a0000000-0000-0000-0000-000000000005', 'eva.qa@peoplepay360.com', crypt('Password@123', gen_salt('bf')), TRUE, 'e0000000-0000-0000-0000-000000000005');

-- Map roles to app_users
INSERT INTO user_role (user_id, role_id)
SELECT 'a0000000-0000-0000-0000-000000000000', id FROM role WHERE name = 'ADMIN';

INSERT INTO user_role (user_id, role_id)
SELECT 'a0000000-0000-0000-0000-000000000001', id FROM role WHERE name = 'HR_MANAGER';

INSERT INTO user_role (user_id, role_id)
SELECT 'a0000000-0000-0000-0000-000000000002', id FROM role WHERE name = 'HR_PAYROLL_MANAGER';

INSERT INTO user_role (user_id, role_id)
SELECT 'a0000000-0000-0000-0000-000000000003', id FROM role WHERE name = 'EMPLOYEE';

INSERT INTO user_role (user_id, role_id)
SELECT 'a0000000-0000-0000-0000-000000000004', id FROM role WHERE name = 'EMPLOYEE';

INSERT INTO user_role (user_id, role_id)
SELECT 'a0000000-0000-0000-0000-000000000005', id FROM role WHERE name = 'EMPLOYEE';

-- ---------------------------------------------------------------------
-- 6. EMPLOYEE BANK ACCOUNTS (One primary per employee)
-- ---------------------------------------------------------------------
INSERT INTO employee_bank_account (id, employee_id, account_holder_name, account_number, ifsc_code, bank_name, is_primary)
VALUES
  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000001', 'Alice Smith', '998877665501', 'HDFC0001234', 'HDFC Bank', TRUE),
  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000002', 'Bob Johnson', '998877665502', 'ICIC0005678', 'ICICI Bank', TRUE),
  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000003', 'Charlie Davis', '998877665503', 'SBIN0009999', 'State Bank of India', TRUE),
  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000004', 'David Miller', '998877665504', 'UTIB0004321', 'Axis Bank', TRUE),
  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000005', 'Eva Wilson', '998877665505', 'KKBK0008888', 'Kotak Mahindra Bank', TRUE);

-- ---------------------------------------------------------------------
-- 7. SALARY STRUCTURES & SALARY RULES
-- ---------------------------------------------------------------------
INSERT INTO salary_structure (id, name, code, description, is_active)
VALUES
  ('00000000-0000-0000-0002-000000000001', 'Standard Corporate Salary Structure', 'STD_SAL_2026', 'Default salary structure for regular full-time employees', TRUE);

-- Insert rules in order of computation
INSERT INTO salary_rule (id, code, name, category, computation_type, fixed_amount, percentage_of_rule_code, percentage_value, formula_expression, is_active)
VALUES
  ('00000000-0000-0000-0002-000000000011', 'BASIC', 'Basic Salary', 'BASIC', 'FIXED', 50000.00, NULL, NULL, NULL, TRUE),
  ('00000000-0000-0000-0002-000000000012', 'HRA', 'House Rent Allowance', 'ALLOWANCE', 'PERCENTAGE', NULL, 'BASIC', 40.000, NULL, TRUE),
  ('00000000-0000-0000-0002-000000000013', 'CONVEYANCE', 'Conveyance Allowance', 'ALLOWANCE', 'FIXED', 3000.00, NULL, NULL, NULL, TRUE),
  ('00000000-0000-0000-0002-000000000014', 'GROSS', 'Gross Total', 'GROSS', 'FORMULA', NULL, NULL, NULL, 'BASIC + HRA + CONVEYANCE', TRUE),
  ('00000000-0000-0000-0002-000000000015', 'PF', 'Provident Fund Deduction', 'DEDUCTION', 'PERCENTAGE', NULL, 'BASIC', 12.000, NULL, TRUE),
  ('00000000-0000-0000-0002-000000000016', 'TAX', 'Income Tax Deduction', 'DEDUCTION', 'FIXED', 2500.00, NULL, NULL, NULL, TRUE),
  ('00000000-0000-0000-0002-000000000017', 'NET', 'Net Payable Salary', 'NET', 'FORMULA', NULL, NULL, NULL, 'GROSS - PF - TAX', TRUE);

-- Attach rules to salary structure with strictly ordered sequence
INSERT INTO salary_structure_rule (id, salary_structure_id, salary_rule_id, sequence)
VALUES
  (gen_random_uuid(), '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0002-000000000011', 10),
  (gen_random_uuid(), '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0002-000000000012', 20),
  (gen_random_uuid(), '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0002-000000000013', 30),
  (gen_random_uuid(), '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0002-000000000014', 40),
  (gen_random_uuid(), '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0002-000000000015', 50),
  (gen_random_uuid(), '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0002-000000000016', 60),
  (gen_random_uuid(), '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0002-000000000017', 70);

-- ---------------------------------------------------------------------
-- 8. CONTRACTS
-- ---------------------------------------------------------------------
-- Enforces: Single ACTIVE contract per employee across overlapping date ranges
INSERT INTO contract (
  id, employee_id, contract_type, start_date, end_date, wage_amount, wage_type,
  salary_structure_id, working_schedule_id, department_id, job_position_id, status, signed_date
) VALUES
  -- Alice Smith (Active)
  ('c0000000-0000-0000-0000-000000000001', 'e0000000-0000-0000-0000-000000000001', 'PERMANENT', '2026-01-01', NULL, 85000.00, 'MONTHLY', '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0001-000000000001', 'd0000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000004', 'ACTIVE', '2025-12-28'),
  -- Bob Johnson (Active)
  ('c0000000-0000-0000-0000-000000000002', 'e0000000-0000-0000-0000-000000000002', 'PERMANENT', '2026-01-01', NULL, 75000.00, 'MONTHLY', '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0001-000000000001', 'd0000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000005', 'ACTIVE', '2025-12-29'),
  -- Charlie Davis (Active)
  ('c0000000-0000-0000-0000-000000000003', 'e0000000-0000-0000-0000-000000000003', 'PERMANENT', '2026-01-01', NULL, 120000.00, 'MONTHLY', '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0001-000000000001', 'd0000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'ACTIVE', '2025-12-20'),
  -- David Miller (Active)
  ('c0000000-0000-0000-0000-000000000004', 'e0000000-0000-0000-0000-000000000004', 'PERMANENT', '2026-01-01', NULL, 90000.00, 'MONTHLY', '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0001-000000000001', 'd0000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000002', 'ACTIVE', '2025-12-30'),
  -- David Miller (Historical EXPIRED contract from 2025 - Non-overlapping status=EXPIRED)
  ('c0000000-0000-0000-0000-000000000099', 'e0000000-0000-0000-0000-000000000004', 'PROBATION', '2025-01-01', '2025-12-31', 70000.00, 'MONTHLY', '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0001-000000000001', 'd0000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000002', 'EXPIRED', '2024-12-28'),
  -- Eva Wilson (Active)
  ('c0000000-0000-0000-0000-000000000005', 'e0000000-0000-0000-0000-000000000005', 'FIXED_TERM', '2026-01-01', '2026-12-31', 70000.00, 'MONTHLY', '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0001-000000000001', 'd0000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000003', 'ACTIVE', '2025-12-29');

-- ---------------------------------------------------------------------
-- 9. ATTENDANCE RECORDS
-- ---------------------------------------------------------------------
INSERT INTO attendance (id, employee_id, work_date, check_in, check_out, worked_hours, status, is_manual_correction, corrected_by_user_id, correction_reason)
VALUES
  -- Regular daily logs for August 2026
  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000004', '2026-08-03', '2026-08-03 09:00:00+00', '2026-08-03 18:00:00+00', 8.00, 'PRESENT', FALSE, NULL, NULL),
  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000004', '2026-08-04', '2026-08-04 09:15:00+00', '2026-08-04 18:00:00+00', 7.75, 'LATE', FALSE, NULL, NULL),
  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000004', '2026-08-05', '2026-08-05 09:00:00+00', '2026-08-05 18:00:00+00', 8.00, 'PRESENT', TRUE, 'a0000000-0000-0000-0000-000000000001', 'Employee forgot to tap badge; verified via manager'),
  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000005', '2026-08-03', '2026-08-03 08:55:00+00', '2026-08-03 18:00:00+00', 8.00, 'PRESENT', FALSE, NULL, NULL),
  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000005', '2026-08-04', '2026-08-04 09:00:00+00', '2026-08-04 18:00:00+00', 8.00, 'PRESENT', FALSE, NULL, NULL);

-- ---------------------------------------------------------------------
-- 10. TIME OFF TYPES, ALLOCATIONS, AND REQUESTS
-- ---------------------------------------------------------------------
INSERT INTO time_off_type (id, name, unit, requires_allocation, requires_approval, affects_payroll, color)
VALUES
  ('00000000-0000-0000-0003-000000000001', 'Paid Time Off (PTO)', 'DAYS', TRUE, TRUE, TRUE, '#3B82F6'),
  ('00000000-0000-0000-0003-000000000002', 'Sick Leave', 'DAYS', TRUE, TRUE, FALSE, '#EF4444'),
  ('00000000-0000-0000-0003-000000000003', 'Unpaid Leave', 'DAYS', FALSE, TRUE, TRUE, '#6B7280');

-- Allocations (remaining_amount is GENERATED ALWAYS AS (allocated_amount - taken_amount))
INSERT INTO time_off_allocation (id, employee_id, time_off_type_id, allocated_amount, taken_amount, valid_from, valid_to, approval_status)
VALUES
  ('00000000-0000-0000-0003-000000000101', 'e0000000-0000-0000-0000-000000000004', '00000000-0000-0000-0003-000000000001', 20.00, 3.00, '2026-01-01', '2026-12-31', 'APPROVED'),
  ('00000000-0000-0000-0003-000000000102', 'e0000000-0000-0000-0000-000000000004', '00000000-0000-0000-0003-000000000002', 10.00, 0.00, '2026-01-01', '2026-12-31', 'APPROVED'),
  ('00000000-0000-0000-0003-000000000103', 'e0000000-0000-0000-0000-000000000005', '00000000-0000-0000-0003-000000000001', 20.00, 0.00, '2026-01-01', '2026-12-31', 'APPROVED');

-- Time Off Requests
INSERT INTO time_off_request (id, employee_id, time_off_type_id, allocation_id, start_date, end_date, duration, status, approved_by_user_id, reason)
VALUES
  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000004', '00000000-0000-0000-0003-000000000001', '00000000-0000-0000-0003-000000000101', '2026-08-10', '2026-08-12', 3.00, 'APPROVED', 'a0000000-0000-0000-0000-000000000001', 'Summer Vacation'),
  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000005', '00000000-0000-0000-0003-000000000001', '00000000-0000-0000-0003-000000000103', '2026-09-15', '2026-09-16', 2.00, 'SUBMITTED', NULL, 'Personal errands');

-- ---------------------------------------------------------------------
-- 11. PAYRUN, PAYSLIP, AND PAYSLIP LINES
-- ---------------------------------------------------------------------
INSERT INTO payrun (id, name, period_start, period_end, salary_structure_id, status, created_by_user_id, computed_at, validated_at, paid_at)
VALUES
  ('00000000-0000-0000-0004-000000000001', 'August 2026 Monthly Payroll', '2026-08-01', '2026-08-31', '00000000-0000-0000-0002-000000000001', 'PAID', 'a0000000-0000-0000-0000-000000000002', '2026-08-28 10:00:00+00', '2026-08-29 14:00:00+00', '2026-08-31 09:00:00+00');

-- Payslips for employees in August 2026 payrun
-- Gross = BASIC(50000) + HRA(20000) + CONVEYANCE(3000) = 73000
-- Deductions = PF(6000) + TAX(2500) = 8500
-- Net = 73000 - 8500 = 64500
INSERT INTO payslip (id, payrun_id, employee_id, contract_id, period_start, period_end, worked_days, status, gross_amount, net_amount, has_warning, warning_notes)
VALUES
  ('00000000-0000-0000-0004-000000000101', '00000000-0000-0000-0004-000000000001', 'e0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', '2026-08-01', '2026-08-31', 22.00, 'PAID', 73000.00, 64500.00, FALSE, NULL),
  ('00000000-0000-0000-0004-000000000102', '00000000-0000-0000-0004-000000000001', 'e0000000-0000-0000-0000-000000000002', 'c0000000-0000-0000-0000-000000000002', '2026-08-01', '2026-08-31', 22.00, 'PAID', 73000.00, 64500.00, FALSE, NULL),
  ('00000000-0000-0000-0004-000000000103', '00000000-0000-0000-0004-000000000001', 'e0000000-0000-0000-0000-000000000003', 'c0000000-0000-0000-0000-000000000003', '2026-08-01', '2026-08-31', 22.00, 'PAID', 73000.00, 64500.00, FALSE, NULL),
  ('00000000-0000-0000-0004-000000000104', '00000000-0000-0000-0004-000000000001', 'e0000000-0000-0000-0000-000000000004', 'c0000000-0000-0000-0000-000000000004', '2026-08-01', '2026-08-31', 22.00, 'PAID', 73000.00, 64500.00, FALSE, NULL),
  ('00000000-0000-0000-0004-000000000105', '00000000-0000-0000-0004-000000000001', 'e0000000-0000-0000-0000-000000000005', 'c0000000-0000-0000-0000-000000000005', '2026-08-01', '2026-08-31', 22.00, 'PAID', 73000.00, 64500.00, FALSE, NULL);

-- Payslip Lines (Denormalized snapshot of salary rule computations)
INSERT INTO payslip_line (id, payslip_id, salary_rule_id, salary_rule_code, sequence, amount, computation_detail)
VALUES
  -- Lines for Alice Smith
  (gen_random_uuid(), '00000000-0000-0000-0004-000000000101', '00000000-0000-0000-0002-000000000011', 'BASIC', 10, 50000.00, '{"type": "FIXED", "value": 50000.00}'::jsonb),
  (gen_random_uuid(), '00000000-0000-0000-0004-000000000101', '00000000-0000-0000-0002-000000000012', 'HRA', 20, 20000.00, '{"type": "PERCENTAGE", "pct": 40.0, "base": 50000.00}'::jsonb),
  (gen_random_uuid(), '00000000-0000-0000-0004-000000000101', '00000000-0000-0000-0002-000000000013', 'CONVEYANCE', 30, 3000.00, '{"type": "FIXED", "value": 3000.00}'::jsonb),
  (gen_random_uuid(), '00000000-0000-0000-0004-000000000101', '00000000-0000-0000-0002-000000000014', 'GROSS', 40, 73000.00, '{"type": "FORMULA", "expression": "BASIC + HRA + CONVEYANCE"}'::jsonb),
  (gen_random_uuid(), '00000000-0000-0000-0004-000000000101', '00000000-0000-0000-0002-000000000015', 'PF', 50, 6000.00, '{"type": "PERCENTAGE", "pct": 12.0, "base": 50000.00}'::jsonb),
  (gen_random_uuid(), '00000000-0000-0000-0004-000000000101', '00000000-0000-0000-0002-000000000016', 'TAX', 60, 2500.00, '{"type": "FIXED", "value": 2500.00}'::jsonb),
  (gen_random_uuid(), '00000000-0000-0000-0004-000000000101', '00000000-0000-0000-0002-000000000017', 'NET', 70, 64500.00, '{"type": "FORMULA", "expression": "GROSS - PF - TAX"}'::jsonb),
  
  -- Lines for David Miller
  (gen_random_uuid(), '00000000-0000-0000-0004-000000000104', '00000000-0000-0000-0002-000000000011', 'BASIC', 10, 50000.00, '{"type": "FIXED", "value": 50000.00}'::jsonb),
  (gen_random_uuid(), '00000000-0000-0000-0004-000000000104', '00000000-0000-0000-0002-000000000012', 'HRA', 20, 20000.00, '{"type": "PERCENTAGE", "pct": 40.0, "base": 50000.00}'::jsonb),
  (gen_random_uuid(), '00000000-0000-0000-0004-000000000104', '00000000-0000-0000-0002-000000000013', 'CONVEYANCE', 30, 3000.00, '{"type": "FIXED", "value": 3000.00}'::jsonb),
  (gen_random_uuid(), '00000000-0000-0000-0004-000000000104', '00000000-0000-0000-0002-000000000014', 'GROSS', 40, 73000.00, '{"type": "FORMULA", "expression": "BASIC + HRA + CONVEYANCE"}'::jsonb),
  (gen_random_uuid(), '00000000-0000-0000-0004-000000000104', '00000000-0000-0000-0002-000000000015', 'PF', 50, 6000.00, '{"type": "PERCENTAGE", "pct": 12.0, "base": 50000.00}'::jsonb),
  (gen_random_uuid(), '00000000-0000-0000-0004-000000000104', '00000000-0000-0000-0002-000000000016', 'TAX', 60, 2500.00, '{"type": "FIXED", "value": 2500.00}'::jsonb),
  (gen_random_uuid(), '00000000-0000-0000-0004-000000000104', '00000000-0000-0000-0002-000000000017', 'NET', 70, 64500.00, '{"type": "FORMULA", "expression": "GROSS - PF - TAX"}'::jsonb);

-- ---------------------------------------------------------------------
-- 12. AUDIT LOGS
-- ---------------------------------------------------------------------
INSERT INTO audit_log (id, user_id, entity_name, entity_id, action, field_changes, reason)
VALUES
  (gen_random_uuid(), 'a0000000-0000-0000-0000-000000000001', 'contract', 'c0000000-0000-0000-0000-000000000004', 'APPROVE', '{"status": {"old": "DRAFT", "new": "ACTIVE"}}'::jsonb, 'Approved initial employee contract'),
  (gen_random_uuid(), 'a0000000-0000-0000-0000-000000000001', 'time_off_request', '00000000-0000-0000-0003-000000000101', 'APPROVE', '{"status": {"old": "SUBMITTED", "new": "APPROVED"}}'::jsonb, 'Approved summer vacation leave request'),
  (gen_random_uuid(), 'a0000000-0000-0000-0000-000000000002', 'payrun', '00000000-0000-0000-0004-000000000001', 'UPDATE', '{"status": {"old": "VALIDATED", "new": "PAID"}}'::jsonb, 'Executed monthly salary payout');

COMMIT;
