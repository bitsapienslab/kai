"""Create fixed demo users for local development. Safe to re-run."""
from datetime import datetime, timedelta

from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.models import (
    Consent,
    ConversationEvent,
    Evidence,
    Mission,
    Objective,
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

    # ── Missions (3 with varied statuses) ─────────────────────────────────────

    MISSIONS = [
        {
            "title": "Talk to one new person",
            "mission_type": "social",
            "hypothesis": "Starting small conversations builds confidence.",
            "action": "Say hello to someone you do not usually talk to and ask one genuine question.",
            "proof": "Write one sentence about what you noticed.",
            "status": "active",
            "due_at": datetime.utcnow() + timedelta(days=3),
            "learning": "",
        },
        {
            "title": "Read for 20 minutes every day this week",
            "mission_type": "learning",
            "hypothesis": "Consistent daily reading builds focus and curiosity.",
            "action": "Choose a book or article on any topic you are curious about and read for 20 minutes without interruptions.",
            "proof": "After each session, write one thing you learned or noticed.",
            "status": "completed",
            "due_at": datetime.utcnow() - timedelta(days=5),
            "learning": "I discovered I actually enjoy reading when I pick the topic myself instead of being assigned it.",
        },
        {
            "title": "Create something with your hands",
            "mission_type": "creative",
            "hypothesis": "Making something physical builds creative confidence and reduces screen-time anxiety.",
            "action": "Spend 30 minutes making or building anything — drawing, cooking, assembling, writing by hand. No screens.",
            "proof": "Take a photo of what you made or write two sentences describing it.",
            "status": "active",
            "due_at": datetime.utcnow() + timedelta(days=7),
            "learning": "",
        },
    ]

    for spec in MISSIONS:
        exists = db.scalar(
            select(Mission).where(Mission.user_id == user.id, Mission.title == spec["title"])
        )
        if not exists:
            db.add(Mission(tenant_id=tenant_id, user_id=user.id, **spec))

    # ── Objectives / Commitments ───────────────────────────────────────────────

    OBJECTIVES = [
        {
            "title": "Improve my focus during study sessions",
            "action": "Put my phone in another room and study for 25 minutes using a timer, then take a 5-minute break.",
            "why": "I keep getting distracted and then feel bad about not finishing work I actually care about.",
            "proof": "Record how many Pomodoro sessions I complete each day for two weeks.",
            "anticipated_difficulty": "The first 5 minutes are hardest — the urge to check my phone is strong.",
            "fallback_plan": "If I slip, I restart the timer instead of giving up on the whole session.",
            "status": "active",
            "progress": 40,
            "due_at": datetime.utcnow() + timedelta(days=14),
        },
        {
            "title": "Have one honest conversation with a friend about something that matters",
            "action": "Choose a friend I trust and bring up something real — not just small talk — and listen to their response without immediately solving it.",
            "why": "I want my friendships to feel deeper, not just surface-level.",
            "proof": "Write three sentences about how the conversation went and how I felt.",
            "anticipated_difficulty": "Vulnerability feels risky — I might say the wrong thing.",
            "fallback_plan": "Start by sharing something small and see how they respond before going deeper.",
            "status": "completed",
            "progress": 100,
            "due_at": datetime.utcnow() - timedelta(days=2),
        },
    ]

    for spec in OBJECTIVES:
        exists = db.scalar(
            select(Objective).where(Objective.user_id == user.id, Objective.title == spec["title"])
        )
        if not exists:
            db.add(Objective(tenant_id=tenant_id, user_id=user.id, **spec))

    # ── Evidence / Learnings (powers Progress tab and World district map) ──────
    # Competency keywords must match district keywords in main.py:
    #   social, learning, health, creative, projects, self_knowledge → self

    EVIDENCE = [
        {
            "competency": "social",
            "statement": "I said hello to a classmate I usually ignore. We ended up talking for 10 minutes about a show we both watch. It felt less awkward than I expected.",
            "confidence": 0.75,
            "created_at": datetime.utcnow() - timedelta(days=1),
        },
        {
            "competency": "learning",
            "statement": "I spent 30 minutes reading about climate science because I was actually curious — not because it was assigned. I noticed I retained more.",
            "confidence": 0.80,
            "created_at": datetime.utcnow() - timedelta(days=3),
        },
        {
            "competency": "self",
            "statement": "I noticed that I get anxious before speaking in group settings, but the anxiety disappears once I actually say something. The fear is about the moment before, not the speaking itself.",
            "confidence": 0.85,
            "created_at": datetime.utcnow() - timedelta(days=5),
        },
        {
            "competency": "creative",
            "statement": "I drew something for fun for the first time in months. I kept thinking it was bad, but I kept going anyway. Finished it and felt proud.",
            "confidence": 0.70,
            "created_at": datetime.utcnow() - timedelta(days=8),
        },
        {
            "competency": "social",
            "statement": "I shared my idea in class even though my voice shook. Two people nodded. Nobody laughed. I realised my fear was bigger than the actual risk.",
            "confidence": 0.90,
            "created_at": datetime.utcnow() - timedelta(days=10),
        },
        {
            "competency": "health",
            "statement": "I went to bed 45 minutes earlier three nights in a row. My mood was noticeably better by day three. Sleep actually works.",
            "confidence": 0.80,
            "created_at": datetime.utcnow() - timedelta(days=12),
        },
        {
            "competency": "self",
            "statement": "I wrote down three things I was avoiding and chose one to do immediately. Starting was harder than finishing.",
            "confidence": 0.75,
            "created_at": datetime.utcnow() - timedelta(days=15),
        },
        {
            "competency": "learning",
            "statement": "I asked a teacher a question I was embarrassed about. They gave me a genuinely helpful answer. Asking is cheaper than staying confused.",
            "confidence": 0.85,
            "created_at": datetime.utcnow() - timedelta(days=18),
        },
    ]

    for spec in EVIDENCE:
        exists = db.scalar(
            select(Evidence).where(Evidence.user_id == user.id, Evidence.statement == spec["statement"])
        )
        if not exists:
            db.add(Evidence(tenant_id=tenant_id, user_id=user.id, source="youth", **spec))

    # ── Kai conversation history ───────────────────────────────────────────────

    CONVERSATION_EVENTS = [
        {
            "user_message": "I want to get better at talking to people.",
            "assistant_message": "Good. What is one low-stakes conversation you could try today?",
            "topic": "social",
        },
        {
            "user_message": "Give me a small challenge for today.",
            "assistant_message": "Ok. Here is something small: choose a 2-minute conversation with someone you normally ignore. It does not need to be deep — just real.",
            "topic": "social",
        },
        {
            "user_message": "That feels like too much. Make it easier.",
            "assistant_message": "Fair. Let's reduce it: instead of the full action, do just the first part — say hello and their name. That counts.",
            "topic": "social",
        },
        {
            "user_message": "I finished reading the book I chose. I actually liked it.",
            "assistant_message": "What did you notice about reading something you chose versus something assigned to you?",
            "topic": "learning",
        },
        {
            "user_message": "I can't today. I'm really tired.",
            "assistant_message": "That's okay. Today is not a day to force it. Do you want to record what's blocking you, or come back tomorrow with calm?",
            "topic": "general",
        },
    ]

    for spec in CONVERSATION_EVENTS:
        exists = db.scalar(
            select(ConversationEvent).where(
                ConversationEvent.user_id == user.id,
                ConversationEvent.user_message == spec["user_message"],
            )
        )
        if not exists:
            db.add(
                ConversationEvent(
                    tenant_id=tenant_id,
                    user_id=user.id,
                    pseudonym="demo-youth-01",
                    risk_level="none",
                    **spec,
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
