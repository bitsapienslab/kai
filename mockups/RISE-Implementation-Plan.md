# RISE — Plano de Implementação

**Data:** 6 Agosto 2026  
**Base:** `RISE-Kai-Mobile-UI-Prompt-Library.md` + mockups gerados + codebase V1 actual  
**Objectivo:** Transformar o snapshot V1 (dashboard administrativo) na experiência mobile RISE/Kai definida nos mockups.

---

## 1. Resumo executivo

A app actual é um **dashboard web desktop** com sidebar, estilo editorial/produtividade, navegação Today/Objectives/Journal/Kai/Admin/Research, e dados majoritariamente mock no frontend.

A visão dos mockups é uma **PWA mobile-first** com:
- Mundo pessoal vivo (6 distritos de desenvolvimento)
- Kai como companheiro conversacional (não chatbot genérico)
- Acções no mundo real → evidência → reflexão → mudança no mundo
- Regressão controlada sem punição (Legacy vs Current Energy)
- Navegação: **World · Kai · Journey · Progress · Me**

O backend V1 já cobre ~40% das necessidades funcionais (auth, missões, objectivos, evidências, perfil adaptativo, notificações proactivas, guardrails). Falta o **World Engine**, a **nova shell mobile**, e a **ligação frontend ↔ API** nas áreas do jovem.

---

## 2. Mockups disponíveis vs. ecrãs planeados

### Mockups já gerados (5 imagens)

| Ficheiro | Ecrã | Prompt Library | Estado |
|----------|------|----------------|--------|
| `bdd59aaa…png` | My World (noite/cinemático) | SCREEN 01 | ✅ Referência visual |
| `e1b39fbc…png` / `908886bb…png` | My World (pastel/claro) | SCREEN 01 | ✅ Variantes de estilo |
| `77f72f7f…png` | Kai Chat | SCREEN 02 | ✅ Referência visual |
| `a1feb1f6…png` | Welcome / Onboarding | SCREEN 18 (parcial) | ✅ Referência visual |

**Estilo visual aprovado:** *Calm Editorial Cartoon + Soft 2.5D World-Building* — usar como constituição visual fixa.

### Sequência prioritária (Prompt Library §29) — 8 ecrãs

| # | Ecrã | Mockup | App actual | Prioridade |
|---|------|--------|------------|------------|
| 1 | My World — estado normal | ✅ | ❌ Sidebar dashboard | P0 |
| 2 | Kai Chat | ✅ | ⚠️ Mock estático | P0 |
| 3 | Real-world Mission | ❌ | ⚠️ Backend only | P0 |
| 4 | Growth Event (pós-acção) | ❌ | ❌ | P1 |
| 5 | Controlled Decline | ❌ | ❌ | P1 |
| 6 | Reawakening | ❌ | ❌ | P1 |
| 7 | Permanent Milestone | ❌ | ❌ | P2 |
| 8 | Mature World (1 ano) | ❌ | ❌ | P2 |

### Restantes ecrãs (Prompt Library) — fase posterior

| Screens | Funcionalidade | Fase |
|---------|----------------|------|
| 05 — Before/After | Comparação visual de transformação | Fase 2 |
| 08 — Welcome Back | Retorno após ausência longa | Fase 2 |
| 09–10 — Pause Mode | Pausa consciente do mundo | Fase 2 |
| 12 — Development Map | Legacy + Current Energy por distrito | Fase 2 |
| 13–14 — District Detail | Zoom e história por distrito | Fase 2 |
| 15 — Journey Selection | Experiências finitas (30d, 8sem, 6sem) | Fase 3 |
| 16 — Weekly Reflection | Reflexão semanal guiada | Fase 2 |
| 17 — Growth Timeline | Linha temporal emocional | Fase 3 |
| 20 — Kai + World Context | Conversa com contexto visual | Fase 2 |
| 21 — Choice of Next Move | Tiny / Real / Stretch moves | Fase 1 |
| 22 — Personalisation | 5 estilos visuais do mundo | Fase 3 |
| 23–24 — Achievement / Setback | Sem badges, sem falha | Fase 2 |
| 25 — Global World View | Ecrã icónico de marca | Fase 3 |

---

## 3. Gap analysis — App actual vs. Visão RISE

### 3.1 Frontend

