# Pexo

Pexo is an enterprise-grade HR, Attendance, and Payroll Management System built with a modular microservice architecture and a modern React frontend.

## Architecture Overview

```
                        +----------------------+
                        |   Nginx / Gateway    |
                        |   (Reverse Proxy)    |
                        +----------+-----------+
                                   |
                  +----------------+----------------+
                  |                                 |
                  v                                 v
        +-------------------+             +-------------------+
        | React Frontend    |             | API Gateway       |
        | (Vite + Tailwind) |             | (FastAPI + Auth)  |
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
                      +---------------+---------------+
                      |                               |
                      v                               v
             +------------------+            +------------------+
             | PostgreSQL DB    |            | Redis & Azurite  |
             | (Multi-Schema)   |            | (Cache & Storage)|
             +------------------+            +------------------+
```

## Services Summary

| Service | Port | Description |
|---|---|---|
| **api-gateway** | `8000` | Auth (JWT/RBAC), Service Proxying, Dashboard Aggregation |
| **hr-service** | `8001` | Employee master, departments, contracts, working schedules |
| **attendance-timeoff-service** | `8002` | Clock-in/out attendance, leave requests, leave allocations |
| **payroll-service** | `8003` | Salary structures, salary rule engine, payrun wizard, payslips |
| **frontend** | `5173` | React 18, Vite, TailwindCSS, Redux Toolkit, TanStack Query |
| **PostgreSQL** | `5432` | Schemas: `hr`, `attendance_timeoff`, `payroll`, `gateway` |
| **Redis** | `6379` | Celery broker, result backend, dashboard metrics caching |
| **Azurite** | `10000` | Local Azure Blob Storage emulator for payslip PDF archives |

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Quick Start with Docker Compose
```bash
# 1. Clone the repository and copy environment variables
cp .env.example .env

# 2. Start all services, databases, cache, and frontend
docker-compose -f infra/docker-compose.yml up --build
```

Access:
- Frontend Web App: `http://localhost:5173` (or `http://localhost` via Nginx)
- API Gateway Swagger: `http://localhost:8000/docs`
- HR Service Swagger: `http://localhost:8001/docs`
- Attendance Service Swagger: `http://localhost:8002/docs`
- Payroll Service Swagger: `http://localhost:8003/docs`
