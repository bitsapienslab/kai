# RISE V1

Functional snapshot of the RISE product before Liquid Focus.

**Claim:** Rise above the noise. Build your direction.

## Included

- Responsive installable PWA dashboard.
- Login, registration, refresh token and logout.
- Youth onboarding.
- Today dashboard with check-in, objectives and recent conversations.
- Objectives area.
- Private journal.
- Kai conversation.
- User administration and invitations.
- Authorized Research Console.
- Consent and audit records.
- Basic operational analytics.
- Individual commitment notifications.
- FastAPI backend with PostgreSQL and pgvector.

## Run locally

```bash
cd v1
python3 -m http.server 4173
```

In another terminal:

```bash
cd v1
docker compose up
```

- PWA: `http://localhost:4173`
- API docs: `http://localhost:8000/docs`

The root application is RISE V2 Liquid Focus. This folder keeps the RISE V1 dashboard experience with its original visible sections.