| Área | Actual | Target (mockups) | Gap |
|------|--------|------------------|-----|
| Layout | Sidebar desktop 245px | Mobile portrait, bottom nav 5 tabs | **Reescrever shell** |
| Home | Dashboard cards (check-in, objectivos, conversas) | Mundo 3D/2.5D com 6 distritos | **Novo ecrã World** |
| Navegação | Today · Objectives · Journal · Kai · Admin | World · Kai · Journey · Progress · Me | **Reestruturar IA** |
| Kai Chat | Mensagens hardcoded, sem API | Chips de resposta, acção real-world card, contexto de distrito | **Ligar API + UX** |
| Objectivos | Array JS local | Missões com dificuldade, prova, plano B | **Ligar API** |
| Diário | localStorage-like (só UI) | Reflexão semanal + registo de aprendizagem | **Ligar API evidence** |
| Onboarding | Form funcional | Welcome screen + "Start with Kai" + categorias | **Redesign visual** |
| Progress | Inexistente (só admin KPIs) | Timeline, mapa de desenvolvimento, before/after | **Construir do zero** |
| Mundo visual | Inexistente | Distritos, energia, legacy, marcos | **Construir do zero** |
| Streak | "6 days" hardcoded | **Proibido** nos mockups — remover | **Eliminar** |
| Branding | Mistura Bússola/RISE/NORTE | RISE unificado | **Normalizar** |
| Idioma | PT/EN misturado | PT-PT consistente | **Unificar** |

### 3.2 Backend

| Funcionalidade | Estado API | Gap |
|----------------|------------|-----|
| Auth multi-tenant | ✅ Completo | — |
| Onboarding + consentimentos | ✅ Completo | Adicionar personalização visual |
| Objectivos / compromissos | ✅ CRUD parcial | Falta listagem GET, update status, progress |
| Missões | ✅ Create + feedback | Falta listagem, link a distrito |
| Evidências | ✅ Create + list | Falta link a transformações do mundo |
| Perfil adaptativo | ✅ GET + feedback | Falta inferência automática |
| Chat Kai | ⚠️ Stub (resposta fixa) | **Integrar LLM real** |
| Guardrails | ✅ Regex básico | Expandir categorias |
| Notificações proactivas | ✅ Check + feedback | Web Push production |
| `/me/today` | ✅ Existe | Frontend não consome |
| **World Engine** | ❌ | **Novo módulo completo** |
| **Distritos (6)** | ❌ | Modelo + estado energia/legacy |
| **Transformações** | ❌ | Eventos before/after por acção |
| **Pause Mode** | ❌ | Modelo + lógica freeze |
| **Journeys** | ❌ | Modelo + milestones + duração |
| **Landmarks** | ❌ | Conquistas permanentes |
| **Welcome Back** | ❌ | Detecção ausência + flow |
| **Weekly Reflection** | ❌ | Perguntas + respostas |
| **Memory / pgvector** | ⚠️ Modelo only | Sem endpoints |
| **Guardian dashboard** | ❌ | Modelo GuardianYouth only |

---

## 4. Arquitectura proposta

### 4.1 Lógica central (inviolável)

```
Real life action → evidence → reflection → world change → next choice
```

### 4.2 Lógica de regressão

```
Legacy never disappears. Current energy can change. Restarting is easy.
```

### 4.3 World Engine (novo)

```text
┌─────────────────────────────────────────────────┐
│                   World State                    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ Social  │ │Learning │ │ Health  │  ...×6      │
│  │ legacy  │ │ legacy  │ │ legacy  │           │
│  │ energy  │ │ energy  │ │ energy  │           │
│  └─────────┘ └─────────┘ └─────────┘           │
│                                                  │
│  Landmarks[] · Transformations[] · PauseState   │
└─────────────────────────────────────────────────┘
         ↑                    ↓
    Evidence/Mission    Visual state API
    Completion          → Frontend renderer
```

**Distritos (enum fixo):**
- `social` — Social District
- `learning` — Learning District
- `health` — Health District
- `creative` — Creative District
- `projects` — Projects District
- `self_knowledge` — Self-Knowledge District

**Estados por distrito:**
- `legacy_level`: `none | seed | growing | established | strong`
- `current_energy`: `dormant | low | medium | high | active`
- `landmarks[]`: objectos permanentes (nunca destruídos)

