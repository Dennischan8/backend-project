# Backend Project

Simple backend API built with Flask for learning production-style workflows.

## Tech stack

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- SQLite (dev)

## Setup (dev)

These steps are for macOS. Run them from the project root.

```bash
# 1. Create a virtual environment
python3 -m venv .venv

# 2. Activate it
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your environment file (see "Environment variables" below)
cp .env.example .env

# 5. Run the app
flask --app 'backend_project:create_app("development")' run --debug
```

The app runs at http://127.0.0.1:5000.

## Environment variables

The app reads its settings from a `.env` file in the project root. This file holds secrets and is not committed to git.

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Database connection URL used by the app |
| `JWT_SECRET` | Secret key used to sign login tokens |

To set up your own copy, run `cp .env.example .env`, then open `.env` and replace the placeholder values with real ones. The app won't start if `JWT_SECRET` is missing or empty.