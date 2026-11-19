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
- Settings come from `.env` (`DATABASE_URL`, `JWT_SECRET`, optional `JWT_LIFETIME_SECONDS`); `.env` is gitignored, `.env.example` is committed
- Dev DB: SQLite at `instance/dev.db`
- Blueprints: `main_bp` in `main.py` (no routes), `health_bp` in `health.py` (`GET /health`), `auth_bp` in `auth.py` (`url_prefix /auth`: `POST /auth/register`, `POST /auth/login`). All registered in the factory.
- Models file: `backend_project/models.py` with `User` (`id`, `email` unique and indexed, `password_hash`, `role` String(20) default "user", `created_at`) plus `set_password()` and `check_password()`; imported inside the factory after `db.init_app(app)` so Flask-Migrate sees it. `Trail` model not created yet.
- Migrations: `migrations/` is committed. `a94178aec5c4` creates `users`, `854d2a20484a` adds `role`. Both applied to `instance/dev.db`.

## Auth
- Register: validates JSON, email, and password; lowercases the email; returns 409 on duplicate; stores a scrypt hash; returns 201 with `id`, `email`, `created_at`.
- Login: looks up the user by lowercased email; a missing user or wrong password both return the same generic 401 `{"error": "invalid credentials"}`; success returns 200 `{"access_token": ...}`.
- JWT: `/auth/login` issues an HS256 token with payload `sub` (`str(user.id)`), `role`, and `exp`. The secret (`JWT_SECRET`) and lifetime (`JWT_LIFETIME_SECONDS`, default 3600) are read from app config via `current_app.config`, not hardcoded.
- All validation errors use `{"error": "validation_error", "message": "..."}`.

## Git
- Unit 1 work is on `unit1-setup`, committed and pushed to `origin/unit1-setup`
- Unit 2 branch: `feature/unit-2-auth`, pushed to `origin/feature/unit-2-auth`

## Next / pending
- Next: decorator that reads `Authorization: Bearer <token>`, verifies it, and loads the current user; then `GET /auth/me` and the trails routes
- Pending: length caps (email 255, password 128); `register()` could use `user.set_password()`