import { api, getSession, setSession, clearSession, refreshMe } from './api.js';

const BG = {
  worldMain: 'assets/backgrounds/world-main.png',
  worldSocial: 'assets/backgrounds/world-social.png',
  worldLearning: 'assets/backgrounds/world-learning.png',
  worldAlt: 'assets/backgrounds/world-alt.png',
};

const DISTRICTS = [
  { id: 'learning', label: 'Learning', icon: '📚', top: '24%', left: '22%' },
  { id: 'self_knowledge', label: 'Self-Knowledge', icon: '🧠', top: '18%', left: '72%' },
  { id: 'social', label: 'Social', icon: '👥', top: '44%', left: '38%' },
  { id: 'creative', label: 'Creative', icon: '🎨', top: '40%', left: '78%' },
  { id: 'health', label: 'Health', icon: '💚', top: '68%', left: '18%' },
  { id: 'projects', label: 'Projects', icon: '💡', top: '64%', left: '82%' },
];

const ENERGY_LABEL = { dormant: 'Dormant', low: 'Low', medium: 'Medium', high: 'High', active: 'Active' };
const LEGACY_LABEL = { none: '—', seed: 'Seed', growing: 'Growing', established: 'Established', strong: 'Strong' };

let activeMission = null;
let deferredInstallPrompt = null;

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => [...document.querySelectorAll(sel)];

const IS_LOCAL = ['localhost', '127.0.0.1'].includes(location.hostname);

function initDemoLogin() {
  if (!IS_LOCAL) return;
  const email = $('#login-email');
  const password = $('#login-password');
  if (!email || !password) return;
  email.value = 'youth@rise.dev';
  password.value = 'RiseDemo2026!';
  const form = $('#login-form');
  if (form && !$('#demo-hint')) {
    const hint = el('p', 'muted');
    hint.id = 'demo-hint';
    hint.style.cssText = 'font-size:0.85rem;text-align:center;margin:0 0 0.75rem;';
    hint.textContent = 'Demo mode — click Sign in to continue';
    form.insertBefore(hint, form.firstChild);
  }
}

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text != null) node.textContent = text;
  return node;
}

function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }

function setActionTag(label) {
  const tag = $('#kai-action-tag');
  if (!tag) return;
  let dot = tag.querySelector('.tag-dot');
  if (!dot) {
    dot = document.createElement('span');
    dot.className = 'tag-dot';
    dot.setAttribute('aria-hidden', 'true');
  }
  clear(tag);
  tag.append(dot, document.createTextNode(label));
}

function showScreen(id) {
  $$('.screen').forEach((s) => { s.hidden = s.id !== id; });
}

function initKaiScreen() {
  const card = $('#kai-action-card');
  if (!card || card.dataset.ready) return;
  card.dataset.ready = '1';
  $('#kai-action-title').textContent = 'Share one idea in class today, even if your voice shakes.';
  setActionTag('Confidence');
  activeMission = {
    title: 'Share one idea in class',
    hypothesis: 'Build social confidence',
    action: 'Share one idea in class today, even if your voice shakes.',
    proof: 'Write one sentence about what you noticed.',
  };
  // Keep hidden if user already dismissed this session; re-shows on new Kai action
  card.hidden = sessionStorage.getItem('kai-action-dismissed') === '1';
}

const DISTRICT_META = {
  social: { label: 'Social District', hero: BG.worldSocial, badge: 'Social Confidence ↑', context: 'Social District · The Plaza' },
  learning: { label: 'Learning District', hero: BG.worldLearning, badge: 'Learning ↑', context: 'Learning District · The Academy' },
  creative: { label: 'Creative District', hero: BG.worldAlt, badge: 'Creativity ↑', context: 'Creative District · The Studios' },
  health: { label: 'Health District', hero: BG.worldMain, badge: 'Health ↑', context: 'Health District · The Park' },
  projects: { label: 'Projects District', hero: BG.worldAlt, badge: 'Projects ↑', context: 'Projects District · Innovation Row' },
  self_knowledge: { label: 'Self-Knowledge District', hero: BG.worldAlt, badge: 'Self-Knowledge ↑', context: 'Self-Knowledge District · The Observatory' },
  general: { label: 'Social District', hero: BG.worldSocial, badge: 'Growth ↑', context: 'Learning District · The Academy' },
};

