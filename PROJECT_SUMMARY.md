# Project summary

- **Domain:** Hiking trails in Maryland
- **Core resource:** Trails on a user's personal to-hike list
- **Ownership:** Each trail belongs to a single user (one user -> many trails). The owner ID comes from the auth token (`g.current_user.id`), never the request body.
- **Primary actions:** Add a trail, update trail details, mark as high priority (via PATCH with `priority: true`)
- **User story:** Maryland hikers keep a clear to-hike list and see which trails are top priority, so they can quickly choose their next hike.

## Tech/project setup
- Flask app using an application factory: `create_app(config_name)` in `backend_project/__init__.py`
- Extensions (unbound `db = SQLAlchemy()`, `migrate = Migrate()`) live in `backend_project/extensions.py` and are bound inside the factory
- Config classes (Development/Testing/Production) and the `config_by_name` dict live in `backend_project/config.py`; the factory picks one with `app.config.from_object(config_by_name[config_name])`
- Settings come from `.env` (`DATABASE_URL`, `JWT_SECRET`, optional `JWT_LIFETIME_SECONDS`, default 3600); `.env` is gitignored, `.env.example` is committed
- Dev DB: SQLite at `instance/dev.db`
- Run: `export FLASK_APP='backend_project:create_app("development")'` then `flask run --debug`

## Models (`backend_project/models.py`)
- `User`: `id`, `email` (unique, indexed), `password_hash`, `role` (String(20), default "user"), `created_at`, plus `set_password()` and `check_password()`
- `Trail`: `id`, `owner_id` (FK to `users.id`), `name`, `location`, `distance_miles`, `difficulty`, `notes`, `priority`, `created_at`
- Relationship: one user has many trails (`user.trails`, `trail.owner`)

## Migrations
- `a94178aec5c4` creates `users`, `854d2a20484a` adds `role`, `327b7f6d8c53` creates `trails`. All applied to `instance/dev.db`.

## Auth
- Register: validates input, lowercases the email, 409 on duplicate, stores a scrypt hash, returns 201.
- Login: generic 401 `{"error": "invalid credentials"}` for a missing user or wrong password. Success returns an HS256 JWT with `sub` (`str(user.id)`), `role`, and `exp`. Secret and lifetime are read from app config.
- `@token_required` (`auth_utils.py`): reads `Authorization: Bearer <token>`, verifies it, loads the user from the database, sets `g.current_user`. Expired token gives 401 "token has expired"; any other bad token gives 401 "missing or invalid token".
- `@admin_required` (`auth_utils.py`): runs after `token_required`, checks `g.current_user.role` from the database, returns 403 "admin access required" if not admin.
- Roles: `user` (default) and `admin`. The API never writes `role`; admins are promoted directly in the database.
- No server-side session or revocation state, so logout is just the client discarding its token. Expiry limits how long a stolen token is usable.
- All errors use `{"error": "<code>", "message": "..."}` (login's generic 401 is the one exception, with no `message`).
- `GET /auth/me`:
  - Missing or bad token → `401` with `{"error": "unauthorized", "message": "missing or invalid token"}`
  - Valid token → `200` with user JSON (`id`, `email`, `role`, `created_at`)
- `GET /admin/ping`:
  - Valid non-admin user token → `403` with `{"error": "forbidden", "message": "admin access required"}`

## Routes and files (all in `backend_project/`)
- `auth.py` (`auth_bp`, `/auth`): `POST /register`, `POST /login`, `GET /me`, `PATCH /me` (allowlist: only `email`)
- `trails.py` (`trails_bp`, `/trails`): `POST /trails`, `GET /trails` (high priority first), both `@token_required`
- `admin.py` (`admin_bp`, `/admin`): `GET /admin/ping` (`@token_required` then `@admin_required`)
- `health.py` (`health_bp`): `GET /health` (public)
- `main.py` (`main_bp`): no routes
- `auth_utils.py`: `error_response`, `token_required`, `admin_required`

## Git
- Unit 1 work: `unit1-setup`, pushed
- Unit 2 branch: `feature/unit-2-auth`, pushed to `origin/feature/unit-2-auth`; working tree clean as of the admin route commit

## Next / pending
- Next: `GET`, `PATCH`, `DELETE /trails/<id>`, filtered by trail ID and `g.current_user.id` so another user's trail returns 404
- Pending: length caps (email 255, password 128); `register()` could use `user.set_password()`