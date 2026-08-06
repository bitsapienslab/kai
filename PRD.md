# PRD — RISE V1

**Product:** RISE — Purpose, Agency and Action Agent  
**Version:** V1  
**Status:** Controlled local pilot  
**Primary audience:** Young people aged 13–17  
**Interface:** Responsive, installable mobile PWA  
**Backend:** FastAPI, PostgreSQL and pgvector

**Claim:** Rise above the noise. Build your direction.

**Strategic category:** Youth Development Operating System

### Product context

We live in a world of increasing options, stimulation and distraction, making it harder for a young person to understand what truly matters and where to invest attention, effort and time during a decisive stage of development. Many young people also face growing emotional distress, risky behaviors and dependencies that can compromise identity, autonomy and the future they are building.

RISE helps young people distinguish signal from noise, develop agency, purpose, character skills and stamina, and progressively build the ability to make good choices, act with intention and ask for help when needed.

RISE is not positioned as an AI companion or a thin wrapper around an LLM. The conversation is the entry point. The product asset is a longitudinal development system that connects assessment, behavior, experiences, evidence, safety and outcomes.

## 1. Product thesis

RISE exists to help a young person build internal and practical resources during a decisive stage of life. It has two complementary missions:

- **Development:** agency, purpose, character skills, stamina, autonomy and regulation.
- **Protection:** early recognition of risk, human support and safer decisions.

The central product principle is:

> RISE should become familiar without becoming indispensable.

The avatar can learn how the young person communicates and works best, but it must remain stable, transparent and safe. It mirrors preferences, not harmful behavior or emotional dependency.

## 2. RISE Development System

The product is organized into replaceable intelligence layers:

| Layer | Responsibility |
|---|---|
| Avatar / LLM | Conversation, explanation and reflection |
| Development Graph | Longitudinal representation of the young person |
| Assessment Engine | Validated developmental instruments and repeated screening |
| Intervention Engine | Selects the next experience, prompt or period of silence |
| Character Skills Engine | Converts behavior and evidence into observable capabilities |
| Safety Engine | Detects risk and governs escalation |
| Outcome Engine | Measures which interventions produce useful change |

The LLM provider must remain replaceable. RISE owns the development model, structured data, interventions, safety policy and outcome learning.

### Development Graph

The Development Graph connects:

```text
interests → values → capabilities → difficulties → projects
→ behaviors → feedback → evolution → objectives
```

It is more than conversation memory. It records how a young person learns, where they persist, what energizes them, which challenges help them grow and what capabilities they demonstrate over time.

### RISE development cycle

The proprietary product cycle is:

```text
Reflect → Initiate → Sustain → Evolve → new experience
```

Every meaningful conversation should move toward reflection, a real-world action, sustained effort or learning that changes the next step.

### Comfort place, not dependency place

RISE should feel familiar, calm and non-judgmental. Adaptive personalization may include:

- concise or detailed replies;
- direct or exploratory questions;
- calm or energetic tone;
- vocabulary and examples;
- moderate use of humor or emojis;
- preferred feedback intensity;
- preferred rhythm and contact time.

The avatar must not use exclusivity, guilt, emotional pressure or the suggestion that it replaces real relationships. A successful session can end with the young person leaving the application to act.

## 3. Executive summary

RISE V1 is a digital coach, tutor and mentor for young people. It helps them understand their interests, turn intentions into concrete goals, make commitments, reflect on outcomes, ask for help and build agency.

The product combines a personal PWA with a multi-tenant backend for organizations, guardians, researchers and administrators. The agent is called Kai.

Kai should be warm, demanding and responsible. It may challenge a young person without humiliating them, should not automatically agree with every conclusion, and must route safety situations to human support.

Success is not measured by screen time or message volume. It is measured by movement from reflection to real-world action and growing independence from the agent.

## 4. Problem

Young people often need help to:

- understand their interests and strengths;
- turn vague ideas into next steps;
- keep commitments;
- learn from failure;
- explore education, projects and career possibilities;
- ask trusted people for help;
- recognize abilities through evidence.

Existing tools are often generic motivational chatbots, static career tests, task managers without personal context or social products optimized for attention. RISE combines conversation, reflection, goals and accountability around real action.

RISE differentiates itself by accumulating structured evidence about how young people develop agency, rather than accumulating conversations alone.

## 5. Goals and non-goals

### Goals

- Provide a safe personal conversation space with Kai.
- Help each young person create concrete goals and commitments.
- Store action, reason, deadline, proof, anticipated difficulty and fallback plan.
- Provide check-ins, reflection and consent-based accountability.
- Give organizations secure user, consent and analytics management.
- Support controlled research with pseudonymization and auditability.
- Prepare personalized memory and adaptive agent behavior.

### Strategic roadmap goals

- Add validated developmental assessments as screening and development tools, never as diagnosis.
- Build repeated micro-assessments and periodic reassessments rather than relying on one onboarding questionnaire.
- Add a real-world experience engine with micro-projects, interviews, creation, contribution and exploration.
- Create a Character Skills Engine that distinguishes self-report from demonstrated behavior.
- Add an adaptive intervention engine that chooses what to say, what to suggest, how strongly to challenge and when to remain silent.
- Create an independent Safety Engine outside the avatar persona.
- Create an Outcome Engine that learns which interventions help which contexts, with safeguards against automated clinical or high-stakes decisions.

### Non-goals