function districtForMission(mission) {
  const text = `${mission.title || ''} ${mission.hypothesis || mission.why || ''} ${mission.action || ''}`.toLowerCase();
  if (/social|conversation|speak|talk|class|people|friend/.test(text)) return DISTRICT_META.social;
  if (/learn|study|read|school|classroom/.test(text)) return DISTRICT_META.learning;
  if (/creat|art|music|write/.test(text)) return DISTRICT_META.creative;
  if (/health|sleep|walk|body|run/.test(text)) return DISTRICT_META.health;
  if (/project|build|make|code/.test(text)) return DISTRICT_META.projects;
  return DISTRICT_META.general;
}

function showView(name) {
  $$('.view').forEach((v) => v.classList.toggle('active', v.id === `view-${name}`));
  $$('.nav-btn').forEach((b) => b.classList.toggle('active', b.dataset.nav === name));
  $('#app-shell')?.classList.toggle('app-shell--kai', name === 'kai');
  if (name === 'kai') initKaiScreen();
  if (name === 'journey') loadJourney();
  if (name === 'progress') loadProgress();
  if (name === 'me') loadMe();
  if (name === 'world') loadWorld();
}

function initials(name = 'R') {
  return name.trim().charAt(0).toUpperCase() || 'R';
}

async function renderDistrictPills(energyMap = {}) {
  const root = $('#world-districts');
  if (!root || root.dataset.ready) return;
  root.dataset.ready = '1';
  clear(root);
  DISTRICTS.forEach((d) => {
    const energy = energyMap[d.id]?.current_energy || 'dormant';
    const pill = el('button', 'district-pill');
    pill.type = 'button';
    pill.dataset.district = d.id;
    pill.dataset.energy = energy;
    pill.style.top = d.top;
    pill.style.left = d.left;
    pill.setAttribute('aria-label', `${d.label} district`);
    pill.append(
      el('span', 'district-pill-icon', d.icon),
      el('span', 'district-pill-label', d.label),
    );
    pill.addEventListener('click', () => showView('kai'));
    root.appendChild(pill);
  });
}

async function loadWorld() {
  let energyMap = {};
  try {
    const world = await api('/me/world');
    energyMap = world.districts || {};
  } catch { /* use defaults */ }

  const root = $('#world-districts');
  if (root) {
    if (root.dataset.ready) {
      root.querySelectorAll('.district-pill').forEach((pill) => {
        const energy = energyMap[pill.dataset.district]?.current_energy || 'dormant';
        pill.dataset.energy = energy;
      });
    } else {
      await renderDistrictPills(energyMap);
    }
  }

  try {
    const today = await api('/me/today');
    const card = $('#next-move-card');
    card.hidden = false;
    if (today.action) {
      $('#next-move-title').textContent = today.action.title;
      $('#next-move-quote').textContent = `${today.orientation.body} — Kai`;
      card.dataset.actionId = today.action.id;
      card.dataset.actionKind = today.action.kind;
      card.dataset.actionBody = today.action.body;
      card.dataset.actionProof = today.action.proof;
    } else {
      $('#next-move-title').textContent = today.orientation.title;
      $('#next-move-quote').textContent = today.orientation.body;
      card.dataset.actionId = '';
    }
  } catch {
    $('#next-move-card').hidden = false;
    $('#next-move-title').textContent = 'Spend 25 minutes on deep learning';
    $('#next-move-quote').textContent = 'Focus fuels confidence. — Kai';
  }
}

function syncKaiLayout() {
  const screen = $('#view-kai .kai-screen');
  const count = $('#kai-messages')?.children.length || 0;
  screen?.classList.toggle('kai-screen--active', count >= 3);
}

function appendMessage(role, text) {
  if (role === 'user') {
    const row = el('div', 'message-row user-row');
    row.appendChild(el('div', 'message user-message', text));
    $('#kai-messages').appendChild(row);
  } else {
    const row = el('div', 'message-row');
    const bubble = el('div', 'message kai-message');
    const meta = el('div', 'message-meta');
    meta.append(el('strong', null, 'Kai'), el('span', null, new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })));
    bubble.append(meta, document.createTextNode(text));
    const heart = el('button', 'message-heart', '♡');
    heart.type = 'button';
    heart.addEventListener('click', () => { heart.textContent = heart.textContent === '♡' ? '♥' : '♡'; });
    row.append(bubble, heart);
    $('#kai-messages').appendChild(row);
  }
  syncKaiLayout();
  $('#kai-messages').lastElementChild?.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

