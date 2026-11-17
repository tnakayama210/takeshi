/* 株式会社delta 中古車オークション 参加登録LP
 * - FAQ アコーディオン
 * - 参加登録フォーム：バリデーション / 送信 / 完了表示
 * - モバイル固定CTAの表示制御
 * 依存ライブラリなし（ES2017）
 */
(function () {
  'use strict';

  /* ---------- FAQ アコーディオン ---------- */
  document.querySelectorAll('[data-accordion] .faq-q').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var panel = document.getElementById(btn.getAttribute('aria-controls'));
      var open = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!open));
      panel.hidden = open;
    });
  });

  /* ---------- 参加登録フォーム ---------- */
  var form = document.getElementById('entry-form');
  if (!form) return;
  var thanks = document.getElementById('entry-thanks');
  var summary = document.getElementById('form-error-summary');
  var submitBtn = form.querySelector('button[type="submit"]');
  var licenseWrap = document.getElementById('license-input-wrap');
  var licenseLater = document.getElementById('license-later-note');
  var licenseInput = document.getElementById('f-license');

  // 全角英数字・記号 → 半角
  function toHalfWidth(s) {
    return s.replace(/[！-～]/g, function (c) { return String.fromCharCode(c.charCodeAt(0) - 0xfee0); })
            .replace(/[ー−‐―]/g, '-').replace(/　/g, ' ');
  }
  function digitsOnly(s) { return toHalfWidth(s).replace(/\D/g, ''); }
  function licenseStatus() { return form.querySelector('input[name="license_status"]:checked').value; }

  // 各項目のルール：値が正しければ '' を、誤りがあればエラーメッセージを返す
  var rules = {
    company: function (v) { return v.trim() ? '' : '会社名／屋号を入力してください。'; },
    name: function (v) { return v.trim() ? '' : 'ご担当者名を入力してください。'; },
    tel: function (v) {
      if (!v.trim()) return '電話番号を入力してください。';
      var d = digitsOnly(v);
      return /^0\d{9,10}$/.test(d) ? '' : '電話番号は0から始まる10〜11桁の数字で入力してください。';
    },
    prefecture: function (v) { return v ? '' : '都道府県を選択してください。'; },
    email: function (v) {
      var s = toHalfWidth(v).trim();
      if (!s) return 'メールアドレスを入力してください。';
      return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(s) ? '' : 'メールアドレスの形式が正しくありません。';
    },
    license_number: function (v) {
      if (licenseStatus() === 'later') return '';
      if (!v.trim()) return '古物商許可証番号を入力するか、「後日提出する」を選択してください。';
      return /^\d{12}$/.test(digitsOnly(v)) ? '' : '古物商許可証番号は12桁の数字で入力してください。';
    },
    privacy: function (_, el) { return el.checked ? '' : '個人情報の取り扱いへの同意が必要です。'; }
  };

  function fieldEl(name) { return form.elements[name]; }
  function errEl(el) { return document.getElementById(el.id + '-err'); }

  function validateField(name) {
    var el = fieldEl(name);
    var msg = rules[name](el.value, el);
    var err = errEl(el);
    if (msg) {
      el.setAttribute('aria-invalid', 'true');
      el.setAttribute('aria-errormessage', err.id);
      err.textContent = msg;
      err.hidden = false;
    } else {
      el.removeAttribute('aria-invalid');
      el.removeAttribute('aria-errormessage');
      err.textContent = '';
      err.hidden = true;
    }
    return !msg;
  }

  // 入力中は「一度触った項目」だけ再検証（打鍵ごとに赤くしない）
  Object.keys(rules).forEach(function (name) {
    var el = fieldEl(name);
    var touched = false;
    el.addEventListener('blur', function () { touched = true; validateField(name); });
    el.addEventListener(el.type === 'checkbox' || el.tagName === 'SELECT' ? 'change' : 'input', function () {
      if (touched || el.getAttribute('aria-invalid')) validateField(name);
    });
  });

  // 古物商許可証番号：今すぐ入力／後日提出 の切り替え
  form.querySelectorAll('input[name="license_status"]').forEach(function (r) {
    r.addEventListener('change', function () {
      var later = licenseStatus() === 'later';
      licenseWrap.hidden = later;
      licenseLater.hidden = !later;
      licenseInput.disabled = later;
      if (later) validateField('license_number'); // エラー表示をクリア
    });
  });

  // 送信データの整形（バックエンドへ渡す形）
  function buildPayload() {
    var fd = new FormData(form);
    fd.set('tel', toHalfWidth(fd.get('tel')).trim());
    fd.set('email', toHalfWidth(fd.get('email')).trim());
    if (licenseStatus() === 'now') fd.set('license_number', digitsOnly(licenseInput.value));
    else fd.set('license_number', '');
    fd.set('source', 'auction-lp');
    return fd;
  }

  /**
   * 送信処理（バックエンド接続ポイント）
   * data-endpoint が空ならデモモード。既存PHPフォーム等に繋ぐ場合はここを調整してください。
   * @param {FormData} payload
   * @returns {Promise<void>} 成功で resolve、失敗で reject
   */
  function submitRegistration(payload) {
    var endpoint = form.dataset.endpoint;
    if (!endpoint) {
      if (window.console) console.info('[demo] 参加登録データ', Object.fromEntries(payload.entries()));
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
    if (stickyCta) stickyCta.remove(); // 登録完了後は固定CTAを出さない
    document.getElementById('entry').scrollIntoView({ behavior: 'smooth', block: 'start' });
    thanks.focus({ preventScroll: true });
    if (typeof window.gtag === 'function') window.gtag('event', 'generate_lead', { form: 'auction_entry' });
    if (typeof window.ga === 'function') window.ga('send', 'event', 'auction', 'entry_submit');
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    summary.hidden = true;

    if (form.elements.website.value) return; // ハニーポットに入力あり＝bot

    var firstInvalid = null;
    Object.keys(rules).forEach(function (name) {
      if (!validateField(name) && !firstInvalid) firstInvalid = fieldEl(name);
    });
    if (firstInvalid) {
      summary.textContent = '入力内容に誤りがあります。赤字の項目をご確認ください。';
      summary.hidden = false;
      firstInvalid.focus();
      return;
    }

    submitBtn.disabled = true;
    var label = submitBtn.textContent;
    submitBtn.textContent = '送信中…';

    submitRegistration(buildPayload())
      .then(showThanks)
      .catch(function () {
        summary.textContent = '送信に失敗しました。時間をおいて再度お試しいただくか、お電話（03-6327-0805）でお問い合わせください。';
        summary.hidden = false;
      })
      .then(function () {
        submitBtn.disabled = false;
        submitBtn.textContent = label;
      });
  });

  /* ---------- モバイル固定CTA：フォーム表示中は隠す ---------- */
  var sticky = document.getElementById('sticky-cta');
  var entry = document.getElementById('entry');
  if (sticky && entry && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      var visible = entries[0].isIntersecting;
      sticky.style.transform = visible ? 'translateY(110%)' : '';
      sticky.inert = visible;
    }, { threshold: 0.05 }).observe(entry);
  }
})();
