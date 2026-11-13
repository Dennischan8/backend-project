# Project summary

- **Domain:** Hiking trails in Maryland
- **Core resource:** Trails on a user's personal to-hike list
- **Ownership:** Each trail belongs to a single user (one user -> many trails). The owner ID comes from the auth token, never the request body.
- **Primary actions:** Add a trail, update trail details, mark as high priority (via PATCH with `priority: true`)
- **User story:** Maryland hikers keep a clear to-hike list and see which trails are top priority, so they can quickly choose their next hike.

## Tech/project setup
- Flask app using an application factory: `create_app(config_name)` in `backend_project/__init__.py`
- Extensions (unbound `db = SQLAlchemy()`, `migrate = Migrate()`) live in `backend_project/extensions.py` and are bound inside the factory
- Config classes (Development/Testing/Production) and the `config_by_name` dict live in `backend_project/config.py`; the factory picks one with `app.config.from_object(config_by_name[config_name])`
- Settings come from `.env` (`DATABASE_URL`, `JWT_SECRET`); `.env` is gitignored, `.env.example` is committed
- Dev DB: SQLite at `instance/dev.db`
- Blueprints so far: `main_bp` in `backend_project/main.py` (no routes yet) and `health_bp` in `backend_project/health.py` (`GET /health`)
- Models file: not created yet (planned: `backend_project/models.py`, imported where the app loads so Flask-Migrate sees it)
- Auth and trails blueprints: not created yet (planned from the endpoint table)
- Migrations: Flask-Migrate is wired in; confirm whether `flask db init` has been run and `migrations/` is committed

## Git
- Unit 1 work is on `unit1-setup`, committed and pushed to `origin/unit1-setup`
- Unit 2 branch: not created yet (suggested: `feature/unit-2-auth`)