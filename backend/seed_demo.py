"""Create fixed demo users for local development. Safe to re-run."""
from datetime import datetime, timedelta

from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.models import (
    Consent,
    ConversationEvent,
    Mission,
    ProactivePreference,
    Tenant,
    User,
)
from app.security import hash_password

DEMO_PASSWORD = "RiseDemo2026!"
TENANT_NAME = "RISE Demo School"

USERS = [
    {
        "email": "admin@rise.dev",
        "display_name": "Demo Admin",
        "role": "organization_admin",
    },
    {
        "email": "researcher@rise.dev",
        "display_name": "Demo Researcher",
        "role": "researcher",
    },
    {
        "email": "youth@rise.dev",
        "display_name": "Alex",
        "role": "youth",
        "onboarding_status": "complete",
        "onboarding_data": {
            "preferred_name": "Alex",
            "energy_areas": ["learning", "creative"],
            "current_difficulties": ["focus"],
            "challenge_intensity": "normal",
            "proactive_consent": True,
            "research_consent": True,
            "service_terms": True,
            "youth_assent": True,
        },
    },
]


def upsert_user(db, tenant_id: str, spec: dict) -> User:
    email = spec["email"].lower()
    user = db.scalar(select(User).where(User.tenant_id == tenant_id, User.email == email))
    if not user:
        user = User(
            tenant_id=tenant_id,
            email=email,
            display_name=spec["display_name"],
            password_hash=hash_password(DEMO_PASSWORD),
            role=spec["role"],
        )
        db.add(user)
        db.flush()
        print(f"  + created {email} ({spec['role']})")
    else:
        user.display_name = spec["display_name"]
        user.password_hash = hash_password(DEMO_PASSWORD)
        user.role = spec["role"]
        user.is_active = True
        print(f"  ~ updated {email} ({spec['role']})")

    if spec.get("onboarding_status"):
        user.onboarding_status = spec["onboarding_status"]
    if spec.get("onboarding_data"):
        user.onboarding_data = spec["onboarding_data"]

    return user


def ensure_consents(db, tenant_id: str, user: User) -> None:
    for kind in ("service", "research", "proactive_messages"):
        row = db.scalar(
            select(Consent).where(Consent.user_id == user.id, Consent.kind == kind)
        )
        if not row:
            db.add(
                Consent(
                    tenant_id=tenant_id,
                    user_id=user.id,
                    kind=kind,
                    granted=True,
                    granted_by=user.id,
                )
            )


def ensure_youth_extras(db, tenant_id: str, user: User) -> None:
    pref = db.get(ProactivePreference, user.id)
    if not pref:
        db.add(
            ProactivePreference(
                user_id=user.id,
                tenant_id=tenant_id,
                cadence="normal",
                allowed_hours=["09:00-21:00"],
                paused=False,
            )
        )

    mission = db.scalar(
        select(Mission).where(Mission.user_id == user.id, Mission.title == "Talk to one new person")
    )
    if not mission:
        db.add(
            Mission(
                tenant_id=tenant_id,
                user_id=user.id,
                title="Talk to one new person",
                mission_type="social",
                hypothesis="Starting small conversations builds confidence.",
                action="Say hello to someone you do not usually talk to and ask one genuine question.",
                proof="Write one sentence about what you noticed.",
                status="active",
                due_at=datetime.utcnow() + timedelta(days=3),
            )
        )

    event = db.scalar(
        select(ConversationEvent).where(
            ConversationEvent.user_id == user.id,
            ConversationEvent.user_message == "I want to get better at talking to people.",
        )
    )
    if not event:
        db.add(
            ConversationEvent(
                tenant_id=tenant_id,
                user_id=user.id,
                pseudonym="demo-youth-01",
                risk_level="none",
                topic="social",
                user_message="I want to get better at talking to people.",
                assistant_message="Good. What is one low-stakes conversation you could try today?",
            )
        )


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        tenant = db.scalar(select(Tenant).where(Tenant.name == TENANT_NAME))
        if not tenant:
            tenant = Tenant(name=TENANT_NAME)
            db.add(tenant)
            db.flush()
            print(f"Created tenant: {TENANT_NAME}")
        else:
            print(f"Using tenant: {TENANT_NAME}")

        created_users = []
        for spec in USERS:
            user = upsert_user(db, tenant.id, spec)
            ensure_consents(db, tenant.id, user)
            if user.role == "youth":
                ensure_youth_extras(db, tenant.id, user)
            created_users.append(user)

        db.commit()
        print("\nDemo accounts ready:\n")
        print(f"  Password (all accounts): {DEMO_PASSWORD}\n")
        for spec in USERS:
            area = "App + Admin" if spec["role"] != "youth" else "App only"
            print(f"  {spec['email']:<22} {spec['role']:<22} {area}")
        print("\nURLs:")
        print("  App:   http://localhost:4173")
        print("  Admin: http://localhost:4173/admin/")
    finally:
        db.close()


if __name__ == "__main__":
    main()
