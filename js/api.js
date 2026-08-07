const API = localStorage.getItem('rise_api') || (['localhost', '127.0.0.1'].includes(location.hostname) ? 'http://localhost:8000' : '');

let session = JSON.parse(localStorage.getItem('bussola_session') || 'null');

export function getSession() { return session; }

export function setSession(data) {
  session = data;
  localStorage.setItem('bussola_session', JSON.stringify(data));
}

export function clearSession() {
  session = null;
  localStorage.removeItem('bussola_session');
}

export async function api(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (session?.access_token) headers.Authorization = `Bearer ${session.access_token}`;
  const response = await fetch(`${API}${path}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'The operation could not be completed.');
  return data;
}

export async function refreshMe() {
  const me = await api('/me');
  session.user = me;
  localStorage.setItem('bussola_session', JSON.stringify(session));
  return me;
}