- Diagnosing mental health conditions.
- Replacing psychologists, guardians, teachers or emergency services.
- Determining a young person’s “correct” career.
- Public rankings or social comparison.
- Maximizing screen time, message volume or notification opens.
- Full guardian surveillance.

## 6. Users and roles

- **Youth:** talks with Kai, completes check-ins, creates goals and records reflections.
- **Guardian:** supports the linked young person and sees approved progress and safety signals, not private conversations by default.
- **Organization administrator:** manages users, invitations, onboarding, consents and operational analytics.
- **Researcher:** accesses authorized pseudonymized data for a declared research purpose.
- **Platform administrator:** manages organizations, global policies and operational safety.

## 7. Core journeys

### Organization setup

An initial user registers with an organization name and becomes `organization_admin`. The administrator can invite guardians, youth and researchers.

### Youth onboarding

The youth provides a preferred name, school context, interests, energy areas, current difficulties, trusted people, contact preferences, challenge intensity, allowed hours, proactive-message consent, service terms and assent. Research consent is separate. The flow can be paused and resumed.

### Objective and accountability

Each objective records:

```text
Action / Why / Deadline / Proof / Anticipated difficulty / Fallback plan
```

When a commitment is missed, Kai helps the youth choose to recommit, reduce, redesign, ask for help or consciously abandon it.

### Kai conversation

Kai can act as coach, mentor, challenger, project architect, accountability partner or human-support bridge. It should ask one useful question at a time and avoid long automatic solutions.

### Research access

Researchers declare a purpose, the system verifies research consent, authorized records are shown under a stable pseudonym and every full-content access is audited.

## 8. V1 features

### Youth PWA

- Personalized Today dashboard.
- Emotional check-in.
- Focus of the day.
- Goals and progress.
- Private journal.
- Kai conversation.
- Recent conversations.
- Login, registration, refresh session and logout.
- Installable PWA experience.

### Administration

- User list and role/status filters.
- Invitations.
- Account suspension and reactivation.
- Onboarding status.
- Consent status.
- Basic operational dashboard.

### Proactive accountability

- Explicit consent.
- Light, normal and intensive cadence.
- Allowed hours.
- Daily limit.
- Pause control.
- Commitment reminders.
- Feedback linked to the notification and commitment.

### Research Console

- Aggregate analytics.
- Authorized conversation access.
- Stable pseudonyms.
- Purpose declaration.
- Audit log.
- Controlled exports.

## 9. Safety, privacy and multi-tenancy

Initial safety categories include crisis, self-harm, abuse, violence and immediate danger. A flagged message interrupts normal coaching, returns calm guidance, recommends trusted human or emergency help and creates a safety event for review.

The initial guardrail is lexical and is not a clinical assessment system.

Tenant scope comes from the authenticated token, not from a client-provided tenant header. Conversations are pseudonymized for research. Full-content access requires authorization and is audited. Guardians do not see private conversations by default.

## 10. Technical requirements

- Static responsive PWA with manifest and service worker.
- FastAPI REST API.
- JWT access and refresh tokens.
- PBKDF2 password hashing.
- SQLAlchemy models.
- PostgreSQL and pgvector.
- Alembic migration setup.
- Docker Compose local environment.
- Open WebUI-compatible chat completion endpoint.

## 11. Public API groups

### Authentication

`POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `GET /me`, `PATCH /me/onboarding`

### Accounts and administration

`POST /auth/invites`, `GET /admin/users`, `PATCH /admin/users/{user_id}/status`, `GET /admin/consents`

### Development and accountability

`POST /v1/users/{user_id}/objectives`, `GET /v1/proactive/preferences`, `PATCH /v1/proactive/preferences`, `POST /v1/proactive/check`, `POST /v1/proactive/notifications/{notification_id}/feedback`

### Conversation and research

`GET /v1/kai/policy`, `POST /v1/openwebui/chat/completions`, `GET /admin/dashboard`, `GET /research/dashboard`, `GET /v1/analytics/kpis`, `GET /research/conversations`, `GET /research/audit-log`

## 12. Acceptance criteria

- Users can register, log in, refresh and log out.
- Tenant data is isolated.
- Youth cannot access administration.
- Onboarding can be resumed.
- Service, assent, research and proactive consent are distinct.
- An objective contains action, reason, deadline, proof, difficulty and fallback plan.
- Notifications require active consent.
- Crisis messages receive a safe response and create a safety event.
- Full conversation access requires authorization and creates an audit record.
- The PWA works on small screens and can be installed.
- Docker starts the API and PostgreSQL/pgvector.

## 13. Pilot metrics

### Activation

- Invitation acceptance.
- Onboarding completion.
- Time to first goal.
- Time to first recorded action.

### Healthy participation

- Check-ins completed.
- Commitments completed.
- Commitments consciously renegotiated.
- Help requests made.

### Development

- Self-reported clarity.
- Actions initiated.
- Capabilities demonstrated.
- Reflection quality.
- Youth satisfaction.
- Reduced dependence on Kai over time.

### Safety

- Risk events detected.
- Time to human review.
- False positives and false negatives.
- Privacy complaints.
- Consent and pause usage.

## 14. Known risks and roadmap boundary

Risks include over-trust in Kai, intrusive notifications, incorrect personal inferences, guardian surveillance, re-identification and missed indirect crisis language.

V1 does not include the Liquid Focus shell, advanced adaptive profile, mission/evidence portfolio, full Safety Orchestrator, peer community, mentor marketplace or production Web Push delivery. Those capabilities belong to V2 and later.