async function sendKaiMessage(text) {
  if (!text.trim()) return;
  appendMessage('user', text);
  $('#kai-input').value = '';
  const row = el('div', 'message-row');
  const bubble = el('div', 'message kai-message typing', '•••');
  row.appendChild(bubble);
  $('#kai-messages').appendChild(row);
  row.scrollIntoView({ behavior: 'smooth', block: 'end' });
  try {
    const res = await api('/v1/openwebui/chat/completions', { method: 'POST', body: JSON.stringify({ message: text }) });
    row.remove();
    const answer = res.choices?.[0]?.message?.content || "Let's make this concrete.";
    appendMessage('kai', answer);
    maybeShowActionCard(answer);
  } catch {
    row.remove();
    appendMessage('kai', "I couldn't respond right now. Try again.");
  }
}

function maybeShowActionCard(answer) {
  if (answer.length <= 20) return;
  // New action from Kai always surfaces the card and clears any prior dismiss
  sessionStorage.removeItem('kai-action-dismissed');
  const card = $('#kai-action-card');
  card.hidden = false;
  $('#kai-action-title').textContent = answer.length > 120 ? `${answer.slice(0, 117)}…` : answer;
  activeMission = { title: 'Kai suggested action', hypothesis: 'Build a real skill', action: answer, proof: 'Record what happened' };
}

function openMission(mission) {
  activeMission = mission;
  const district = districtForMission(mission);
  $('#mission-title').textContent = mission.title;
  $('#mission-purpose').textContent = mission.hypothesis || mission.why || 'Build a real skill';
  $('#mission-action').textContent = mission.action;
  $('#mission-district').textContent = district.label;
  $('#mission-hero-img').src = district.hero;
  $('#mission-complete').hidden = true;
  $('#mission-dialog').showModal();
}

function showGrowthOverlay(body, badge = 'Social Confidence ↑') {
  $('#growth-overlay-body').textContent = body;
  const badgeEl = document.querySelector('.growth-badge');
  if (badgeEl) badgeEl.textContent = badge;
  $('#growth-overlay').hidden = false;
}

function renderJourneyCard(item) {
  const card = el('article', 'journey-card glass');
  card.dataset.id = item.id;
  card.dataset.kind = item.kind;
  card.append(
    el('span', 'tag-pill', `${item.kind === 'mission' ? 'Mission' : 'Commitment'} · ${item.status}`),
    el('h3', null, item.title),
    el('p', null, item.action),
  );
  const btn = el('button', 'btn btn-secondary btn-sm open-mission', 'Open →');
  btn.addEventListener('click', () => openMission(item));
  card.appendChild(btn);
  return card;
}

async function loadJourney() {
  const root = $('#journey-list');
  clear(root);
  try {
    const [missions, objectives] = await Promise.all([api('/me/missions'), api('/me/objectives')]);
    const items = [
      ...missions.items.map((m) => ({ ...m, kind: 'mission' })),
      ...objectives.items.map((o) => ({ ...o, kind: 'objective', hypothesis: o.why })),
    ];
    if (!items.length) {
      root.appendChild(el('p', 'muted', 'No missions yet. Ask Kai for a challenge.'));
      return;
    }
    items.forEach((item) => root.appendChild(renderJourneyCard(item)));
  } catch {
    root.appendChild(el('p', 'muted', 'Could not load your journey.'));
  }
}

function renderStat(value, label) {
  const s = el('div', 'stat-card glass');
  s.append(el('strong', null, String(value)), el('span', null, label));
  return s;
}

async function loadProgress() {
  const statsRoot = $('#progress-stats');
  const evRoot = $('#evidence-list');
  clear(statsRoot);
  clear(evRoot);
  try {
    const [stats, evidence] = await Promise.all([api('/me/progress'), api('/me/evidence')]);
    statsRoot.append(
      renderStat(stats.missions_started, 'Missions started'),
      renderStat(stats.missions_completed, 'Completed'),
      renderStat(stats.evidence_count, 'Learnings'),
      renderStat(`${stats.completion_rate}%`, 'Completion rate'),
    );
    if (!evidence.items.length) {
      evRoot.appendChild(el('p', 'muted', 'Record your first learning below.'));
      return;
    }
    evidence.items.forEach((e) => {
      const card = el('article', 'evidence-card glass');
      card.append(
        el('span', 'tag-pill', e.competency),
        el('p', null, e.statement),
        el('small', null, new Date(e.created_at).toLocaleDateString('en-GB')),
      );
      evRoot.appendChild(card);
    });
  } catch (e) {
    console.debug('progress', e);
  }
}

