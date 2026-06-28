# Deployment Guide

## Local Development

- Use `npm run dashboard:start` to build the SPA and start the FastAPI backend that serves it.
- App: <http://127.0.0.1:8095/app>

## Production

- Set all secrets and environment variables in your deployment environment as needed.
- Use HTTPS and a reverse proxy such as Nginx or Caddy.
- Use `docker-compose -f docker-compose.yml up --build -d` for deployment.

## CI/CD

- See `.github/workflows/` for build, test, and deploy pipelines.

## Cloud/Container

- Compatible with most container platforms, including Azure, AWS, GCP, and DigitalOcean.
- For Kubernetes, adapt `docker-compose.yml` to manifests or use Kompose.

## References

- `ARCHITECTURE.md`
- `ONBOARDING.md`
- `SECURITY_HEADERS.md`
