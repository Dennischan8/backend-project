# curl commands

Server: flask run --debug (venv active, FLASK_APP exported). Base URL: http://localhost:5000
Test users: hiker1@example.com / longenough (admin), hiker2@example.com / longenough2 (regular)
Tokens last one hour. If one expires, rerun the "Get tokens" commands.

## Public

Health check, expect 200:
curl -i http://localhost:5000/health

Register, expect 201 (400 invalid body, 409 duplicate email):
curl -i -X POST http://localhost:5000/auth/register -H "Content-Type: application/json" -d '{"email": "hiker3@example.com", "password": "longenough3"}'

Log in, expect 200 with access_token:
curl -i -X POST http://localhost:5000/auth/login -H "Content-Type: application/json" -d '{"email": "hiker1@example.com", "password": "longenough"}'

Wrong password, expect 401 invalid credentials:
curl -i -X POST http://localhost:5000/auth/login -H "Content-Type: application/json" -d '{"email": "hiker1@example.com", "password": "this-is-definitely-wrong-123"}'

## Get tokens (saves them in variables)

TOKEN_A=$(curl -s -X POST http://localhost:5000/auth/login -H "Content-Type: application/json" -d '{"email":"hiker1@example.com","password":"longenough"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

TOKEN_B=$(curl -s -X POST http://localhost:5000/auth/login -H "Content-Type: application/json" -d '{"email":"hiker2@example.com","password":"longenough2"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

## Profile (token required)

My profile, expect 200:
curl -i http://localhost:5000/auth/me -H "Authorization: Bearer $TOKEN_A"

No token, expect 401:
curl -i http://localhost:5000/auth/me

Bad token, expect 401:
curl -i http://localhost:5000/auth/me -H "Authorization: Bearer garbage"

Update my email, expect 200:
curl -i -X PATCH http://localhost:5000/auth/me -H "Authorization: Bearer $TOKEN_A" -H "Content-Type: application/json" -d '{"email": "hiker1-updated@example.com"}'

Restore my email afterward:
curl -i -X PATCH http://localhost:5000/auth/me -H "Authorization: Bearer $TOKEN_A" -H "Content-Type: application/json" -d '{"email": "hiker1@example.com"}'

Try to change role, expect 400 no updatable fields provided:
curl -i -X PATCH http://localhost:5000/auth/me -H "Authorization: Bearer $TOKEN_A" -H "Content-Type: application/json" -d '{"role": "admin"}'

## Trails (token required)

Add a trail, expect 201 (note the "id" in the response):
curl -i -X POST http://localhost:5000/trails -H "Authorization: Bearer $TOKEN_A" -H "Content-Type: application/json" -d '{"name": "Billy Goat Trail", "priority": true}'

List my trails, high priority first, expect 200:
curl -i http://localhost:5000/trails -H "Authorization: Bearer $TOKEN_A"

Get one trail (replace 1 with your trail id), expect 200:
curl -i http://localhost:5000/trails/1 -H "Authorization: Bearer $TOKEN_A"

Same trail as the other user, expect 404 (not yours):
curl -i http://localhost:5000/trails/1 -H "Authorization: Bearer $TOKEN_B"

No token, expect 401:
curl -i http://localhost:5000/trails/1

Update a trail, expect 200:
curl -i -X PATCH http://localhost:5000/trails/1 -H "Authorization: Bearer