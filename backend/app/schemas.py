from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    conversation_id: str | None = None

class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=10)
    display_name: str = Field(min_length=1, max_length=120)
    tenant_name: str | None = None
    invite_token: str | None = None

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class InviteCreate(BaseModel):
    email: str
    role: str = "guardian"
    expires_days: int = Field(default=7, ge=1, le=30)

class OnboardingUpdate(BaseModel):
    preferred_name: str | None = None
    school_context: str | None = None
    energy_areas: list[str] = []
    interests: list[str] = []
    current_difficulties: list[str] = []
    trusted_people: list[str] = []
    contact_preference: str | None = None
    challenge_intensity: str = "normal"
    allowed_hours: list[str] = []
    proactive_consent: bool = False
    service_terms: bool = False
    youth_assent: bool = False
    guardian_consent: bool = False
    research_consent: bool = False

class ProactivePreferenceUpdate(BaseModel):
    cadence: str = "normal"
    allowed_hours: list[str] = []
    channel: str = "push"
    paused: bool = False
    max_per_day: int = Field(default=1, ge=0, le=3)

class NotificationFeedback(BaseModel):
    feedback: str = Field(min_length=1, max_length=2000)

class AdaptiveFeedback(BaseModel):
    hypothesis_id: str
    accepted: bool
    correction: str | None = None

class MissionCreate(BaseModel):
    title: str
    mission_type: str = "investigate"
    hypothesis: str
    action: str
    proof: str
    anticipated_difficulty: str = ""
    fallback_plan: str = ""
    due_at: datetime | None = None

class MissionFeedback(BaseModel):
    learning: str = Field(min_length=1, max_length=3000)
    status: str = "completed"

class EvidenceCreate(BaseModel):
    competency: str
    statement: str = Field(min_length=1, max_length=2000)
    mission_id: str | None = None
    confidence: float = Field(default=0.5, ge=0, le=1)

class PushSubscriptionCreate(BaseModel):
    endpoint: str
    subscription: dict


class CommitmentCreate(BaseModel):
    title: str
    action: str
    why: str
    due_at: datetime | None = None
    proof: str
    anticipated_difficulty: str
    fallback_plan: str


class ConsentUpdate(BaseModel):
    kind: str
    granted: bool
    granted_by: str

class ObjectiveUpdate(BaseModel):
    status: str | None = None
    progress: int | None = Field(default=None, ge=0, le=100)

class MissionStatusUpdate(BaseModel):
    status: str
