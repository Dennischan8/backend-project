# curl commands

Server: flask run --debug (venv active, FLASK_APP exported). Base URL: http://localhost:5000
Test users: hiker1@example.com / longenough (admin), hiker2@example.com / longenough2 (regular)
Tokens last one hour. If one expires, rerun the "Get tokens" commands.
Put quotes around any URL that contains ? or & (zsh treats them as special characters).

## Start the server

source .venv/bin/activate
export FLASK_APP='backend_project:create_app("development")'
flask run --debug

Ready when you see "Running on http://127.0.0.1:5000". Leave that terminal open and run the curl commands in a second terminal.
If port 5000 is taken (AirPlay Receiver on macOS), use: flask run --debug --port 5001 and change 5000 to 5001 in the URLs.


## Public

Health check, expect 200:
curl -i http://localhost:5000/health

Register, expect 201 (400 invalid body, 409 duplicate email):
curl -i -X POST http://localhost:5000/auth/register -H "Content-Type: application/json" -d '{"email": "hiker6@example.com", "password": "longenough6"}'

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

List my trails, expect 200 with an object: items, page, per_page, total, pages (defaults: page=1, per_page=10, ordered by id):
curl -i http://localhost:5000/trails -H "Authorization: Bearer $TOKEN_A"

Page 1 with 10 per page, expect 200:
curl -i "http://localhost:5000/trails?page=1&per_page=10" -H "Authorization: Bearer $TOKEN_A"

Small pages to see paging with little data, expect 200:
curl -i "http://localhost:5000/trails?page=2&per_page=2" -H "Authorization: Bearer $TOKEN_A"

Past the end, expect 200 with "items": [] (pages shows the real last page):
curl -i "http://localhost:5000/trails?page=99&per_page=10" -H "Authorization: Bearer $TOKEN_A"

per_page too big, expect 400 bad_request "per_page must be at most 50":
curl -i "http://localhost:5000/trails?per_page=999" -H "Authorization: Bearer $TOKEN_A"

page not a number, expect 400 bad_request "page must be an integer":
curl -i "http://localhost:5000/trails?page=abc" -H "Authorization: Bearer $TOKEN_A"

page below 1, expect 400 bad_request "page must be at least 1":
curl -i "http://localhost:5000/trails?page=0" -H "Authorization: Bearer $TOKEN_A"

List with no token, expect 401:
curl -i http://localhost:5000/trails

Get one trail (replace 1 with your trail id), expect 200:
curl -i http://localhost:5000/trails/1 -H "Authorization: Bearer $TOKEN_A"

Same trail as the other user, expect 404 (not yours):
curl -i http://localhost:5000/trails/1 -H "Authorization: Bearer $TOKEN_B"

No token, expect 401:
curl -i http://localhost:5000/trails/1

Update a trail, expect 200:
curl -i -X PATCH http://localhost:5000/trails/1 -H "Authorization: Bearer $TOKEN_A" -H "Content-Type: application/json" -d '{"notes": "Go early to beat the crowds", "difficulty": "moderate"}'

Mark a trail high priority, expect 200:
curl -i -X PATCH http://localhost:5000/trails/1 -H "Authorization: Bearer $TOKEN_A" -H "Content-Type: application/json" -d '{"priority": true}'

Other user tries to update, expect 404:
curl -i -X PATCH http://localhost:5000/trails/1 -H "Authorization: Bearer $TOKEN_B" -H "Content-Type: application/json" -d '{"priority": false}'

Invalid value, expect 400:
curl -i -X PATCH http://localhost:5000/trails/1 -H "Authorization: Bearer $TOKEN_A" -H "Content-Type: application/json" -d '{"difficulty": "impossible"}'

Other user tries to delete, expect 404:
curl -i -X DELETE http://localhost:5000/trails/1 -H "Authorization: Bearer $TOKEN_B"

Delete my trail, expect 204 with no body:
curl -i -X DELETE http://localhost:5000/trails/1 -H "Authorization: Bearer $TOKEN_A"

Get it again after deleting, expect 404:
curl -i http://localhost:5000/trails/1 -H "Authorization: Bearer $TOKEN_A"

## Admin only

Regular user, expect 403:
curl -i http://localhost:5000/admin/ping -H "Authorization: Bearer $TOKEN_B"

Admin, expect 200:
curl -i http://localhost:5000/admin/ping -H "Authorization: Bearer $TOKEN_A"