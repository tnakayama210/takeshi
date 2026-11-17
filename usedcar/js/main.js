/* 株式会社delta 中古車販売LP
 * - 車両写真ギャラリー
 * - お問い合わせフォーム：バリデーション / 送信 / 完了表示
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

  /* ---------- お問い合わせフォーム ---------- */
  var form = document.getElementById('contact-form');
  if (!form) return;
  var thanks = document.getElementById('contact-thanks');
  var summary = document.getElementById('form-error-summary');
  var submitBtn = form.querySelector('button[type="submit"]');

  // 全角英数字・記号 → 半角
  function toHalfWidth(s) {
    return s.replace(/[！-～]/g, function (c) { return String.fromCharCode(c.charCodeAt(0) - 0xfee0); })
            .replace(/[ー−‐―]/g, '-').replace(/　/g, ' ');
  }

  var rules = {
    name: function (v) { return v.trim() ? '' : 'お名前を入力してください。'; },
    tel: function (v) {
      if (!v.trim()) return '電話番号を入力してください。';
      return /^0\d{9,10}$/.test(toHalfWidth(v).replace(/\D/g, '')) ? '' : '電話番号は0から始まる10〜11桁の数字で入力してください。';
    },
    email: function (v) {
      var s = toHalfWidth(v).trim();
      if (!s) return 'メールアドレスを入力してください。';
      return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(s) ? '' : 'メールアドレスの形式が正しくありません。';
    },
    privacy: function (_, el) { return el.checked ? '' : '個人情報の取り扱いへの同意が必要です。'; }
  };

  function validateField(name) {
    var el = form.elements[name];
    var err = document.getElementById(el.id + '-err');
    var msg = rules[name](el.value, el);
    if (msg) {
      el.setAttribute('aria-invalid', 'true');
      el.setAttribute('aria-errormessage', err.id);
    } else {
      el.removeAttribute('aria-invalid');
      el.removeAttribute('aria-errormessage');
    }
    err.textContent = msg;
    err.hidden = !msg;
    return !msg;
  }

  Object.keys(rules).forEach(function (name) {
    var el = form.elements[name];
    var touched = false;
    el.addEventListener('blur', function () { touched = true; validateField(name); });
    el.addEventListener(el.type === 'checkbox' ? 'change' : 'input', function () {
      if (touched || el.getAttribute('aria-invalid')) validateField(name);
    });
  });

  function buildPayload() {
    var fd = new FormData(form);
    fd.set('tel', toHalfWidth(fd.get('tel')).trim());
    fd.set('email', toHalfWidth(fd.get('email')).trim());
    fd.set('source', 'usedcar-lp');
    return fd;
  }

  /**
   * 送信処理（バックエンド接続ポイント）
   * data-endpoint が空ならデモモード。
   * @param {FormData} payload
   * @returns {Promise<void>}
   */
  function submitInquiry(payload) {
    var endpoint = form.dataset.endpoint;
    if (!endpoint) {
      if (window.console) console.info('[demo] お問い合わせデータ', Object.fromEntries(payload.entries()));
      return new Promise(function (resolve) { setTimeout(resolve, 600); });
    }
    return fetch(endpoint, {
      method: 'POST',
      body: payload,
      headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
      credentials: 'same-origin'
    }).then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
    });
  }

  function showThanks() {
    form.hidden = true;
    document.querySelectorAll('[data-hide-on-thanks]').forEach(function (el) { el.hidden = true; });
    thanks.hidden = false;
    var stickyCta = document.getElementById('sticky-cta');
    if (stickyCta) stickyCta.remove();
    document.getElementById('contact').scrollIntoView({ behavior: 'smooth', block: 'start' });
    thanks.focus({ preventScroll: true });
    if (typeof window.gtag === 'function') window.gtag('event', 'generate_lead', { form: 'usedcar_contact' });
    if (typeof window.ga === 'function') window.ga('send', 'event', 'usedcar', 'contact_submit');
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    summary.hidden = true;
    if (form.elements.website.value) return; // ハニーポット

    var firstInvalid = null;
    Object.keys(rules).forEach(function (name) {
      if (!validateField(name) && !firstInvalid) firstInvalid = form.elements[name];
    });
    if (firstInvalid) {
      summary.textContent = '入力内容をご確認ください。';
      summary.hidden = false;
      firstInvalid.focus();
      return;
    }

    submitBtn.disabled = true;
    var label = submitBtn.textContent;
    submitBtn.textContent = '送信中…';

    submitInquiry(buildPayload())
      .then(showThanks)
      .catch(function () {
        summary.textContent = '送信に失敗しました。お電話（03-6327-0805）でお問い合わせください。';
        summary.hidden = false;
      })
      .then(function () {
        submitBtn.disabled = false;
        submitBtn.textContent = label;
      });
  });

  /* ---------- モバイル固定CTA：フォーム表示中は隠す ---------- */
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
