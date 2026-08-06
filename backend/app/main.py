import hashlib
from datetime import datetime, timedelta
from secrets import token_urlsafe
from sqlalchemy import func, select
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from .config import settings
from .db import Base, engine, get_db
from .dependencies import CurrentUser, current_user, require_roles
from .guardrails import inspect_message, kai_system_prompt, safety_category
from .models import AdaptiveProfile, AuditEvent, Consent, ConversationEvent, Evidence, GuardianYouth, Invitation, Mission, Objective, ProactiveNotification, ProactivePreference, PushSubscription, RefreshSession, SafetyCase, Tenant, User
from .schemas import AdaptiveFeedback, ChatRequest, CommitmentCreate, ConsentUpdate, EvidenceCreate, InviteCreate, LoginRequest, MissionCreate, MissionFeedback, NotificationFeedback, OnboardingUpdate, ProactivePreferenceUpdate, PushSubscriptionCreate, RefreshRequest, RegisterRequest
from .security import ACCESS_MINUTES, REFRESH_DAYS, create_token, decode_token, hash_password, verify_password

app = FastAPI(title="RISE API", version="0.2.0")

@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)

def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def issue_tokens(user: User, db: Session) -> dict:
    access = create_token(user.id, user.tenant_id, user.role, "access", timedelta(minutes=ACCESS_MINUTES))
    refresh = create_token(user.id, user.tenant_id, user.role, "refresh", timedelta(days=REFRESH_DAYS))
    db.add(RefreshSession(user_id=user.id, token_hash=token_hash(refresh), expires_at=datetime.utcnow() + timedelta(days=REFRESH_DAYS)))
    db.commit()
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer", "expires_in": ACCESS_MINUTES * 60}

def audit(db: Session, identity: CurrentUser, action: str, target_type: str, target_id: str | None = None, purpose: str | None = None, metadata: dict | None = None) -> None:
    db.add(AuditEvent(tenant_id=identity.user.tenant_id, actor_id=identity.user.id, action=action, target_type=target_type, target_id=target_id, purpose=purpose, metadata_json=metadata or {}))

def pseudonym(tenant_id: str, user_id: str) -> str:
    return hashlib.sha256(f"{tenant_id}:{user_id}".encode()).hexdigest()[:24]

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "bussola-api", "model": settings.model_name}

