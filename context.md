# Pexo — Team Context Document

_This is the single source of truth for the team. Read this before touching any code. Anything not covered here should be added here, not left as tribal knowledge in a chat thread._

---

## 1. What this project actually is

**Pexo** is our hackathon build: an **Integrated HR & Payroll Operations Platform**. We chose this over two other options (an Accounting system, and a Sales Ops platform called DealFlow360) because it gives us the best balance of:
- Rich, provable **data modeling** (contracts, schedules, leave, salary rules all interlinked)
- A genuine **rule-engine** component (Salary Rules executed in sequence) that differentiates us from a CRUD app
- A controllable build timeline compared to the more real-time/algorithmic sales platform

## 2. Odoo — the official context

Our problem statement is deliberately modeled on **Odoo's HR suite** — specifically the `hr`, `hr_attendance`, `hr_holidays` (Time Off), `hr_contract`, and `hr_payroll` modules. Understanding Odoo's actual design philosophy helps us build something judges will recognize as "industry-ready":

- **Employee as central hub**: In Odoo, the `hr.employee` model is the anchor; almost every other HR model (`hr.contract`, `hr.attendance`, `hr.leave`) has a `employee_id` foreign key pointing back to it, and the Employee form has "smart buttons" that jump to filtered views of related records. We replicate this exactly.
- **Period-based contract resolution**: Odoo payroll never asks "what is this employee's contract" — it asks "what is this employee's contract **on this date**", because employees can have multiple historical contracts. This is why our schema has a database-level constraint preventing two overlapping ACTIVE contracts per employee (see `schema.sql`, `excl_no_overlapping_active_contracts`).
- **Salary Rules as data, not code**: Odoo's payroll engine stores Salary Rules as records with a `sequence`, a `category` (Basic/Allowance/Deduction/Net), and a Python-expression-based computation. Rules are evaluated in sequence order, and later rules can reference earlier ones by code (e.g. `HRA = BASIC * 0.4`). We are replicating this pattern with our `salary_rule` + `salary_structure_rule` tables and a small formula evaluator — this is the single most "Odoo-authentic" piece of our build, and where we should invest the most care.
- **Two-step wizards**: Odoo's Payrun ("Batches" in Odoo terms) uses a wizard pattern — define scope first, then select employees — rather than a single giant form. This avoids accidentally including employees who shouldn't be in a payroll run.
- **Time Off allocations vs requests**: Odoo separates "how much leave you're entitled to" (Allocation) from "you're asking to use some of it" (Request) — this is why we don't just have a `leave_balance` integer field on Employee; we model it as its own entity with validity periods.

Knowing this lets us defend our design choices in front of judges: we're not just building forms, we're replicating a real system's business-logic philosophy.

## 3. Problem statement summary

Build an HR & Payroll platform that goes beyond CRUD and becomes a connected operational flow:
- **Employee** record is the central hub
- **Contracts** and **Working Schedules** provide payroll context (period-specific)
- **Attendance** and **Time Off** capture day-to-day HR activity
- **Salary Structures** and **Salary Rules** define computation logic
- **Payruns** turn eligible employees into validated **Payslips**, printable as PDF and emailable in bulk
- A **Payroll Dashboard** aggregates all of the above live

### Roles (5 total)
| Role | Access |
|---|---|
| Employee | Own profile, attendance, leave balances; can submit attendance/leave requests |
| HR Manager | Full CRUD on Employees, Contracts, Attendance, Working Schedules, Time Off; no payroll access |
| HR Payroll User | HR Manager rights + create/read/update Payruns & Payslips; read-only Salary Structures/Rules |
| HR Payroll Manager | Everything HR Payroll User has + full CRUD on Payroll, Salary Structures, Salary Rules |
| Admin | Full system access, user/role management |

## 4. Final tech stack

```
Backend:    FastAPI (async) + SQLAlchemy 2.0 (async) + Alembic + Pydantic v2
Database:   PostgreSQL 15+ (UUID PKs, ENUM types, exclusion constraints, generated columns)
Caching/MQ: Redis (dual purpose — cache layer + Celery broker)
Automation: Celery + Celery Beat + WeasyPrint (PDF) + FastAPI-Mail
Storage:    Azure Blob Storage (Azurite emulator for local dev) — payslip PDFs, profile images
Frontend:   React + Vite + Tailwind + Redux Toolkit + TanStack Query (React Query)
DevOps:     Docker + Docker Compose + GitHub Actions + pre-commit (black, isort, ruff, mypy)
Monitoring: Sentry (free tier) — optional, adds production-readiness credibility for the demo
```

