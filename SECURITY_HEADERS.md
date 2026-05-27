# Security Headers

## Enforced Headers
- **Strict-Transport-Security**: max-age=63072000; includeSubDomains; preload
- **Content-Security-Policy**: default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'
- **X-Content-Type-Options**: nosniff
- **X-Frame-Options**: DENY
- **Referrer-Policy**: strict-origin-when-cross-origin
- **Permissions-Policy**: geolocation=(), microphone=(), camera=()

## Implementation
- Set in FastAPI middleware (see `app/main.py`)
- Set in Node backend (see `dashboard-backend/src/`)
- Enforced in production only

## References
- [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [MDN Web Docs: Security Headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers)