**Transições:**
- Acção completada → `energy` sobe + possível `legacy` sobe + evento visual
- Inactividade (sem pause) → `energy` desce gradualmente (nunca `legacy` desce)
- Acção de recuperação → `energy` sobe rapidamente
- Pause mode → `energy` congelado

### 4.4 Frontend — nova estrutura de ficheiros

```text
v1/
├── index.html              → shell mobile (bottom nav)
├── styles/
│   ├── tokens.css          → design tokens (pastel + dark variants)
│   ├── world.css           → mundo / distritos
│   ├── kai.css             → chat
│   ├── mission.css         → missões
│   └── shared.css          → componentes comuns
├── js/
│   ├── app.js              → bootstrap, routing, session
│   ├── api.js              → client HTTP
│   ├── views/
│   │   ├── world.js
│   │   ├── kai.js
│   │   ├── journey.js
│   │   ├── progress.js
│   │   └── me.js
│   └── components/
│       ├── bottom-nav.js
│       ├── mission-card.js
│       ├── response-chips.js
│       └── world-renderer.js
├── assets/
│   └── world/              → ilustrações por distrito/estado
└── admin/                  → consola admin separada (actual sidebar)
    └── index.html
```

---

## 5. Plano por fases

### FASE 0 — Fundação (1–2 semanas)

**Objectivo:** Shell mobile funcional com auth e navegação correcta.

| Task | Tipo | Detalhe |
|------|------|---------|
| 0.1 | Frontend | Nova `index.html` mobile-first, bottom nav (World/Kai/Journey/Progress/Me) |
| 0.2 | Frontend | Design tokens CSS alinhados com mockups pastel (variante clara como default) |
| 0.3 | Frontend | Migrar auth + onboarding para novo layout (usar mockup Welcome) |
| 0.4 | Frontend | Extrair admin/research para `/admin/index.html` (manter funcional) |
| 0.5 | Frontend | `api.js` centralizado; ligar login, onboarding, `/me`, logout |
| 0.6 | Cleanup | Remover streak, normalizar branding RISE, PT-PT |
| 0.7 | Cleanup | Corrigir `sw.js` (remover ref a `liquid.css` inexistente) |

**Entregável:** App instalável com login, onboarding redesigned, 5 tabs navegáveis (conteúdo placeholder).

---

### FASE 1 — Core Loop (2–3 semanas)

**Objectivo:** Ciclo completo acção → reflexão → progresso, sem mundo 3D ainda.

| Task | Tipo | Detalhe |
|------|------|---------|
| 1.1 | Backend | GET `/me/objectives`, PATCH status/progress |
| 1.2 | Backend | GET `/me/missions`, link `district` field |
| 1.3 | Backend | Integrar LLM no chat (OpenWebUI ou provider) com system prompt Kai |
| 1.4 | Backend | Chat: response chips logic, extrair "real-world action" da conversa |
| 1.5 | Frontend | **Kai Chat** conforme mockup: chips, action card, composer, API |
| 1.6 | Frontend | **Mission screen** (SCREEN 03): título, acção, dificuldade, "I'll try it" |
| 1.7 | Frontend | **Choice of Next Move** (SCREEN 21): Tiny/Real/Stretch |
| 1.8 | Frontend | Ligar `/me/today` ao card "Today's Next Move" no World |
| 1.9 | Frontend | Journal → POST `/me/evidence` (competency + statement) |
| 1.10 | Frontend | Journey tab: listar objectivos/missões activas do utilizador |
| 1.11 | Frontend | Progress tab: GET `/me/progress` + lista evidências |
| 1.12 | Frontend | Me tab: perfil, preferências proactivas, pause mode entry |

**Entregável:** Jovem consegue falar com Kai, receber missão, completar, registar evidência, ver progresso.

---

### FASE 2 — World Engine (3–4 semanas)

**Objectivo:** Mundo visual que reflecte desenvolvimento real.

