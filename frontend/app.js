// ── Nav ──────────────────────────────────────────────────────
function initNav() {
  const token = localStorage.getItem('token');
  const navLogin = document.getElementById('nav-login');
  const navLogout = document.getElementById('nav-logout');
  const navDashboard = document.getElementById('nav-dashboard');
  const guestNote = document.getElementById('guest-note');
  const extras = document.getElementById('logged-in-extras');

  if (token) {
    if (navLogin) navLogin.style.display = 'none';
    if (navLogout) navLogout.style.display = 'inline-block';
    if (navDashboard) navDashboard.style.display = 'inline-block';
    if (guestNote) guestNote.style.display = 'none';
    if (extras) extras.style.display = 'flex';
  }
}

// ── Theme ────────────────────────────────────────────────────
function initTheme() {
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon(saved);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  updateThemeIcon(next);
}

function updateThemeIcon(theme) {
  const btn = document.querySelector('.theme-toggle');
  if (btn) btn.textContent = theme === 'light' ? '🌙' : '☀️';
}

// ── Logout ───────────────────────────────────────────────────
function logout() {
  localStorage.removeItem('token');
  window.location.href = 'index.html';
}

// ── Toast ────────────────────────────────────────────────────
function showToast(msg) {
  const t = document.createElement('div');
  t.className = 'toast';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.classList.add('toast-show'), 10);
  setTimeout(() => { t.classList.remove('toast-show'); setTimeout(() => t.remove(), 300); }, 2500);
}

// ── Error helpers ────────────────────────────────────────────
function showError(msg) {
  const box = document.getElementById('error-box');
  if (!box) return;
  box.textContent = msg;
  box.style.display = 'block';
}

function hideError() {
  const box = document.getElementById('error-box');
  if (box) box.style.display = 'none';
}

// ── Friendly error messages ──────────────────────────────────
function friendlyError(msg) {
  if (!msg) return 'Something went wrong. Try again.';
  const m = msg.toLowerCase();
  if (m.includes('429') || m.includes('too many')) return 'Too many requests. Wait a minute and try again.';
  if (m.includes('invalid') && m.includes('url')) return 'That doesn\'t look like a valid URL. Try including https://';
  if (m.includes('alias') && m.includes('taken')) return 'That alias is already taken. Try a different one.';
  if (m.includes('alias') && m.includes('reserved')) return 'That alias is reserved. Please choose another.';
  if (m.includes('login required') || m.includes('401')) return 'You need to log in to use this feature.';
  if (m.includes('not found') || m.includes('404')) return 'Short URL not found.';
  if (m.includes('expired') || m.includes('410')) return 'This link has expired.';
  if (m.includes('failed to fetch') || m.includes('networkerror')) return 'Could not connect to server. Make sure it\'s running.';
  return msg.charAt(0).toUpperCase() + msg.slice(1);
}
