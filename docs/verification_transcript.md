# Verification transcript

Verified with curl against flask run --debug on Nov 26, 2026.

## Ownership (hiker2 owns trail 13, hiker5 is another user)
hiker5 GET /trails/13    -> 404 {"error": "not_found", "message": "trail not found"}
hiker5 PATCH /trails/13  -> 404
hiker5 DELETE /trails/13 -> 404
hiker2 GET /trails/13    -> 200, unchanged

## Auth failures
GET /trails/13, no token  -> 401 missing or invalid token
GET /trails/13, bad token -> 401 missing or invalid token

## Admin
hiker2 GET /admin/ping -> 403 admin access required
hiker1 GET /admin/ping -> 200

## Pagination
GET /trails?page=1&per_page=2 -> 200, 2 items
GET /trails?page=2&per_page=2 -> 200
GET /trails?per_page=999 -> 400 bad_request