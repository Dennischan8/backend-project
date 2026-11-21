# curl commands

Server: `flask run --debug` (venv active, `FLASK_APP` exported). Base URL: `http://localhost:5000`.
Test users: `hiker1@example.com` / `longenough` (admin), `hiker2@example.com` / `longenough2` (regular).

## Public

Health check, expect 200:
```bash
curl -i http://localhost:5000/health
```

Register a user, expect 201 (400 invalid body, 409 duplicate email):
```bash
curl -i -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "hiker3@example.com", "password": "longenough3"}'
```

Log in, expect 200 with `access_token`:
```bash
curl -i -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "hiker1@example.com", "password": "longenough"}'
```

Log in with a wrong password, expect 401 `invalid credentials`:
```bash
curl -i -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "hiker1@example.com", "password": "this-is-definitely-wrong-123"}'
```

## Get tokens (saves them in variables)

```bash
TOKEN_A=$(curl -s -X POST http://localhost:5000/auth/login -H "Content-Type: application/json" -d '{"email":"hiker1@example.com","password":"longenough"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
TOKEN_B=$(curl -s -X POST http://localhost:5000/auth/login -H "Content-Type: application/json" -d '{"email":"hiker2@example.com","password":"longenough2"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

## Profile (token required)

Get my profile, expect 200:
```bash
curl -i http://localhost:5000/auth/me -H "Authorization: Bearer $TOKEN_A"
```

No token, expect 401:
```bash
curl -i http://localhost:5000/auth/me
```

Bad token, expect 401:
```bash
curl -i http://localhost:5000/auth/me -H "Authorization: Bearer garbage"
```

Update my email, expect 200:
```bash
curl -i -X PATCH http://localhost:5000/auth/me \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"email": "hiker1-updated@example.com"}'
```

Try to change role, expect 400 `no updatable fields provided`:
```bash
curl -i -X PATCH http://localhost:5000/auth/me \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}'
```

## Trails (token required)

Add a trail, expect 201:
```bash
curl -i -X POST http://localhost:5000/trails \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"name": "Billy Goat Trail", "priority": true}'
```

List my trails (high priority first), expect 200:
```bash
curl -i http://localhost:5000/trails -H "Authorization: Bearer $TOKEN_A"
```

## Admin only

Non-admin, expect 403:
```bash
curl -i http://localhost:5000/admin/ping -H "Authorization: Bearer $TOKEN_B"
```

Admin, expect 200:
```bash
curl -i http://localhost:5000/admin/ping -H "Authorization: Bearer $TOKEN_A"
```