@app.post("/auth/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> dict:
    invite = None
    tenant_id = None
    role = "organization_admin" if body.tenant_name else "youth"
    if body.invite_token:
        invite = db.scalar(select(Invitation).where(Invitation.token_hash == token_hash(body.invite_token)))
        if not invite or invite.accepted_at or invite.expires_at < datetime.utcnow(): raise HTTPException(400, "Invitation is invalid or expired")
        tenant_id, role = invite.tenant_id, invite.role
    elif not body.tenant_name:
        raise HTTPException(400, "tenant_name or invite_token is required")
    if db.scalar(select(User).where(User.tenant_id == tenant_id, User.email == body.email.lower())): raise HTTPException(409, "Email already registered")
    if not tenant_id:
        tenant = Tenant(name=body.tenant_name); db.add(tenant); db.flush(); tenant_id = tenant.id
    user = User(tenant_id=tenant_id, email=body.email.lower(), display_name=body.display_name, password_hash=hash_password(body.password), role=role)
    db.add(user); db.flush()
    if invite: invite.accepted_at = datetime.utcnow()
    db.commit()
    return {"user": {"id": user.id, "email": user.email, "role": user.role, "tenant_id": user.tenant_id}, **issue_tokens(user, db)}

@app.post("/auth/login")
def login(body: LoginRequest, db: Session = Depends(get_db)) -> dict:
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if not user or not user.is_active or not verify_password(body.password, user.password_hash): raise HTTPException(401, "Invalid credentials")
    user.last_seen_at = datetime.utcnow(); db.commit()
    return {"user": {"id": user.id, "email": user.email, "display_name": user.display_name, "role": user.role, "tenant_id": user.tenant_id, "onboarding_status": user.onboarding_status}, **issue_tokens(user, db)}

@app.post("/auth/refresh")
def refresh(body: RefreshRequest, db: Session = Depends(get_db)) -> dict:
    try: claims = decode_token(body.refresh_token)
    except ValueError: raise HTTPException(401, "Invalid refresh token")
    if claims.get("kind") != "refresh": raise HTTPException(401, "Refresh token required")
    session = db.scalar(select(RefreshSession).where(RefreshSession.token_hash == token_hash(body.refresh_token), RefreshSession.revoked_at.is_(None)))
    user = db.get(User, claims.get("sub"))
    if not session or not user or session.expires_at < datetime.utcnow(): raise HTTPException(401, "Refresh session expired")
    session.revoked_at = datetime.utcnow(); db.commit()
    return issue_tokens(user, db)

@app.post("/auth/logout")
def logout(body: RefreshRequest, db: Session = Depends(get_db), identity: CurrentUser = Depends(current_user)) -> dict:
    session = db.scalar(select(RefreshSession).where(RefreshSession.token_hash == token_hash(body.refresh_token), RefreshSession.user_id == identity.user.id))
    if session: session.revoked_at = datetime.utcnow(); db.commit()
    return {"ok": True}

@app.get("/me")
def me(identity: CurrentUser = Depends(current_user)) -> dict:
    u = identity.user
    return {"id": u.id, "email": u.email, "display_name": u.display_name, "role": u.role, "tenant_id": u.tenant_id, "onboarding_status": u.onboarding_status, "onboarding": u.onboarding_data}

@app.patch("/me/onboarding")
def onboarding(body: OnboardingUpdate, identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    if not body.service_terms or not body.youth_assent: raise HTTPException(400, "Service terms and youth assent are required")
    u = identity.user; u.onboarding_data = body.model_dump(); u.onboarding_status = "complete"; ensure_profile(identity, db); db.add(Consent(tenant_id=u.tenant_id, user_id=u.id, kind="service", granted=True, granted_by=u.id)); db.add(Consent(tenant_id=u.tenant_id, user_id=u.id, kind="research", granted=body.research_consent, granted_by=u.id)); db.add(Consent(tenant_id=u.tenant_id, user_id=u.id, kind="proactive_messages", granted=body.proactive_consent, granted_by=u.id)); pref = db.get(ProactivePreference, u.id) or ProactivePreference(user_id=u.id, tenant_id=u.tenant_id); pref.cadence=body.challenge_intensity; pref.allowed_hours=body.allowed_hours; pref.paused=not body.proactive_consent; db.add(pref); db.commit()
    return {"status": u.onboarding_status, "data": u.onboarding_data}

@app.post("/auth/invites")
def create_invite(body: InviteCreate, identity: CurrentUser = Depends(require_roles("organization_admin", "platform_admin")), db: Session = Depends(get_db)) -> dict:
    if body.role not in {"guardian", "youth", "researcher"}: raise HTTPException(400, "Invalid invite role")
    raw = token_urlsafe(32); row = Invitation(tenant_id=identity.user.tenant_id, email=body.email.lower(), role=body.role, token_hash=token_hash(raw), invited_by=identity.user.id, expires_at=datetime.utcnow() + timedelta(days=body.expires_days)); db.add(row); audit(db, identity, "invite.create", "invitation", row.id); db.commit()
    return {"id": row.id, "email": row.email, "role": row.role, "expires_at": row.expires_at, "invite_token": raw}

@app.post("/v1/users/{user_id}/consents")
def update_consent(user_id: str, body: ConsentUpdate, identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    if identity.user.id != user_id and identity.user.role not in {"guardian", "organization_admin", "platform_admin"}: raise HTTPException(403, "Not allowed")
    row = Consent(tenant_id=identity.user.tenant_id, user_id=user_id, kind=body.kind, granted=body.granted, granted_by=identity.user.id); db.add(row); db.commit(); return {"id": row.id, "kind": row.kind, "granted": row.granted}

@app.post("/v1/users/{user_id}/objectives")
def create_commitment(user_id: str, body: CommitmentCreate, identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    if identity.user.id != user_id and identity.user.role not in {"guardian", "organization_admin", "platform_admin"}: raise HTTPException(403, "Not allowed")
    row = Objective(tenant_id=identity.user.tenant_id, user_id=user_id, **body.model_dump()); db.add(row); db.commit(); db.refresh(row); return {"id": row.id, "status": row.status, **body.model_dump()}

def ensure_profile(identity: CurrentUser, db: Session) -> AdaptiveProfile:
    profile = db.get(AdaptiveProfile, identity.user.id)
    if not profile:
        profile = AdaptiveProfile(user_id=identity.user.id, tenant_id=identity.user.tenant_id); db.add(profile); db.flush()
    return profile

@app.get("/me/today")
def today(identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    profile = ensure_profile(identity, db)
    mission = db.scalar(select(Mission).where(Mission.user_id == identity.user.id, Mission.status == "active").order_by(Mission.due_at.asc().nullslast()).limit(1))
    objective = db.scalar(select(Objective).where(Objective.user_id == identity.user.id, Objective.status == "active").order_by(Objective.due_at.asc().nullslast()).limit(1))
    evidence = db.scalar(select(Evidence).where(Evidence.user_id == identity.user.id).order_by(Evidence.created_at.desc()).limit(1))
    if mission:
        orientation = {"title": "A tua próxima experiência", "body": mission.hypothesis, "reason": "Existe uma missão ativa que pode produzir informação real."}
        action = {"id": mission.id, "title": mission.title, "body": mission.action, "proof": mission.proof, "kind": "mission"}
    elif objective:
        orientation = {"title": "Uma coisa de cada vez", "body": "Há um compromisso teu que ainda merece uma decisão clara.", "reason": "Prioridade baseada no prazo e no teu compromisso ativo."}
        action = {"id": objective.id, "title": objective.title, "body": objective.action, "proof": objective.proof, "kind": "objective"}
    else:
        orientation = {"title": "O que merece a tua atenção?", "body": "Escolhe uma pequena ação que produza aprendizagem hoje.", "reason": "Não há compromissos ativos; o sistema devolve a escolha ao jovem."}
        action = None
    reflection = {"title": "Leva a aprendizagem contigo", "body": f"A tua evidência mais recente: {evidence.statement}", "kind": "evidence"} if evidence else {"title": "Regista o que descobrires", "body": "Uma experiência só se torna aprendizagem quando reparas no que aconteceu.", "kind": "reflection"}
    db.commit(); return {"orientation": orientation, "action": action, "reflection": reflection, "adaptive": {"mode": profile.preferred_mode, "autonomy_level": profile.autonomy_level, "challenge_tolerance": profile.challenge_tolerance}}

@app.get("/me/adaptive-profile")
def adaptive_profile(identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    profile = ensure_profile(identity, db); db.commit(); return {"autonomy_level": profile.autonomy_level, "challenge_tolerance": profile.challenge_tolerance, "preferred_mode": profile.preferred_mode, "hypotheses": profile.current_hypotheses, "inferences": profile.inference_log}

@app.patch("/me/adaptive-profile/feedback")
def adaptive_feedback(body: AdaptiveFeedback, identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    profile = ensure_profile(identity, db); profile.inference_log = [*profile.inference_log, {"id": body.hypothesis_id, "accepted": body.accepted, "correction": body.correction, "at": datetime.utcnow().isoformat()}][-50:]; profile.updated_at = datetime.utcnow(); db.commit(); return {"ok": True}

@app.post("/me/missions")
def create_mission(body: MissionCreate, identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    row = Mission(tenant_id=identity.user.tenant_id, user_id=identity.user.id, **body.model_dump()); db.add(row); db.commit(); db.refresh(row); return {"id": row.id, "status": row.status, **body.model_dump()}

@app.post("/me/missions/{mission_id}/feedback")
def mission_feedback(mission_id: str, body: MissionFeedback, identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    row = db.scalar(select(Mission).where(Mission.id == mission_id, Mission.user_id == identity.user.id))
    if not row: raise HTTPException(404, "Mission not found")
    row.learning = body.learning; row.status = body.status; db.commit(); return {"id": row.id, "status": row.status, "learning": row.learning}

@app.get("/me/evidence")
def evidence(identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(Evidence).where(Evidence.user_id == identity.user.id).order_by(Evidence.created_at.desc()).limit(100)).all(); return {"items": [{"id": r.id, "competency": r.competency, "statement": r.statement, "confidence": r.confidence, "created_at": r.created_at} for r in rows]}

@app.post("/me/evidence")
def create_evidence(body: EvidenceCreate, identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    row = Evidence(tenant_id=identity.user.tenant_id, user_id=identity.user.id, **body.model_dump()); db.add(row); db.commit(); db.refresh(row); return {"id": row.id, "competency": row.competency, "statement": row.statement, "confidence": row.confidence}

@app.get("/me/progress")
def progress(identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    total = db.scalar(select(func.count(Mission.id)).where(Mission.user_id == identity.user.id)) or 0; completed = db.scalar(select(func.count(Mission.id)).where(Mission.user_id == identity.user.id, Mission.status == "completed")) or 0; evidence_count = db.scalar(select(func.count(Evidence.id)).where(Evidence.user_id == identity.user.id)) or 0; return {"missions_started": total, "missions_completed": completed, "evidence_count": evidence_count, "completion_rate": round(completed / total * 100, 1) if total else 0}

@app.post("/me/push-subscriptions")
def push_subscription(body: PushSubscriptionCreate, identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    row = db.scalar(select(PushSubscription).where(PushSubscription.endpoint == body.endpoint)) or PushSubscription(tenant_id=identity.user.tenant_id, user_id=identity.user.id, endpoint=body.endpoint, subscription_json=body.subscription)
    row.subscription_json = body.subscription; row.user_id = identity.user.id; db.add(row); db.commit(); return {"id": row.id, "registered": True}

@app.post("/internal/safety/evaluate")
def safety_evaluate(body: ChatRequest, identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    result = inspect_message(body.message)
    if result.action != "allow": db.add(SafetyCase(tenant_id=identity.user.tenant_id, user_id=identity.user.id, level=result.level, category=safety_category(body.message))); db.commit()
    return {"level": result.level, "action": result.action, "category": safety_category(body.message)}

@app.get("/v1/proactive/preferences")
def proactive_preferences(identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    pref = db.get(ProactivePreference, identity.user.id)
    return {"cadence": pref.cadence, "allowed_hours": pref.allowed_hours, "channel": pref.channel, "paused": pref.paused, "max_per_day": pref.max_per_day} if pref else {"cadence": "normal", "allowed_hours": [], "channel": "push", "paused": True, "max_per_day": 1}

@app.patch("/v1/proactive/preferences")
def update_proactive_preferences(body: ProactivePreferenceUpdate, identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    if not db.scalar(select(Consent).where(Consent.user_id == identity.user.id, Consent.kind == "proactive_messages", Consent.granted.is_(True))): raise HTTPException(403, "Proactive messaging consent is required")
    pref = db.get(ProactivePreference, identity.user.id) or ProactivePreference(user_id=identity.user.id, tenant_id=identity.user.tenant_id)
    for key, value in body.model_dump().items(): setattr(pref, key, value)
    pref.updated_at = datetime.utcnow(); db.add(pref); db.commit(); return body.model_dump()

@app.post("/v1/proactive/check")
def proactive_check(identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    pref = db.get(ProactivePreference, identity.user.id)
    if not pref or pref.paused: return {"items": [], "reason": "paused_or_not_configured"}
    active_consent = db.scalar(select(Consent).where(Consent.user_id == identity.user.id, Consent.kind == "proactive_messages", Consent.granted.is_(True)))
    if not active_consent: return {"items": [], "reason": "no_consent"}
    objectives = db.scalars(select(Objective).where(Objective.user_id == identity.user.id, Objective.status == "active").order_by(Objective.due_at.asc().nullslast()).limit(pref.max_per_day)).all()
    items = []
    for objective in objectives:
        existing = db.scalar(select(ProactiveNotification).where(ProactiveNotification.objective_id == objective.id, ProactiveNotification.sent_at.is_(None)))
        if not existing:
            item = ProactiveNotification(user_id=identity.user.id, tenant_id=identity.user.tenant_id, objective_id=objective.id, title="Vamos rever o teu compromisso", body=f"Ficou planeado: {objective.action}. Que prova tens até agora?", scheduled_for=datetime.utcnow()); db.add(item); db.flush()
        else: item = existing
        items.append({"id": item.id, "title": item.title, "body": item.body, "objective_id": item.objective_id})
    db.commit(); return {"items": items}

@app.post("/v1/proactive/notifications/{notification_id}/feedback")
def proactive_feedback(notification_id: str, body: NotificationFeedback, identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    row = db.scalar(select(ProactiveNotification).where(ProactiveNotification.id == notification_id, ProactiveNotification.user_id == identity.user.id))
    if not row: raise HTTPException(404, "Notification not found")
    row.feedback = body.feedback; row.sent_at = row.sent_at or datetime.utcnow(); db.commit(); return {"ok": True}

@app.post("/v1/openwebui/chat/completions")
def openwebui_chat(body: ChatRequest, identity: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    safety = inspect_message(body.message); answer = safety.response if safety.action != "allow" else "Vamos tornar isto concreto. O que está sob o teu controlo e qual é a menor ação que podes testar hoje?"
    event = ConversationEvent(tenant_id=identity.user.tenant_id, user_id=identity.user.id, pseudonym=pseudonym(identity.user.tenant_id, identity.user.id), risk_level=safety.level, user_message=body.message, assistant_message=answer); db.add(event); db.commit()
    return {"id": event.id, "object": "chat.completion", "model": settings.model_name, "choices": [{"index": 0, "message": {"role": "assistant", "content": answer}, "finish_reason": "stop"}], "safety": {"level": safety.level, "action": safety.action}}

@app.get("/admin/users")
def admin_users(identity: CurrentUser = Depends(require_roles("organization_admin", "platform_admin")), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(User).where(User.tenant_id == identity.user.tenant_id).order_by(User.created_at.desc())).all(); return {"items": [{"id": u.id, "email": u.email, "display_name": u.display_name, "role": u.role, "active": u.is_active, "onboarding_status": u.onboarding_status, "last_seen_at": u.last_seen_at} for u in rows]}

@app.patch("/admin/users/{user_id}/status")
def admin_user_status(user_id: str, active: bool, identity: CurrentUser = Depends(require_roles("organization_admin", "platform_admin")), db: Session = Depends(get_db)) -> dict:
    user = db.scalar(select(User).where(User.id == user_id, User.tenant_id == identity.user.tenant_id));
    if not user: raise HTTPException(404, "User not found")
    user.is_active = active; audit(db, identity, "user.status", "user", user.id, metadata={"active": active}); db.commit(); return {"id": user.id, "active": user.is_active}

@app.get("/admin/consents")
def admin_consents(identity: CurrentUser = Depends(require_roles("organization_admin", "platform_admin")), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(Consent).where(Consent.tenant_id == identity.user.tenant_id).order_by(Consent.created_at.desc())).all(); return {"items": [{"user_id": c.user_id, "kind": c.kind, "granted": c.granted, "granted_by": c.granted_by, "created_at": c.created_at} for c in rows]}

@app.get("/admin/dashboard")
@app.get("/research/dashboard")
@app.get("/v1/analytics/kpis")
def dashboard(identity: CurrentUser = Depends(require_roles("organization_admin", "platform_admin", "researcher")), db: Session = Depends(get_db)) -> dict:
    tenant = identity.user.tenant_id; total_users = db.scalar(select(func.count(User.id)).where(User.tenant_id == tenant)) or 0; active_users = db.scalar(select(func.count(User.id)).where(User.tenant_id == tenant, User.is_active.is_(True))) or 0; messages = db.scalar(select(func.count(ConversationEvent.id)).where(ConversationEvent.tenant_id == tenant)) or 0; risks = db.scalar(select(func.count(ConversationEvent.id)).where(ConversationEvent.tenant_id == tenant, ConversationEvent.risk_level != "none")) or 0; objectives = db.scalar(select(func.count(Objective.id)).where(Objective.tenant_id == tenant)) or 0; completed = db.scalar(select(func.count(Objective.id)).where(Objective.tenant_id == tenant, Objective.status == "completed")) or 0; onboarded = db.scalar(select(func.count(User.id)).where(User.tenant_id == tenant, User.onboarding_status == "complete")) or 0
    return {"privacy": {"mode": "pseudonymized", "raw_text": "restricted"}, "kpis": {"registered_users": total_users, "active_users": active_users, "onboarding_completion_rate": round(onboarded / total_users * 100, 1) if total_users else 0, "conversation_events": messages, "flagged_events": risks, "objectives": objectives, "objectives_completed": completed, "objective_completion_rate": round(completed / objectives * 100, 1) if objectives else 0}, "trends": []}

@app.get("/research/conversations")
def research_conversations(purpose: str, identity: CurrentUser = Depends(require_roles("researcher", "platform_admin")), db: Session = Depends(get_db)) -> dict:
    consented = select(Consent.user_id).where(Consent.tenant_id == identity.user.tenant_id, Consent.kind == "research", Consent.granted.is_(True)).distinct(); rows = db.scalars(select(ConversationEvent).where(ConversationEvent.tenant_id == identity.user.tenant_id, ConversationEvent.user_id.in_(consented)).order_by(ConversationEvent.created_at.desc()).limit(100)).all(); audit(db, identity, "research.conversations.read", "conversation", purpose=purpose, metadata={"count": len(rows)}); db.commit(); return {"purpose": purpose, "items": [{"id": r.id, "pseudonym": r.pseudonym, "risk_level": r.risk_level, "user_message": r.user_message, "assistant_message": r.assistant_message, "created_at": r.created_at} for r in rows]}

@app.get("/research/audit-log")
def research_audit(identity: CurrentUser = Depends(require_roles("researcher", "platform_admin")), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(AuditEvent).where(AuditEvent.tenant_id == identity.user.tenant_id).order_by(AuditEvent.created_at.desc()).limit(200)).all(); return {"items": [{"actor_id": r.actor_id, "action": r.action, "target_type": r.target_type, "purpose": r.purpose, "created_at": r.created_at} for r in rows]}

@app.get("/v1/kai/policy")
def policy(identity: CurrentUser = Depends(current_user)) -> dict:
    return {"name": "NORTE/Kai", "system_prompt": kai_system_prompt(), "proactivity": {"default": "normal", "max_per_day": 1}}
