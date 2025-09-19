(function(){
  'use strict';

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function updateSetting(id, value) {
    fetch(`/seminars/notifications/${id}/update/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: new URLSearchParams({days_before: value})
    })
    .then(res => res.json())
    .then(data => {
      if (!data.success) {
        alert("更新失敗: " + (data.error || ""));
      }
    });
  }

  function saveSetting(id) {
    const row = document.getElementById("row-" + id);
    if (!row) return;
    const daysInput = row.querySelector('input[type="number"]');
    const days = daysInput ? daysInput.value : '';
    const select = row.querySelector('.setting-integrations');
    let ids = [];
    if (select) {
      ids = Array.from(select.selectedOptions).map(o => o.value);
    }
    const params = new URLSearchParams();
    if (days !== '') params.append('days_before', days);
    if (ids.length > 0) params.append('integration_ids', ids.join(','));

    fetch(`/seminars/notifications/${id}/update/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: params
    })
    .then(res => res.json())
    .then(data => {
      if (!data.success) {
        alert("保存失敗: " + (data.error || ""));
      }
    });
  }

  function deleteSetting(id) {
    if (!confirm("削除してよろしいですか？")) return;
    fetch(`/seminars/notifications/${id}/delete/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      }
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        const row = document.getElementById("row-" + id);
        if (row) row.remove();
      } else {
        alert("削除失敗: " + (data.error || ""));
      }
    });
  }

  // expose to global for inline handlers in template
  window.getCookie = getCookie;
  window.updateSetting = updateSetting;
  window.saveSetting = saveSetting;
  window.deleteSetting = deleteSetting;
})();