**Why each piece, briefly:**
- **FastAPI over Django**: async-native, auto-generates OpenAPI schema we use to keep frontend TypeScript types in sync.
- **SQLAlchemy + Alembic**: strict relational integrity is non-negotiable for payroll — we need real foreign keys, exclusion constraints, and versioned migrations across 4 people editing schema.
- **Redis doing double duty**: avoids standing up two separate infra pieces during a hackathon.
- **Redux Toolkit + React Query split**: Redux owns UI/app state (current wizard step, filters), React Query owns server state (employee lists, dashboard KPIs) — prevents the common mistake of manually managing loading/error/cache state in Redux.
- **Azure Blob (not S3)**: team already has Azure credits; Azurite gives us a local emulator so no code changes between dev and demo deployment.

## 5. Architecture (microservices, service-per-domain)

```
services/
├── hr-service/                  # Employee, Contract, Working Schedule
├── attendance-timeoff-service/  # Attendance, Time Off Types/Allocations/Requests
├── payroll-service/             # Salary Structure/Rule, Payrun, Payslip, rule engine
└── api-gateway/                 # Auth, role middleware, dashboard aggregation, frontend-facing routing
frontend/                        # React app, one feature folder per service
shared/                          # Cross-service Python libs + generated TS types (edit sparingly)
infra/                           # docker-compose, nginx
```

Each service owns its own tables from the schema above (grouped by the numbered sections in `schema.sql`), its own Alembic migration history, and its own Dockerfile/requirements. Cross-service calls happen only via HTTP through the `api-gateway` — never by importing another service's internals.

**Team ownership:**
| Person | Owns |
|---|---|
| Dev A | `hr-service` |
| Dev B | `attendance-timeoff-service` |
| Dev C | `payroll-service` (including the rule engine — hardest, most valuable piece) |
| Dev D | `api-gateway` + `frontend` |

## 6. Data model — key rules everyone must respect

1. **Never hardcode salary logic.** Every earning/deduction goes through the `salary_rule` engine, referenced by `code`, executed in `sequence` order via `salary_structure_rule`.
2. **A contract's validity is a date range, and only one ACTIVE contract per employee can exist for any given date.** This is enforced at the database level (`EXCLUDE USING gist`) — don't try to work around it in application code; if you hit that constraint, your data modeling assumption is wrong somewhere upstream.
3. **Payslip is not a payroll a bare join table — it's a rich entity.** It's how the Payrun↔Employee many-to-many relationship is realized, carrying status, amounts, and warnings.
4. **`payslip_line.salary_rule_code` is intentionally denormalized** (a text snapshot, not just a FK) — historical payslips must stay numerically and semantically accurate even if someone renames or deletes a Salary Rule later.
5. **Time Off Allocation and Time Off Request are separate entities** — entitlement vs. usage. A request always references which allocation it draws down.
6. **Every write to a sensitive entity (Contract, Payrun, Payslip, Time Off approval) should produce an `audit_log` row.** This is a judged criterion in the original problem statement ("all approvals, rejections, and edits must be logged").

Full schema: see `schema.sql`. Full relationship diagram: see `er_diagram.md`.

## 7. MVP scope (in priority order)

1. Employee CRUD + Department/Job Position + manager hierarchy
2. Contract (single active contract enforced) + Working Schedule with auto-computed weekly hours
3. Attendance check-in/check-out with worked-hours computation
4. Time Off Type + Allocation + Request → Approve/Refuse with automatic balance deduction
5. Salary Structure with 4–5 Salary Rules (Basic, one Allowance, one Deduction, Gross, Net) using FIXED/PERCENTAGE computation types (defer FORMULA type if time-constrained)
6. Payrun wizard (scope → employee selection) → Compute → Validate → Mark Paid
7. Payslip screen with rule breakdown
8. Payroll Dashboard with 2–3 live KPI cards

**Explicitly deferred unless time allows:** full contract history UI, PDF/email (can demo with on-screen preview), FORMULA-type salary rules, detailed attendance exception workflows, department-level analytics charts, AI features (see automation doc).

## 8. Git & workflow conventions

- Branch naming: `<service>/<short-description>` e.g. `payroll-service/rule-engine-sequencing`
- Never commit directly to `main` — PR + at least one review from `CODEOWNERS`
- Migrations: run `alembic revision --autogenerate` only within your own service; never hand-edit another service's migration files
- `shared/` folder changes require a ping to the other 3 devs before merging — it's the one place conflicts can cross service boundaries
- Run `pre-commit run --all-files` before every push

## 9. Glossary (so nobody has to ask twice)

| Term | Meaning |
|---|---|
| Salary Structure | A named bundle of Salary Rules (e.g. "Regular Salary") |
| Salary Rule | A single earning/deduction computation (e.g. "PF Deduction = 12% of Basic") |
| Payrun | A batch covering one period + one structure, containing many Payslips |
| Payslip | One employee's computed pay for one Payrun |
| Allocation | An employee's entitled leave balance for a given Time Off Type and validity period |
| Active contract | The one contract whose date range covers "today" (or the payroll period being processed) |
| Blended risk score | _(Not applicable to Pexo — this term belongs to the DealFlow360 alternative we didn't choose.)_ |
