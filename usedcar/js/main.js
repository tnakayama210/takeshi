/* 株式会社delta 中古車販売LP
 * - 車両写真ギャラリー
 * - モバイル固定CTAの表示制御
 * 依存ライブラリなし
 */
(function () {
  'use strict';

  /* ---------- 車両写真ギャラリー ---------- */
  document.querySelectorAll('[data-gallery]').forEach(function (g) {
    var main = g.querySelector('[data-gallery-main]');
    var thumbs = g.querySelectorAll('.thumb');
    thumbs.forEach(function (t) {
      t.addEventListener('click', function () {
        main.src = t.dataset.src;
        main.alt = t.dataset.alt;
        main.style.objectPosition = t.dataset.pos || '50% 50%';
        thumbs.forEach(function (x) { x.setAttribute('aria-pressed', String(x === t)); });
      });
    });
  });

  /* ---------- モバイル固定CTA：お問い合わせ欄の表示中は隠す ---------- */
  var sticky = document.getElementById('sticky-cta');
  var contact = document.getElementById('contact');
  if (sticky && contact && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      var visible = entries[0].isIntersecting;
      sticky.style.transform = visible ? 'translateY(110%)' : '';
      sticky.inert = visible;
    }, { threshold: 0.05 }).observe(contact);
  }
})();
