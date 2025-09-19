(function($){
  'use strict';

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }

  const csrftoken = getCookie('csrftoken');

  $(document).ready(function() {
    const storageKey = 'seminar_detail_open_dates';

    const calendarScript = document.getElementById('seminar-calendar-data');
    let calendarEvents = [];
    if (calendarScript && calendarScript.textContent) {
      try {
        calendarEvents = JSON.parse(calendarScript.textContent);
      } catch (error) {
        console.warn('Failed to parse calendar data', error);
      }
    }

    const calendarRoot = document.querySelector('[data-calendar-root]');
    const calendarGrid = calendarRoot ? calendarRoot.querySelector('[data-calendar-grid]') : null;
    const calendarLabel = document.querySelector('[data-calendar-label]');
    const calendarPrev = document.querySelector('.calendar-nav-prev');
    const calendarNext = document.querySelector('.calendar-nav-next');

    const eventMap = new Map();
    calendarEvents.forEach((event) => {
      eventMap.set(event.date, event);
    });

    const todayDate = new Date();
    const initialDate = (() => {
      if (calendarEvents.length === 0) {
        return new Date(todayDate.getFullYear(), todayDate.getMonth(), 1);
      }
      const sortable = calendarEvents
        .map((event) => event.date)
        .sort();
      const focus = sortable.find((d) => d >= todayDate.toISOString().slice(0, 10)) || sortable[0];
      const [year, month] = focus.split('-').map(Number);
      return new Date(year, month - 1, 1);
    })();

    let currentMonth = initialDate;

    function formatMonthLabel(dateObj) {
      const year = dateObj.getFullYear();
      const month = dateObj.getMonth() + 1;
      return `${year}年${String(month).padStart(2, '0')}月`;
    }

    function buildCell(dateObj, inCurrentMonth) {
      const iso = dateObj.toISOString().slice(0, 10);
      const event = eventMap.get(iso);
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'relative rounded-lg border px-2 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-400 transition';
      button.dataset.date = iso;

      if (!inCurrentMonth) {
        button.classList.add('border-transparent', 'text-gray-300', 'hover:bg-gray-50');
      } else {
        button.classList.add('border-gray-200', 'hover:border-primary-300', 'hover:bg-primary-50/50');
      }

      if (iso === todayDate.toISOString().slice(0, 10)) {
        button.classList.add('ring-2', 'ring-primary-300');
      }

      const daySpan = document.createElement('span');
      daySpan.textContent = String(dateObj.getDate());
      daySpan.className = 'block text-sm font-medium';
      button.appendChild(daySpan);

      if (event) {
        const dot = document.createElement('span');
        dot.className = 'absolute top-1 right-1 inline-flex items-center justify-center w-2.5 h-2.5 rounded-full';
        if (event.overdue > 0) {
          dot.classList.add('bg-red-500');
        } else if (event.completed >= event.total) {
          dot.classList.add('bg-gray-300');
        } else {
          dot.classList.add('bg-primary-500');
        }
        button.appendChild(dot);

        const count = document.createElement('span');
        count.className = 'mt-2 block text-[11px] text-gray-500';
        count.textContent = `${event.completed}/${event.total}`;
        button.appendChild(count);
      }

      return button;
    }

    function renderCalendar(monthDate) {
      if (!calendarRoot || !calendarGrid || !calendarLabel) {
        return;
      }

      calendarGrid.innerHTML = '';
      const year = monthDate.getFullYear();
      const month = monthDate.getMonth();
      const firstDay = new Date(year, month, 1);
      const startOffset = firstDay.getDay();
      const gridStart = new Date(year, month, 1 - startOffset);

      for (let i = 0; i < 42; i += 1) {
        const cellDate = new Date(gridStart.getFullYear(), gridStart.getMonth(), gridStart.getDate() + i);
        const inCurrentMonth = cellDate.getMonth() === month;
        const cell = buildCell(cellDate, inCurrentMonth);
        calendarGrid.appendChild(cell);
      }

      calendarLabel.textContent = formatMonthLabel(monthDate);
      const emptyMessage = calendarGrid.querySelector('[data-calendar-empty]');
      if (emptyMessage) {
        emptyMessage.remove();
      }
    }

    function scrollToDateSection(dateIso) {
      const target = document.querySelector(`[data-date-key="${dateIso}"]`);
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        target.classList.add('ring-2', 'ring-primary-400', 'ring-offset-2');
        setTimeout(() => {
          target.classList.remove('ring-2', 'ring-primary-400', 'ring-offset-2');
        }, 1000);
      }
    }

    if (calendarRoot && calendarGrid && calendarLabel) {
      renderCalendar(currentMonth);

      if (calendarPrev) {
        calendarPrev.addEventListener('click', () => {
          currentMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1);
          renderCalendar(currentMonth);
        });
      }

      if (calendarNext) {
        calendarNext.addEventListener('click', () => {
          currentMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1);
          renderCalendar(currentMonth);
        });
      }

      calendarGrid.addEventListener('click', (event) => {
        const button = event.target.closest('button[data-date]');
        if (!button) {
          return;
        }
        const selected = calendarGrid.querySelector('button[data-date].border-primary-400');
        if (selected) {
          selected.classList.remove('border-primary-400', 'bg-primary-50');
        }
        button.classList.add('border-primary-400', 'bg-primary-50');
        const dateIso = button.dataset.date;
        scrollToDateSection(dateIso);
      });
    }

    function loadOpenSet() {
      try {
        const raw = localStorage.getItem(storageKey);
        const arr = raw ? JSON.parse(raw) : [];
        return new Set(Array.isArray(arr) ? arr : []);
      } catch { return new Set(); }
    }

    function saveOpenSet(set) {
      try {
        localStorage.setItem(storageKey, JSON.stringify(Array.from(set)));
      } catch {}
    }

  const openSet = loadOpenSet();

  // 初期表示は常に全て閉じた状態にする（以前の開閉状態は反映しない）
  $('[data-accordion-panel]').attr('hidden', true);
  $('.date-group-toggle').removeClass('open');

    function ensureDateGroup(dateKey, deadlineDisplay, relativeText) {
      let $group = $(`[data-date-key="${dateKey}"]`).last();
      if ($group.length) {
        return $group;
      }

      const groupHtml = `
        <div class="border border-gray-200 rounded-lg overflow-hidden" data-date-key="${dateKey}">
          <button type="button" class="date-group-toggle group w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100">
            <div class="flex items-center gap-3">
              <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
              <span class="font-semibold text-gray-900">${deadlineDisplay}</span>
              <span class="text-xs text-gray-500">（${relativeText}）</span>
            </div>
            <div class="flex items-center gap-2 text-sm">
              <span class="px-2 py-0.5 bg-green-100 text-green-700 rounded" data-role="group-completed">完了 0/0</span>
              <span class="px-2 py-0.5 bg-red-100 text-red-700 rounded" data-role="group-overdue" style="display:none">期限超過 0</span>
              <svg class="w-4 h-4 text-gray-400 group-[.open]:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>
          </button>
          <div class="divide-y" data-accordion-panel hidden></div>
        </div>`;

      const $list = $('#task-list');
      let inserted = false;
      $list.children('[data-date-key]').each(function(){
        const cur = $(this).data('date-key');
        if (!inserted && cur > dateKey) {
          $(this).before(groupHtml);
          inserted = true;
        }
      });
      if (!inserted) {
        $list.append(groupHtml);
      }
      return $(`[data-date-key="${dateKey}"]`).last();
    }

    function removeEmptyGroup($group, dateKey) {
      const $panel = $group.find('[data-accordion-panel]');
      if ($panel.children('.task-item').length > 0) {
        return;
      }

      const raw = localStorage.getItem(storageKey);
      if (raw) {
        try {
          const arr = JSON.parse(raw) || [];
          const set = new Set(arr);
          set.delete(dateKey);
          localStorage.setItem(storageKey, JSON.stringify(Array.from(set)));
        } catch {}
      }

      $group.remove();
    }

    // Accordion toggle per date group
    $(document).on('click', '.date-group-toggle', function(){
      const $toggle = $(this);
      const $container = $toggle.closest('[data-date-key]');
      const key = $container.data('date-key');
      const panel = $toggle.next('[data-accordion-panel]');
      if (!panel.length) return;
      const isHidden = panel.attr('hidden') !== undefined;
      if (isHidden) {
        panel.removeAttr('hidden');
        $toggle.addClass('open');
        if (key) { openSet.add(key); saveOpenSet(openSet); }
      } else {
        panel.attr('hidden', true);
        $toggle.removeClass('open');
        if (key) { openSet.delete(key); saveOpenSet(openSet); }
      }
    });

    // Task row click toggles checkbox (but ignore direct control clicks)
    $(document).on('click', '.task-item', function(e){
  if ($(e.target).is('input, label, a, button, svg, path, .task-edit-name, .task-edit-deadline')) return;
      const checkbox = $(this).find('.task-checkbox');
      if (checkbox.length === 0) return;
      const newState = !checkbox.prop('checked');
      checkbox.prop('checked', newState).trigger('change');
    });

    // Task toggle via Ajax
    $(document).on('change', '.task-checkbox', function() {
      const $cb = $(this);
      const taskId = $cb.data('task-id');
      const isCompleted = $cb.is(':checked');
      const taskItem = $cb.closest('.task-item');
      const taskTitle = taskItem.find('h4');
      const taskDescription = taskItem.find('p').first();

      // loading state
      $cb.prop('disabled', true);

      $.ajax({
        url: `/seminars/tasks/${taskId}/toggle-ajax/`,
        method: 'POST',
        headers: csrftoken ? { 'X-CSRFToken': csrftoken } : {},
        data: {
          task_id: taskId,
          is_completed: isCompleted
        },
        success: function(response) {
          if (response && response.success) {
            // Update styles
            taskItem.removeClass('task-completed task-pending task-overdue');
            if (isCompleted) {
              taskItem.addClass('task-completed');
              taskTitle.addClass('line-through');
              taskDescription.addClass('line-through');
            } else {
              if (response.is_overdue) {
                taskItem.addClass('task-overdue');
              } else {
                taskItem.addClass('task-pending');
              }
              taskTitle.removeClass('line-through');
              taskDescription.removeClass('line-through');
            }

            // Tiny animation
            taskItem.addClass('animate-pulse');
            setTimeout(() => taskItem.removeClass('animate-pulse'), 500);

            const $group = taskItem.closest('[data-date-key]');
            updateGroupCounts($group);
            updateGlobalProgress();
          } else {
            alert('エラーが発生しました: ' + ((response && response.error) || '不明なエラー'));
            $cb.prop('checked', !isCompleted);
          }
        },
        error: function(xhr, status, error) {
          console.error('Ajax error:', error);
          alert('通信エラーが発生しました。再度お試しください。');
          $cb.prop('checked', !isCompleted);
        },
        complete: function() {
          $cb.prop('disabled', false);
        }
      });
    });

    // -------- Inline Edit: start/cancel/save --------
    $(document).on('click', '.task-edit-start', function(e){
      e.stopPropagation();
      const $item = $(this).closest('.task-item');
      $item.addClass('editing');
      $item.find('.task-edit-form').removeClass('hidden');
    });

    $(document).on('click', '.task-edit-cancel', function(e){
      e.stopPropagation();
      const $item = $(this).closest('.task-item');
      $item.removeClass('editing');
      $item.find('.task-edit-form').addClass('hidden');
      const $err = $item.find('.task-edit-error');
      $err.text('').hide();
    });

    $(document).on('click', '.task-edit-save', function(e){
      e.stopPropagation();
      const $btn = $(this);
      const $item = $btn.closest('.task-item');
      const id = $item.data('task-id');
      const name = ($item.find('.task-edit-name').val() || '').toString().trim();
      const deadline = ($item.find('.task-edit-deadline').val() || '').toString().trim();
      const $err = $item.find('.task-edit-error');

      if (!name) { $err.text('タスク名を入力してください').show(); return; }
      if (!/\d{4}-\d{2}-\d{2}/.test(deadline)) { $err.text('有効な日付(YYYY-MM-DD)を入力してください').show(); return; }

      $err.text('').hide();
      $btn.prop('disabled', true);

      $.ajax({
        url: `/seminars/tasks/${id}/update-ajax/`,
        method: 'POST',
        headers: csrftoken ? { 'X-CSRFToken': csrftoken } : {},
        data: { name, deadline },
        success: function(res){
          if (!res || !res.success) {
            const msg = (res && res.errors && (res.errors.name || res.errors.deadline)) || (res && res.error) || '更新に失敗しました';
            $err.text(msg).show();
            return;
          }

          // 文字列の更新
          const $title = $item.find('h4');
          $title.text(res.name);

          // 日付グループの移動が必要か確認
          const $group = $item.closest('[data-date-key]');
          const oldKey = $group.data('date-key');
          const newKey = res.date_key;
          if (oldKey !== newKey) {
            const $oldGroup = $group;
            $item.detach();
            const $newGroup = ensureDateGroup(newKey, res.deadline_display, res.relative_text);
            $newGroup.find('[data-accordion-panel]').append($item);
            removeEmptyGroup($oldGroup, oldKey);
            if ($oldGroup.closest('body').length) {
              updateGroupCounts($oldGroup);
            }
          }

          updateGroupCounts($item.closest('[data-date-key]'));

          // 期限超過の見た目更新（完了は変えない）
          $item.removeClass('task-overdue task-pending task-completed');
          const isChecked = $item.find('.task-checkbox').is(':checked');
          if (isChecked) {
            $item.addClass('task-completed');
          } else if (res.is_overdue) {
            $item.addClass('task-overdue');
          } else {
            $item.addClass('task-pending');
          }

          // グローバル進捗更新
          updateGlobalProgress();

          // UI終了
          $item.removeClass('editing');
          $item.find('.task-edit-form').addClass('hidden');
          $item.addClass('animate-pulse');
          setTimeout(() => $item.removeClass('animate-pulse'), 400);
        },
        error: function(xhr){
          let msg = '通信エラーが発生しました';
          if (xhr && xhr.responseJSON && xhr.responseJSON.errors) {
            const er = xhr.responseJSON.errors;
            msg = er.name || er.deadline || xhr.responseJSON.error || msg;
          }
          $err.text(msg).show();
        },
        complete: function(){
          $btn.prop('disabled', false);
        }
      });
    });

    function updateGroupCounts($group){
      if (!$group || $group.length === 0) return;
      const totalInGroup = $group.find('.task-item').length;
      const completedInGroup = $group.find('.task-item .task-checkbox:checked').length;
      let overdueInGroup = 0;
      $group.find('.task-item').each(function(){
        const $ti = $(this);
        const done = $ti.find('.task-checkbox').is(':checked');
        const over = $ti.hasClass('task-overdue');
        if (!done && over) overdueInGroup += 1;
      });
      const $groupCompleted = $group.find('[data-role="group-completed"]');
      const $groupOverdue = $group.find('[data-role="group-overdue"]');
      $groupCompleted.text(`完了 ${completedInGroup}/${totalInGroup}`);
      if (overdueInGroup > 0) { $groupOverdue.text(`期限超過 ${overdueInGroup}`).show(); }
      else { $groupOverdue.hide(); }
    }

    function updateGlobalProgress(){
      const $all = $('.task-item .task-checkbox');
      const total = $all.length;
      const done = $all.filter(':checked').length;
      const percent = total > 0 ? Math.round((done * 100) / total) : 0;
      $('[data-role="global-progress-count"]').text(`${done}/${total}${total>0?` (${percent}%)`:''}`);
      $('[data-role="global-progress-bar"]').css('width', `${percent}%`);
    }

    // -------- Create Task (top form) --------
    $(document).on('click', '.add-task-submit', function(){
      const $container = $(this).closest('[data-seminar-id]');
      const seminarId = $container.data('seminar-id');
      const $name = $container.find('.add-task-name');
      const $deadline = $container.find('.add-task-deadline');
      const $err = $container.find('.add-task-error');
      const name = ($name.val() || '').toString().trim();
      const deadline = ($deadline.val() || '').toString().trim();

      if (!name) { $err.text('タスク名を入力してください').show(); return; }
      if (!/\d{4}-\d{2}-\d{2}/.test(deadline)) { $err.text('有効な日付(YYYY-MM-DD)を入力してください').show(); return; }
      $err.text('').hide();

      const $btn = $(this).prop('disabled', true);
      $.ajax({
        url: `/seminars/${seminarId}/tasks/create-ajax/`,
        method: 'POST',
        headers: csrftoken ? { 'X-CSRFToken': csrftoken } : {},
        data: { name, deadline },
        success: function(res){
          if (!res || !res.success) {
            const msg = (res && res.errors && (res.errors.name || res.errors.deadline)) || (res && res.error) || '作成に失敗しました';
            $err.text(msg).show();
            return;
          }

          const newKey = res.date_key;
          const $group = ensureDateGroup(newKey, res.deadline_display, res.relative_text);

          // アイテムHTMLを作成
          const itemHtml = `
            <div class="task-item cursor-pointer task-pending p-4" data-task-id="${res.pk}">
              <div class="flex items-start gap-4">
                <div class="mt-1">
                  <input type="checkbox" class="custom-checkbox task-checkbox" data-task-id="${res.pk}">
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex justify-between items-start">
                    <div>
                      <h4 class="text-lg font-medium text-gray-900">${res.name}</h4>
                    </div>
                    <div class="text-right">
                      <div class="text-sm text-gray-600">担当: 未設定</div>
                      <button type="button" class="task-edit-start mt-2 text-xs px-2 py-1 rounded border border-gray-300 text-gray-700 hover:bg-gray-50">編集</button>
                    </div>
                  </div>
                  <div class="task-edit-form mt-3 hidden">
                    <div class="flex flex-wrap items-center gap-2">
                      <input type="text" class="task-edit-name px-2 py-1 border border-gray-300 rounded w-64" value="${res.name}" maxlength="200" placeholder="タスク名">
                      <input type="date" class="task-edit-deadline px-2 py-1 border border-gray-300 rounded" value="${res.date_key}">
                      <button type="button" class="task-edit-save bg-primary-600 hover:bg-primary-700 text-white text-xs px-3 py-1 rounded">保存</button>
                      <button type="button" class="task-edit-cancel text-xs px-3 py-1 rounded border border-gray-300 text-gray-700 hover:bg-gray-50">キャンセル</button>
                      <span class="task-edit-error text-xs text-red-600 ml-2" style="display:none"></span>
                    </div>
                  </div>
                </div>
              </div>
            </div>`;

          $group.find('[data-accordion-panel]').append(itemHtml);

          // グループ開く＆カウント更新
          const $toggle = $group.find('.date-group-toggle');
          const $panel = $group.find('[data-accordion-panel]');
          if ($panel.attr('hidden') !== undefined) {
            $panel.removeAttr('hidden');
            $toggle.addClass('open');
            // openSetにも追加
            try {
              const raw = localStorage.getItem('seminar_detail_open_dates');
              const arr = raw ? JSON.parse(raw) : [];
              const set = new Set(Array.isArray(arr) ? arr : []);
              set.add(newKey);
              localStorage.setItem('seminar_detail_open_dates', JSON.stringify(Array.from(set)));
            } catch {}
          }
          updateGroupCounts($group);
          updateGlobalProgress();

          // フォームリセット
          $name.val('');
          $deadline.val('');
        },
        error: function(xhr){
          let msg = '通信エラーが発生しました';
          if (xhr && xhr.responseJSON && xhr.responseJSON.errors) {
            const er = xhr.responseJSON.errors;
            msg = er.name || er.deadline || xhr.responseJSON.error || msg;
          }
          $err.text(msg).show();
        },
        complete: function(){
          $btn.prop('disabled', false);
        }
      });
    });
  });
})(jQuery);
