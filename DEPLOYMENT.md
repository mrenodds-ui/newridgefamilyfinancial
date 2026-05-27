# Deployment Guide
## Local Development
- Use `docker-compose up` to start the frontend SPA
- SPA: http://localhost:5173
## Production
- Set all secrets and environment variables in your deployment environment (if needed)
- Use HTTPS and a reverse proxy (e.g., Nginx, Caddy)
- Use `docker-compose -f docker-compose.yml up --build -d` for SPA deployment
## CI/CD
- See `.github/workflows/` for build, test, and deploy pipelines
## Cloud/Container
- Compatible with most container platforms (Azure, AWS, GCP, DigitalOcean)
- For Kubernetes, adapt `docker-compose.yml` to manifests or use Kompose for SPA only
# Deployment Guide

## Local Development
- Use `docker-compose up` to start the frontend SPA only
- Frontend: http://localhost:5173

## Production
- Set all secrets and environment variables in your deployment environment (if needed)
- Use HTTPS and a reverse proxy (e.g., Nginx, Caddy)
- Use `docker-compose -f docker-compose.yml up --build -d` for deployment

## CI/CD
- See `.github/workflows/` for build, test, and deploy pipelines

## Cloud/Container
- Compatible with most container platforms (Azure, AWS, GCP, DigitalOcean)
- For Kubernetes, adapt `docker-compose.yml` to manifests or use Kompose

## References
- See `ARCHITECTURE.md`, `ONBOARDING.md`, `SECURITY_HEADERS.md` for more