| Task | Tipo | Detalhe |
|------|------|---------|
| 2.1 | Backend | Modelos: `WorldState`, `DistrictState`, `Landmark`, `WorldEvent` |
| 2.2 | Backend | Migration Alembic para world tables |
| 2.3 | Backend | `WorldService`: calcular energy/legacy a partir de acções e tempo |
| 2.4 | Backend | Endpoints: GET `/me/world`, GET `/me/world/districts/{id}`, POST `/me/world/events` |
| 2.5 | Backend | Pause Mode: POST `/me/pause`, GET status, auto-resume |
| 2.6 | Backend | Welcome Back: detectar `last_seen_at` > 14 dias → flag `welcome_back` |
| 2.7 | Backend | Weekly Reflection: POST `/me/reflections` com perguntas rotativas |
| 2.8 | Frontend | **World view** com ilustração 2.5D (SVG/CSS layers ou imagens estáticas por estado) |
| 2.9 | Frontend | 6 distritos clicáveis com labels (conforme mockup) |
| 2.10 | Frontend | Card "Today's Next Move" sobreposto ao mundo |
| 2.11 | Frontend | **Growth Event** (SCREEN 04): animação subtil pós-completar missão |
| 2.12 | Frontend | **Before/After** (SCREEN 05): slider comparativo |
| 2.13 | Frontend | **Controlled Decline** (SCREEN 06): estado dormant visual |
| 2.14 | Frontend | **Reawakening** (SCREEN 07): transição de retorno |
| 2.15 | Frontend | **Welcome Back** (SCREEN 08): flow sem culpa |
| 2.16 | Frontend | **Pause Mode** (SCREEN 09–10): activar/ver mundo em pausa |
| 2.17 | Frontend | **Development Map** (SCREEN 12): Legacy + Energy por distrito |
| 2.18 | Frontend | **District Detail** (SCREEN 14): história + acções recentes |
| 2.19 | Frontend | **Setback** (SCREEN 24): tentativa incompleta, opções adaptar |
| 2.20 | Frontend | **Kai + World Context** (SCREEN 20): conversa com distritos visíveis |

**Entregável:** Mundo reactivo às acções do jovem, com regressão controlada e pause mode.

---

### FASE 3 — Journeys & Maturity (2–3 semanas)

**Objectivo:** Experiências finitas, marcos permanentes, visão a longo prazo.

| Task | Tipo | Detalhe |
|------|------|---------|
| 3.1 | Backend | Modelo `Journey` (template) + `UserJourney` (instância) + milestones |
| 3.2 | Backend | 3 journeys iniciais: Find Your Direction (30d), Build Something Real (8w), Social Confidence (6w) |
| 3.3 | Backend | Landmarks: POST automático quando journey completa |
| 3.4 | Backend | Growth Timeline: GET `/me/timeline` (eventos + pauses + marcos) |
| 3.5 | Frontend | **Journey Selection** (SCREEN 15): 3 cards premium |
| 3.6 | Frontend | **Milestone / Legacy** (SCREEN 11): landmark permanente |
| 3.7 | Frontend | **Achievement** (SCREEN 23): metáfora visual (ponte, não badge) |
| 3.8 | Frontend | **Growth Timeline** (SCREEN 17): path emocional |
| 3.9 | Frontend | **Mature World** (SCREEN 19): estado após uso prolongado |
| 3.10 | Frontend | **Global World View** (SCREEN 25): zoom out icónico |
| 3.11 | Frontend | **Personalisation** (SCREEN 22): 5 estilos visuais |
| 3.12 | Frontend | **Early World** (SCREEN 18): estado inicial pós-onboarding |

**Entregável:** Experiência completa de jornada finita com legado visual acumulado.

---

### FASE 4 — Polish & Production (1–2 semanas)

| Task | Tipo | Detalhe |
|------|------|---------|
| 4.1 | Backend | Web Push production (VAPID keys, sender) |
| 4.2 | Backend | Memory/embeddings: contexto Kai enriquecido |
| 4.3 | Backend | RLS PostgreSQL (aplicar `0002_rls.sql`) |
| 4.4 | Backend | Guardian endpoints (progresso aprovado, sinais segurança) |
| 4.5 | Frontend | Animações de transição entre ecrãs |
| 4.6 | Frontend | Offline support (cache world assets) |
| 4.7 | QA | Testes E2E do core loop |
| 4.8 | QA | Teste guardrails com mensagens de crise |
| 4.9 | Design | Gerar mockups em falta (Mission, Growth, Decline, Reawakening, Milestone) |

---

## 6. Mapeamento ecrãs actuais → novos

