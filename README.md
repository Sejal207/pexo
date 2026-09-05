# Pexo

Pexo is an enterprise-grade HR, Attendance, and Payroll Management System built with a modular microservice architecture and a modern React frontend.

## Architecture Overview

```
        +-------------------+             +-------------------+
        | React Frontend    |             | API Gateway       |
        | (Vite + Tailwind) |  --------->  | (FastAPI + Auth)  |
        +-------------------+             +--------+----------+
                                                   |
             +--------------------+----------------+--------------------+
             |                    |                                     |
             v                    v                                     v
   +-------------------+  +-----------------------+           +-------------------+
   | HR Service        |  | Attendance & Time-Off |           | Payroll Service   |
   | (FastAPI)         |  | Service (FastAPI)     |           | (FastAPI+Celery)  |
   +---------+---------+  +-----------+-----------+           +---------+---------+
             |                        |                                 |
             +------------------------+---------------------------------+
                                      |
                                      v
                            +------------------+
                            | Neon PostgreSQL  |
                            | (schema.sql)     |
                            +------------------+
```

Every service runs directly with `uvicorn` — no Docker. They all point at the
same Neon Postgres database (one flat schema, defined by `schema.sql` at the
repo root), so there's nothing to containerize locally for the database either.

## Services Summary

| Service | Port | Description |
|---|---|---|
| **api-gateway** | `8000` | Auth (JWT/RBAC), Service Proxying, Dashboard Aggregation |
| **hr-service** | `8001` | Employee master, departments, contracts, working schedules |
| **attendance-timeoff-service** | `8002` | Clock-in/out attendance, leave requests, leave allocations |
| **payroll-service** | `8003` | Salary structures, salary rule engine, payrun wizard, payslips |
| **frontend** | `5173` | React 18, Vite, TailwindCSS, Redux Toolkit, TanStack Query |
| **Neon PostgreSQL** | — | One flat database/schema, shared by every service — see `schema.sql` |
| **Redis** _(optional)_ | `6379` | Only needed for payroll-service's Celery workers and dashboard KPI caching — not required for auth or the core CRUD flows |
| **Azurite** _(optional)_ | `10000` | Local Azure Blob Storage emulator for payslip PDF archives — only needed once payslip PDF generation is wired up |

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- A Neon Postgres database (or any Postgres 15+) with `schema.sql` and `refresh_token.sql` applied, optionally seeded with `seed_dummy_data.sql`

### Database setup
Run these once against your Neon database (e.g. via the Neon SQL editor, or `psql "$DATABASE_URL" -f <file>`), in order:
```bash
psql "$DATABASE_URL" -f schema.sql
psql "$DATABASE_URL" -f refresh_token.sql
psql "$DATABASE_URL" -f seed_dummy_data.sql   # optional: sample employees, users, roles
```

### Running a service locally
Each service has its own `.env.example` — copy it to `.env` in that service's
directory and fill in your real `DATABASE_URL` (never commit the real one):
```bash
cd services/api-gateway
cp .env.example .env   # edit DATABASE_URL, etc.
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Repeat for `hr-service` (port 8001), `attendance-timeoff-service` (port 8002),
and `payroll-service` (port 8003).

### Running the frontend
```bash
cd frontend
npm install
npm run dev
```

Access:
- Frontend Web App: `http://localhost:5173`
- API Gateway Swagger: `http://localhost:8000/docs`
- HR Service Swagger: `http://localhost:8001/docs`
- Attendance Service Swagger: `http://localhost:8002/docs`
- Payroll Service Swagger: `http://localhost:8003/docs`

### Seeded login credentials
If you ran `seed_dummy_data.sql`, these accounts are available (password `Password@123` for all):

| Email | Role |
|---|---|
| admin@Pexo.com | ADMIN |
| alice.hr@Pexo.com | HR_MANAGER |
| bob.payroll@Pexo.com | HR_PAYROLL_MANAGER |
| charlie.lead@Pexo.com | EMPLOYEE |
| david.dev@Pexo.com | EMPLOYEE |
| eva.qa@Pexo.com | EMPLOYEE |