async function loadMe() {
  const me = getSession()?.user;
  if (!me) return;
  $('#me-name').textContent = me.display_name || me.onboarding?.preferred_name || 'Profile';
  $('#me-email').textContent = me.email;
  const avatarImg = $('#world-avatar-img');
  if (avatarImg) avatarImg.alt = me.display_name || 'Profile';
  const map = $('#me-districts');
  clear(map);
  try {
    const world = await api('/me/world');
    map.appendChild(el('h3', null, 'Development map'));
    DISTRICTS.forEach((d) => {
      const s = world.districts[d.id];
      const row = el('div', 'district-row');
      row.append(
        el('span', null, `${d.icon} ${d.label}`),
        el('span', null, `Legacy: ${LEGACY_LABEL[s.legacy_level]}`),
        el('span', null, `Energy: ${ENERGY_LABEL[s.current_energy]}`),
      );
      map.appendChild(row);
    });
  } catch (_) { /* optional */ }
}

function showGrowthToast(title, body) {
  $('#growth-title').textContent = title;
  $('#growth-body').textContent = body;
  const t = $('#growth-toast');
  t.hidden = false;
  setTimeout(() => { t.hidden = true; }, 4000);
}

$('#growth-see-changes')?.addEventListener('click', () => {
  $('#growth-overlay').hidden = true;
  showView('world');
  loadWorld();
});

async function enterApp(me) {
  showScreen(null);
  $('#app-shell').hidden = false;
  const avatarImg = $('#world-avatar-img');
  if (avatarImg) avatarImg.alt = me.display_name || 'Profile';
  if (me.onboarding_status !== 'complete' && me.role === 'youth') {
    $('#welcome-screen').hidden = false;
    return;
  }
  showView('world');
  loadWorld();
  if (me.role === 'youth') requestNotificationPermission();
}

async function startSession(data) {
  setSession(data);
  const me = await refreshMe();
  await enterApp(me);
}

async function requestNotificationPermission() {
  if ('Notification' in window && Notification.permission === 'default') await Notification.requestPermission();
}

$('#login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  $('#login-error').textContent = '';
  try {
    await startSession(await api('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email: $('#login-email').value, password: $('#login-password').value }),
    }));
  } catch (err) {
    $('#login-error').textContent = err.message;
  }
});

$('#register-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    await startSession(await api('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        display_name: $('#register-name').value,
        email: $('#register-email').value,
        password: $('#register-password').value,
        tenant_name: $('#register-tenant').value || null,
      }),
    }));
  } catch (err) {
    $('#login-error').textContent = err.message;
  }
});

$('#welcome-start').addEventListener('click', () => {
  $('#welcome-screen').hidden = true;
  $('#onboarding-screen').hidden = false;
});

document.getElementById('welcome-explore')?.addEventListener('click', () => {
  $('#welcome-screen').hidden = true;
  showView('world');
  loadWorld();
});

$('#onboarding-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const f = new FormData(e.currentTarget);
  try {
    await api('/me/onboarding', {
      method: 'PATCH',
      body: JSON.stringify({
        preferred_name: f.get('preferred_name'),
        energy_areas: String(f.get('energy') || '').split(',').map((x) => x.trim()).filter(Boolean),
        current_difficulties: String(f.get('difficulty') || '').split(',').map((x) => x.trim()).filter(Boolean),
        challenge_intensity: f.get('challenge_intensity'),
        proactive_consent: f.has('proactive_consent'),
        research_consent: f.has('research_consent'),
        service_terms: f.has('terms'),
        youth_assent: f.has('terms'),
      }),
    });
    $('#onboarding-screen').hidden = true;
    await refreshMe();
    showView('world');
    loadWorld();
  } catch (err) {
    alert(err.message);
  }
});

$$('[data-nav]').forEach((node) => node.addEventListener('click', () => showView(node.dataset.nav)));
$('#bottom-nav').addEventListener('click', (e) => {
  const btn = e.target.closest('.nav-btn');
  if (btn) showView(btn.dataset.nav);
});

$('#kai-form').addEventListener('submit', (e) => { e.preventDefault(); sendKaiMessage($('#kai-input').value); });

$('#kai-chips').addEventListener('click', (e) => {
  const chip = e.target.closest('[data-chip]');
  if (!chip) return;
  const prompts = {
    challenge: 'Give me a small challenge for today.',
    easier: 'That feels like too much. Make it easier.',
    'not-today': "I can't today. Is that okay?",
    talk: 'I need to talk this through.',
  };
  sendKaiMessage(prompts[chip.dataset.chip]);
});

