Quick Reference Table
Directive Meaning Use Case
no-store Never store anywhere Sensitive data (tokens, personal info)
no-cache Store but revalidate every time Dynamic data that changes often
private Only browser can cache, not CDN User-specific data
public CDN and browser can cache Shared data (questionnaire)
max-age=N Cache for N seconds Control freshness
s-maxage=N CDN cache time (overrides max-age for CDN) Different CDN vs browser TTL
must-revalidate Must check origin when stale Ensure freshness
immutable Never changes, cache forever Versioned assets
Common Patterns for Your API

# 1. NEVER CACHE - Sensitive/Personal Data

# Use for: /api/v1/users/me, /api/v1/auth/\*, tokens, personal stats

response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"

# 2. SHORT CACHE - Frequently changing shared data

# Use for: /health, /api/v1/leaderboard

response.headers["Cache-Control"] = "public, max-age=10" # 10 seconds

# 3. MEDIUM CACHE - Semi-static shared data

# Use for: /api/v1/questionnaire, /api/v1/config

response.headers["Cache-Control"] = "public, max-age=300" # 5 minutes

# 4. LONG CACHE - Rarely changing data

# Use for: /api/v1/static-content, terms of service

response.headers["Cache-Control"] = "public, max-age=86400" # 24 hours

# 5. USER-SPECIFIC but cacheable in browser only

# Use for: User preferences that don't change often

response.headers["Cache-Control"] = "private, max-age=60" # Browser only, 1 min

# 6. CDN vs Browser different TTLs

# CDN caches 5 min, browser caches 1 min

response.headers["Cache-Control"] = "public, max-age=60, s-maxage=300"
