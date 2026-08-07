# RISE V1 — Mobile PWA

**Claim:** Rise above the noise. Build your direction.

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

- **PWA:** http://localhost:4173
- **API docs:** http://localhost:8000/docs
- **Admin:** http://localhost:4173/admin/

## What's included

- Mobile-first PWA with World · Kai · Journey · Progress · Me navigation
- Living world home screen with 6 development districts
- Kai conversation with response chips and real-world action cards
- Mission flow (accept → complete → growth feedback)
- Journey (missions & objectives), Progress (evidence), Profile
- Auth, onboarding, multi-tenant backend
- Admin & research console at `/admin/`

## Demo accounts

Run once (with Docker API + Postgres up):

```bash
cd v1/backend
pip install -r requirements.txt
python seed_demo.py
```

| Email | Password | Role | Access |
|-------|----------|------|--------|
| `youth@rise.dev` | `RiseDemo2026!` | Youth | Main app |
| `admin@rise.dev` | `RiseDemo2026!` | Organization admin | App + admin console |
| `researcher@rise.dev` | `RiseDemo2026!` | Researcher | App + admin + research view |