$('#kai-action-open').addEventListener('click', () => { if (activeMission) openMission(activeMission); });

$('#kai-action-dismiss').addEventListener('click', () => {
  const card = $('#kai-action-card');
  card.hidden = true;
  sessionStorage.setItem('kai-action-dismissed', '1');
});

$('#next-move-go').addEventListener('click', () => {
  const card = $('#next-move-card');
  if (card.dataset.actionId) {
    openMission({
      id: card.dataset.actionId,
      title: $('#next-move-title').textContent,
      hypothesis: 'Active commitment',
      action: card.dataset.actionBody || $('#next-move-title').textContent,
      proof: card.dataset.actionProof || 'Record what you did',
      kind: card.dataset.actionKind,
    });
  } else {
    showView('kai');
  }
});

$('#mission-close').addEventListener('click', () => $('#mission-dialog').close());
$('#mission-difficulty').addEventListener('click', (e) => {
  const pill = e.target.closest('.diff-pill');
  if (!pill) return;
  $$('.diff-pill').forEach((p) => p.classList.remove('active'));
  pill.classList.add('active');
});

$('#mission-accept').addEventListener('click', () => { $('#mission-complete').hidden = false; });
$('#mission-easier').addEventListener('click', () => {
  showView('kai');
  sendKaiMessage('Make this mission easier.');
  $('#mission-dialog').close();
});

$('#mission-done').addEventListener('click', async () => {
  const learning = $('#mission-learning').value.trim();
  if (!learning) return alert('Write what you learned.');
  try {
    if (activeMission?.id && activeMission?.kind !== 'objective') {
      await api(`/me/missions/${activeMission.id}/feedback`, { method: 'POST', body: JSON.stringify({ learning, status: 'completed' }) });
    }
    await api('/me/evidence', { method: 'POST', body: JSON.stringify({ competency: 'general', statement: learning, confidence: 0.7 }) });
    $('#mission-dialog').close();
    const district = districtForMission(activeMission || {});
    showGrowthOverlay('You started a conversation even though it felt uncomfortable.', district.badge);
    showGrowthToast('You showed up.', 'A real action brought life to your world.');
    loadWorld();
    loadProgress();
  } catch (e) {
    alert(e.message);
  }
});

$('#add-mission-btn').addEventListener('click', async () => {
  const title = prompt('Mission title');
  if (!title) return;
  const action = prompt('Concrete action') || title;
  try {
    await api('/me/missions', { method: 'POST', body: JSON.stringify({ title, hypothesis: 'Test something real', action, proof: 'Written record' }) });
    loadJourney();
  } catch (e) { alert(e.message); }
});

$('#reflect-save').addEventListener('click', async () => {
  const statement = $('#reflect-text').value.trim();
  const competency = $('#reflect-competency').value.trim() || 'reflection';
  if (!statement) return;
  try {
    await api('/me/evidence', { method: 'POST', body: JSON.stringify({ competency, statement, confidence: 0.6 }) });
    $('#reflect-text').value = '';
    $('#reflect-status').textContent = 'Reflection saved ✓';
    loadProgress();
    loadWorld();
  } catch (e) { $('#reflect-status').textContent = e.message; }
});

$('#logout-button').addEventListener('click', async () => {
  try {
    const s = getSession();
    if (s?.refresh_token) await api('/auth/logout', { method: 'POST', body: JSON.stringify({ refresh_token: s.refresh_token }) });
  } catch (_) {}
  clearSession();
  $('#app-shell').hidden = true;
  showScreen('auth-screen');
  if (IS_LOCAL) initDemoLogin();
  else $('#login-password').value = '';
});

window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferredInstallPrompt = e; });
$('#install-pwa').addEventListener('click', async () => {
  if (deferredInstallPrompt) { deferredInstallPrompt.prompt(); await deferredInstallPrompt.userChoice; return; }
  alert('On iPhone: Safari → Share → Add to Home Screen.');
});

if ('serviceWorker' in navigator) window.addEventListener('load', () => navigator.serviceWorker.register('sw.js'));

initDemoLogin();

const existing = getSession();
if (existing?.access_token && existing.user) enterApp(existing.user);
else showScreen('auth-screen');

appendMessage('kai', "You said speaking up in class still feels harder than it should.");
setTimeout(() => appendMessage('kai', 'Want to try something small today?'), 400);
