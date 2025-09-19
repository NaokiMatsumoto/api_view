(function(){
  function getCookie(name){
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? decodeURIComponent(m.pop()) : '';
  }
  const csrftoken = getCookie('csrftoken');
  function csrfHeaders(){
    return { 'X-CSRFToken': csrftoken };
  }

  const container = document.querySelector('[data-template-id]');
  if(!container) return;
  const templateId = container.getAttribute('data-template-id');

  const addForm = document.querySelector('[data-role="task-template-add-form"]');
  const listEl = document.querySelector('[data-role="task-template-list"]');

  function renderRow(item){
    const li = document.createElement('li');
    li.className = 'flex items-start gap-3 border-b py-3';
    li.setAttribute('data-task-template-id', item.id);
    // no order/draggable
    li.innerHTML = `
  <div class="mt-1 text-gray-300 select-none">•</div>
      <div class="flex-1 min-w-0">
        <div class="flex justify-between items-start">
          <div>
            <div class="font-medium text-gray-900" data-role="name">${item.name}</div>
            <div class="text-xs text-gray-500 mt-0.5" data-role="when">${item.when_display}</div>
          </div>
          <div class="shrink-0 flex items-center gap-2">
            <button class="px-2 py-1 text-xs border rounded" data-role="edit">編集</button>
            <button class="px-2 py-1 text-xs border rounded text-red-600" data-role="delete">削除</button>
          </div>
        </div>
        <div class="hidden mt-2" data-role="edit-form">
          <div class="flex flex-wrap items-end gap-2">
            <input type="text" class="px-2 py-1 border rounded w-56" data-field="name" maxlength="200" placeholder="タスク名" value="${item.name}">
            <input type="number" class="px-2 py-1 border rounded w-28" data-field="relative_days_before" placeholder="開催◯日前" value="${item.relative_days_before ?? ''}">
            <input type="text" class="px-2 py-1 border rounded w-40" data-field="default_assignee" placeholder="担当" value="${item.default_assignee ?? ''}">
            <input type="text" class="px-2 py-1 border rounded flex-1" data-field="default_notes" placeholder="メモ" value="${(item.default_notes || '').replace(/"/g,'&quot;')}">
            <button class="px-3 py-1 text-xs bg-primary-600 text-white rounded" data-role="save">保存</button>
            <button class="px-3 py-1 text-xs border rounded" data-role="cancel">キャンセル</button>
            <span class="text-xs text-red-600" data-role="error" style="display:none"></span>
          </div>
        </div>
      </div>`;
    bindRow(li);
    return li;
  }

  function bindRow(row){
    const editBtn = row.querySelector('[data-role="edit"]');
    const delBtn = row.querySelector('[data-role="delete"]');
    const form = row.querySelector('[data-role="edit-form"]');
    const saveBtn = row.querySelector('[data-role="save"]');
    const cancelBtn = row.querySelector('[data-role="cancel"]');

    editBtn.addEventListener('click', ()=>{
      form.classList.toggle('hidden');
    });
    cancelBtn.addEventListener('click', ()=>{
      form.classList.add('hidden');
    });

    saveBtn.addEventListener('click', async ()=>{
      const id = row.getAttribute('data-task-template-id');
      const payload = new URLSearchParams();
      form.querySelectorAll('[data-field]').forEach(inp=>{
        payload.append(inp.getAttribute('data-field'), inp.value);
      });
      try{
        const res = await fetch(`/seminars/templates/tasks/${id}/update-ajax/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded', ...csrfHeaders() },
          body: payload.toString()
        });
        const data = await res.json();
        if(!data.success){
          const err = form.querySelector('[data-role="error"]');
          err.style.display = '';
          err.textContent = Object.values(data.errors||{_:'更新に失敗しました'})[0];
          return;
        }
        row.querySelector('[data-role="name"]').textContent = data.name;
        row.querySelector('[data-role="when"]').textContent = data.when_display;
        form.classList.add('hidden');
      }catch(e){
        alert('通信に失敗しました');
      }
    });

    delBtn.addEventListener('click', async ()=>{
      if(!confirm('削除しますか？')) return;
      const id = row.getAttribute('data-task-template-id');
      try{
        const res = await fetch(`/seminars/templates/tasks/${id}/delete-ajax/`, {
          method: 'POST',
          headers: csrfHeaders()
        });
        const data = await res.json();
        if(data.success){
          row.remove();
        }
      }catch(e){
        alert('通信に失敗しました');
      }
    });
  }

  if(addForm){
    const nameEl = addForm.querySelector('[data-field="name"]');
    const rdbEl = addForm.querySelector('[data-field="relative_days_before"]');
    const assEl = addForm.querySelector('[data-field="default_assignee"]');
    const notesEl = addForm.querySelector('[data-field="default_notes"]');
    const errEl = addForm.querySelector('[data-role="error"]');
    const btn = addForm.querySelector('[data-role="add"]');

    btn.addEventListener('click', async ()=>{
      errEl.style.display = 'none';
      const payload = new URLSearchParams();
      payload.append('name', nameEl.value.trim());
      if(rdbEl.value) payload.append('relative_days_before', rdbEl.value);
  // fixed_date は廃止
      if(assEl.value) payload.append('default_assignee', assEl.value);
      if(notesEl.value) payload.append('default_notes', notesEl.value);
      try{
        const res = await fetch(`/seminars/templates/${templateId}/tasks/create-ajax/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded', ...csrfHeaders() },
          body: payload.toString()
        });
        const data = await res.json();
        if(!data.success){
          errEl.style.display = '';
          errEl.textContent = Object.values(data.errors||{_:'追加に失敗しました'})[0];
          return;
        }
        const row = renderRow(data);
        listEl.appendChild(row);
        nameEl.value = '';
        rdbEl.value = '';
  // fixed_date は廃止
        assEl.value = '';
        notesEl.value = '';
      }catch(e){
        errEl.style.display = '';
        errEl.textContent = '通信に失敗しました';
      }
    });
  }

  // 既存行にハンドラを付与
  if(listEl){
    Array.from(listEl.querySelectorAll('li')).forEach(li => {
      bindRow(li);
    });
  }
  // 並び替えは未対応（要望により削除）
})();
