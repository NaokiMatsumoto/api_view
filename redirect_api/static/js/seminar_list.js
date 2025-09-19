// 元のコードをベースにした最小限の改善版
(function() {
  'use strict';

  // 重複実行を防ぐ
  if (window.seminarCardHandlerLoaded) return;
  window.seminarCardHandlerLoaded = true;

  // カード全体クリックで詳細へ。内部のリンク/ボタンは通常動作。
  document.addEventListener('click', function(e) {
    const btn = e.target.closest('a, button');
    if (btn && btn.closest('.seminar-card')) {
      // 内部リンクやボタンは優先（編集・複製・タイトルリンクなど）
      return;
    }

    const card = e.target.closest('.seminar-card');
    if (!card) return;

    const href = card.getAttribute('data-href');
    if (!href) return;

    // URL の安全性チェックを追加
    try {
      const url = new URL(href, window.location.origin);
      if (url.origin !== window.location.origin) {
        // 外部URLは新しいタブで開く
        window.open(href, '_blank', 'noopener,noreferrer');
      } else {
        window.location.href = href;
      }
    } catch (error) {
      console.warn('Invalid URL:', href);
      // フォールバック：元の動作
      window.location.href = href;
    }
  });

  // キーボード操作のアクセシビリティ
  document.addEventListener('keydown', function(e) {
    if (e.key !== 'Enter' && e.key !== ' ') return;

    const card = e.target.closest('.seminar-card');
    if (!card) return;

    const tag = (e.target.tagName || '').toLowerCase();
    if (['a', 'button', 'input', 'textarea', 'select'].includes(tag)) return;

    const href = card.getAttribute('data-href');
    if (href) {
      if (e.key === ' ') {
        e.preventDefault(); // スペースキーのスクロールを防ぐ
      }

      // URL の安全性チェック
      try {
        const url = new URL(href, window.location.origin);
        if (url.origin !== window.location.origin) {
          window.open(href, '_blank', 'noopener,noreferrer');
        } else {
          window.location.href = href;
        }
      } catch (error) {
        console.warn('Invalid URL:', href);
        window.location.href = href;
      }
    }
  });

  // アクセシビリティの自動向上
  function enhanceAccessibility() {
    const cards = document.querySelectorAll('.seminar-card[data-href]');
    cards.forEach(function(card) {
      if (!card.hasAttribute('tabindex')) {
        card.setAttribute('tabindex', '0');
      }
      if (!card.hasAttribute('role')) {
        card.setAttribute('role', 'button');
      }
      if (!card.hasAttribute('aria-label')) {
        const title = card.querySelector('h1, h2, h3, h4, h5, h6, .title')?.textContent?.trim();
        if (title) {
          card.setAttribute('aria-label', title + 'の詳細を表示');
        }
      }
    });
  }

  // 初期化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhanceAccessibility);
  } else {
    enhanceAccessibility();
  }

  // 必要に応じて再実行できるようにグローバルに公開
  window.enhanceSeminarCardAccessibility = enhanceAccessibility;

})();