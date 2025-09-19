// CSRF helper (same pattern as other pages)
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

async function postForm(url, formData) {
  const csrftoken = getCookie('csrftoken');
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'X-CSRFToken': csrftoken },
    body: formData,
  });
  return res.json();
}

window.integrations = {
  async create() {
    const provider = document.getElementById('create-provider').value;
    const name = document.getElementById('create-name').value;
    const isActive = document.getElementById('create-active').checked ? '1' : '0';
    const config = document.getElementById('create-config').value || '{}';
    const fd = new FormData();
    fd.append('provider', provider);
    fd.append('name', name);
    fd.append('is_active', isActive);
    fd.append('config', config);
    const data = await postForm('/account/integrations/create/', fd);
    if (!data.success) {
      alert('作成失敗: ' + data.error);
    } else {
      location.reload();
    }
  },

  async update(id) {
    const row = document.querySelector(`tr[data-id="${id}"]`);
    const provider = row.querySelector('.provider').value;
    const name = row.querySelector('.name').value;
    const isActive = row.querySelector('.is_active').checked ? '1' : '0';
    // configは空欄なら送らない（現状は空でも上書きになるためここで空は送信しない）
    const cfgTextarea = row.querySelector('.config');
    const cfg = (cfgTextarea && cfgTextarea.value.trim()) || null;

    const fd = new FormData();
    fd.append('provider', provider);
    fd.append('name', name);
    fd.append('is_active', isActive);
    if (cfg) fd.append('config', cfg);
    const data = await postForm(`/account/integrations/${id}/update/`, fd);
    if (!data.success) {
      alert('更新失敗: ' + data.error);
    } else {
      alert('保存しました');
    }
  },

  async remove(id) {
    if (!confirm('削除しますか？')) return;
    const fd = new FormData();
    const data = await postForm(`/account/integrations/${id}/delete/`, fd);
    if (!data.success) {
      alert('削除失敗: ' + data.error);
    } else {
      document.querySelector(`tr[data-id="${id}"]`).remove();
    }
  },
};

// 初期化: 既存configをtextareaにプレフィル
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('tr[data-id]').forEach(row => {
    const id = row.getAttribute('data-id');
    const script = document.getElementById(`integration-config-${id}`);
    if (script) {
      try {
        const cfg = JSON.parse(script.textContent);
        const ta = row.querySelector('.config');
        if (ta) ta.value = JSON.stringify(cfg, null, 2);
      } catch (e) {
        // ignore
      }
    }
  });
});
