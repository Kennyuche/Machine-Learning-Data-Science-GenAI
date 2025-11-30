async function fetchJSON(url, opts) {
  const r = await fetch(url, opts);
  if (!r.ok) {
    let body = null;
    try { body = await r.json(); } catch (e) {}
    throw body || { error: 'Request failed', status: r.status };
  }
  return r.json();
}

let currentUser = null;

async function loadUsers() {
  const data = await fetchJSON('/api/users');
  const users = data.users || [];
  const userSelect = document.getElementById('user-select');
  const recipientSelect = document.getElementById('recipient-select');
  userSelect.innerHTML = '';
  recipientSelect.innerHTML = '';
  users.forEach(u => {
    const o = document.createElement('option'); o.value = u.id; o.textContent = u.username; userSelect.appendChild(o);
    const r = document.createElement('option'); r.value = u.id; r.textContent = u.username; recipientSelect.appendChild(r);
  });
}

async function whoami() {
  const data = await fetchJSON('/api/whoami');
  currentUser = data.user;
  updateAuthUI();
}

function updateAuthUI() {
  if (currentUser) {
    document.getElementById('login-area').style.display = 'none';
    document.getElementById('whoami').style.display = 'block';
    document.getElementById('current-user').textContent = currentUser.username + (currentUser.is_admin ? ' (admin)' : '');
    document.getElementById('give-kudos').style.display = 'block';
    // remove current user from recipient list
    const recipientSelect = document.getElementById('recipient-select');
    for (let i = recipientSelect.options.length - 1; i >= 0; i--) {
      if (recipientSelect.options[i].value == currentUser.id) recipientSelect.remove(i);
    }
  } else {
    document.getElementById('login-area').style.display = 'block';
    document.getElementById('whoami').style.display = 'none';
    document.getElementById('give-kudos').style.display = 'none';
  }
}

async function loadFeed() {
  const data = await fetchJSON('/api/kudos?limit=50');
  const list = document.getElementById('kudos-list');
  list.innerHTML = '';
  (data.kudos || []).forEach(k => {
    const el = document.createElement('div'); el.className = 'kudos-item';
    el.innerHTML = `<div class="meta"><strong>${escapeHtml(k.sender)}</strong> → <strong>${escapeHtml(k.recipient)}</strong> <span class="time">${escapeHtml(k.created_at)}</span></div><div class="msg">${escapeHtml(k.message)}</div>`;
    if (currentUser && currentUser.is_admin) {
      const controls = document.createElement('div'); controls.className = 'controls';
      const hideBtn = document.createElement('button'); hideBtn.textContent = 'Hide';
      hideBtn.onclick = async () => {
        const reason = prompt('Reason for hiding (optional)') || '';
        await fetchJSON(`/api/kudos/${k.id}/moderate`, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({action: 'hide', reason})});
        await loadFeed();
      };
      const delBtn = document.createElement('button'); delBtn.textContent = 'Delete';
      delBtn.onclick = async () => {
        if (!confirm('Delete this kudos permanently?')) return;
        await fetchJSON(`/api/kudos/${k.id}/moderate`, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({action: 'delete'})});
        await loadFeed();
      };
      controls.appendChild(hideBtn); controls.appendChild(delBtn);
      el.appendChild(controls);
    }
    list.appendChild(el);
  });
}

function escapeHtml(s) {
  if (!s) return '';
  return s.replace(/[&<>"']/g, function(c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; });
}

document.addEventListener('DOMContentLoaded', async () => {
  await loadUsers();
  await whoami();
  await loadFeed();

  document.getElementById('login-btn').onclick = async () => {
    const userId = document.getElementById('user-select').value;
    await fetchJSON('/login', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({user_id: userId})});
    await whoami();
    await loadUsers();
    await loadFeed();
  };

  document.getElementById('logout-btn').onclick = async () => {
    await fetchJSON('/logout', {method: 'POST'});
    currentUser = null; updateAuthUI();
    await loadUsers();
    await loadFeed();
  };

  document.getElementById('send-kudos').onclick = async () => {
    const recipientId = document.getElementById('recipient-select').value;
    const message = document.getElementById('message').value;
    try {
      const res = await fetchJSON('/api/kudos', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({recipient_id: recipientId, message})});
      document.getElementById('message').value = '';
      document.getElementById('kudos-feedback').textContent = 'Kudos sent!';
      setTimeout(()=>document.getElementById('kudos-feedback').textContent = '', 3000);
      await loadFeed();
    } catch (err) {
      document.getElementById('kudos-feedback').textContent = err.error || 'Error sending kudos';
    }
  };
});
