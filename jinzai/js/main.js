/* 株式会社delta 特定技能外国人の派遣・紹介LP
 * - モバイル固定CTAの表示制御（お問い合わせ欄の表示中は隠す）
 * 依存ライブラリなし
 */
(function () {
  'use strict';
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