| Ecrã actual | Destino | Acção |
|-------------|---------|-------|
| `#view-home` (Today dashboard) | **World** (SCREEN 01) | Substituir |
| `#view-coach` (Kai chat) | **Kai** (SCREEN 02) | Redesign + API |
| `#view-objectives` | **Journey** (parcial) + Mission flow | Dividir |
| `#view-journal` | **Progress** + Evidence | Integrar |
| `#onboarding-screen` | **Welcome** (mockup a1feb1f6) | Redesign |
| `#view-admin` | `/admin/index.html` | Separar |
| `#view-research` | `/admin/index.html` | Separar |
| Check-in moods | Weekly Reflection (SCREEN 16) | Evoluir |
| Streak widget | — | **Remover** |
| `#notification-card` | World overlay + push | Manter, redesign |

---

## 7. Decisões técnicas pendentes

| Decisão | Opções | Recomendação |
|---------|--------|--------------|
| Renderização do mundo | A) Imagens estáticas por estado B) SVG/CSS layers C) Canvas/WebGL | **A→B** para MVP (imagens mockup + CSS overlays) |
| Variante visual default | Pastel (e1b39fbc) vs Dark (bdd59aaa) | **Pastel** como default; dark como opção "Bold" |
| LLM provider | OpenWebUI self-hosted / OpenAI API / Anthropic | OpenWebUI (já referenciado no endpoint) |
| World state storage | JSON column vs normalised tables | **Normalised** (DistrictState table) |
| Admin console | Manter no mesmo repo ou separar | Mesmo repo, rota `/admin/` |
| Framework frontend | Vanilla JS vs lightweight (Preact) | **Vanilla** (consistente com V1, PWA simples) |

---

## 8. Métricas de sucesso por fase

| Fase | Critério de done |
|------|------------------|
| 0 | Login → onboarding → 5 tabs navegáveis em mobile |
| 1 | Kai responde (LLM) → missão criada → evidência registada → progresso visível |
| 2 | Completar missão altera energy do distrito → decline após inactividade → pause funciona |
| 3 | Journey de 30d completável → landmark permanente → timeline com 3+ eventos |
| 4 | Push notification recebida → offline world carrega → admin/research intactos |

---

## 9. Riscos

| Risco | Mitigação |
|-------|-----------|
| Mundo 3D demasiado complexo para MVP | Começar com imagens estáticas + estados CSS; evoluir depois |
| LLM sem guardrails suficientes | Manter `inspect_message` pré e pós resposta; safety cases |
| Scope creep (25 ecrãs) | Fase 1–2 cobrem 80% do valor; restantes são fase 3+ |
| Inconsistência visual | Usar mockup pastel como referência única; tokens CSS fixos |
| Backend world engine complexo | Regras simples: energy ±1 por acção; decay 1/semana inactivo |

---

## 10. Próximo passo imediato

**Iniciar Fase 0, Task 0.1:** Criar nova shell mobile com bottom navigation, usando o mockup `e1b39fbc` (pastel) como referência visual, mantendo auth funcional.

Mockups em falta a gerar antes de Fase 2:
1. Real-world Mission (SCREEN 03)
2. Action Completed / Growth (SCREEN 04)
3. Controlled Decline (SCREEN 06)
4. Reawakening (SCREEN 07)
5. Permanent Milestone (SCREEN 11)

---

## Apêndice A — Endpoints a criar (consolidado)

```
# Fase 1
GET    /me/objectives
PATCH  /me/objectives/{id}
GET    /me/missions
POST   /v1/openwebui/chat/completions  (upgrade LLM)

# Fase 2
GET    /me/world
GET    /me/world/districts/{district}
POST   /me/world/events
POST   /me/pause
GET    /me/pause
DELETE /me/pause
POST   /me/reflections
GET    /me/reflections

# Fase 3
GET    /journeys
POST   /me/journeys/{journey_id}/start
GET    /me/journeys
GET    /me/timeline
GET    /me/landmarks
PATCH  /me/world/style
```

## Apêndice B — Modelos a criar (consolidado)

```python
# Fase 2
class DistrictState:
    user_id, district, legacy_level, current_energy, last_action_at, updated_at

class Landmark:
    user_id, district, title, description, earned_at, permanent=True

class WorldEvent:
    user_id, district, event_type, before_state, after_state, trigger_id, created_at

class PausePeriod:
    user_id, reason, starts_at, ends_at, active

class Reflection:
    user_id, question, answer, choices, created_at

# Fase 3
class Journey:
    id, title, duration_days, description, milestones[]

class UserJourney:
    user_id, journey_id, started_at, status, current_milestone

class WorldStyle:
    user_id, style  # calm, bold, social, explorer, creator
```
