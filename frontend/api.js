// ── Config ──────────────────────────────────────────────────
// Change this to your Render URL when deploying
const BASE_URL = 'http://127.0.0.1:8000';

// ── API helper ───────────────────────────────────────────────
async function api(path, method = 'GET', body = null) {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(`${BASE_URL}${path}`, opts);
  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || `Error ${res.status}`);
  }
  return data;
}
