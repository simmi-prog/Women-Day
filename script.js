/* ──────────────────────────────────────────────────────────
   CONFIGURATION — Replace these two values with your own
   ────────────────────────────────────────────────────────── */
const FORM_BASE_URL = 'https://docs.google.com/forms/d/e/1FAIpQLScu22zeFoxvFXUr7r0SvDOKauAYb7Stu0YwpnS0qi4YIIYAXg/viewform?usp=header';   // e.g. "https://docs.google.com/forms/d/e/XXXXX/viewform"
const ENTRY_ID      = '713405156';         // e.g. "1234567890"
/* ────────────────────────────────────────────────────────── */

const GRADIENTS = 8; // number of .grad-N classes in CSS

const grid        = document.getElementById('card-grid');
const searchInput = document.getElementById('search');
const teamFilter  = document.getElementById('team-filter');
const toastBox    = document.getElementById('toast-container');

let allWomen = [];

// Clipboard SVG icon (inline to avoid external dependencies)
const COPY_ICON = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`;

/* ── Helpers ──────────────────────────────────────────────── */

function getInitials(name) {
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0][0].toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function gradClass(name) {
  let hash = 0;
  for (const ch of name) hash = (hash * 31 + ch.charCodeAt(0)) | 0;
  return 'grad-' + (Math.abs(hash) % GRADIENTS);
}

function buildFormURL(name) {
  return `${FORM_BASE_URL}?usp=pp_url&entry.${ENTRY_ID}=${encodeURIComponent(name)}`;
}

/* ── Toast ────────────────────────────────────────────────── */

function showToast(msg) {
  const el = document.createElement('div');
  el.className = 'toast';
  el.textContent = msg;
  toastBox.appendChild(el);
  setTimeout(() => el.remove(), 2200);
}

/* ── Card rendering ──────────────────────────────────────── */

function createCard(woman) {
  const url = buildFormURL(woman.name);

  const card = document.createElement('a');
  card.className = 'card';
  card.href = url;
  card.target = '_blank';
  card.rel = 'noopener noreferrer';
  card.setAttribute('aria-label', `Appreciate ${woman.name}`);

  // Copy-link button
  const copyBtn = document.createElement('button');
  copyBtn.className = 'copy-btn';
  copyBtn.setAttribute('aria-label', `Copy appreciation link for ${woman.name}`);
  copyBtn.innerHTML = COPY_ICON;
  copyBtn.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    navigator.clipboard.writeText(url).then(() => {
      showToast('Link copied!');
    }).catch(() => {
      showToast('Could not copy link');
    });
  });
  card.appendChild(copyBtn);

  // Avatar
  const avatarWrap = document.createElement('div');
  avatarWrap.className = 'avatar-wrap';

  if (woman.img) {
    const img = document.createElement('img');
    img.src = woman.img;
    img.alt = woman.name;
    img.loading = 'lazy';
    img.onerror = function () {
      this.remove();
      avatarWrap.appendChild(makeInitialsEl(woman.name));
    };
    avatarWrap.appendChild(img);
  } else {
    avatarWrap.appendChild(makeInitialsEl(woman.name));
  }

  card.appendChild(avatarWrap);

  // Name
  const nameEl = document.createElement('div');
  nameEl.className = 'card-name';
  nameEl.textContent = woman.name;
  card.appendChild(nameEl);

  // Team (optional)
  if (woman.team) {
    const teamEl = document.createElement('div');
    teamEl.className = 'card-team';
    teamEl.textContent = woman.team;
    card.appendChild(teamEl);
  }

  return card;
}

function makeInitialsEl(name) {
  const span = document.createElement('span');
  span.className = `avatar-initials ${gradClass(name)}`;
  span.textContent = getInitials(name);
  span.setAttribute('aria-hidden', 'true');
  return span;
}

/* ── Filtering & rendering ───────────────────────────────── */

function render() {
  const query = searchInput.value.trim().toLowerCase();
  const team  = teamFilter.value;

  const filtered = allWomen.filter((w) => {
    const matchesName = w.name.toLowerCase().includes(query);
    const matchesTeam = !team || w.team === team;
    return matchesName && matchesTeam;
  });

  grid.innerHTML = '';

  if (filtered.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'empty-state';
    empty.textContent = 'No results found.';
    grid.appendChild(empty);
    return;
  }

  const fragment = document.createDocumentFragment();
  filtered.forEach((w) => fragment.appendChild(createCard(w)));
  grid.appendChild(fragment);
}

/* ── Team dropdown setup ─────────────────────────────────── */

function setupTeamFilter() {
  const teams = [...new Set(allWomen.map((w) => w.team).filter(Boolean))].sort();
  if (teams.length === 0) return;

  teamFilter.hidden = false;
  teams.forEach((t) => {
    const opt = document.createElement('option');
    opt.value = t;
    opt.textContent = t;
    teamFilter.appendChild(opt);
  });
}

/* ── Init ─────────────────────────────────────────────────── */

async function init() {
  try {
    const res = await fetch('women.json');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    allWomen = await res.json();
  } catch (err) {
    grid.innerHTML = `<div class="empty-state">Could not load data. Make sure <code>women.json</code> is in the same folder.</div>`;
    console.error('Failed to load women.json:', err);
    return;
  }

  allWomen.sort((a, b) => a.name.localeCompare(b.name));

  setupTeamFilter();
  render();

  searchInput.addEventListener('input', render);
  teamFilter.addEventListener('change', render);
}

document.addEventListener('DOMContentLoaded', init);
