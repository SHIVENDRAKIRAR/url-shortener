// Config ──────────────────────────────────────────────────
const BASE_URL = 'https://url-shortener-0izm.onrender.com';

// API helper ───────────────────────────────────────────────
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
