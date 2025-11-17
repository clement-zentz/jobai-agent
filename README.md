<!-- README.md -->

# 🤖 JobAI Agent

An AI agent that helps you find and filter job opportunities.

Due to Terms of Service restrictions and bot-detection policies on major job platforms, this project currently focuses on data collection, parsing, and intelligent filtering of job offers.

A fully automated application flow may be added in the future, but a semi-automated application process is sufficient for now and avoids violating platform rules.

## 🐘 Database Configuration (PostgreSQL)

The project is configured to use PostgreSQL via Docker for local development. A postgres service is defined in `docker-compose.yml` and persisted with a named volume.

### 🔧 Environment Variables

Set these in your `.env` file (they are consumed by both the app and the postgres container):

```ini
POSTGRES_USER=jobai
POSTGRES_PASSWORD=jobai_password
POSTGRES_DB=jobai
DATABASE_URL=postgresql+asyncpg://jobai:jobai_password@postgres:5432/jobai
```

Notes:
- `postgres` in the URL is the Docker service name, enabling internal DNS resolution.
- The `postgresql+asyncpg` driver enables async usage with SQLModel / FastAPI.

### 🚀 Running Locally

Build and start the stack:

```bash
docker compose up --build --watch
```

The API will be available at http://localhost:8000 and PostgreSQL at localhost:5432.

### 📂 Data Persistence

The Postgres data files are stored in the named volume `pg_data` defined in `docker-compose.yml`.

### 🛠️ Schema Initialization

Tables are created automatically on application startup (SQLModel metadata create). No manual migration step is required yet. Introduce Alembic later when evolving schemas.

## 📜 License
This project is licensed under the GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later).  
See the [LICENSE](./LICENSE) file for details.

