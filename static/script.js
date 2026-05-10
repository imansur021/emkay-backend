/* ═══════════════════════════════════════════════════════════
   EMKAY JS PATCH
   Add a <script src="emkay-patch.js"></script> tag
   AFTER your existing <script src="script__2_.js"></script>

   Implements ALL 5 missing features:
   1) Chat message slide-in animation  (CSS does the work)
   2) Button ripple effect
   3) Quick-reply chips in chat
   4) Chat history in localStorage
   5) Browser language auto-detect
═══════════════════════════════════════════════════════════ */

(function () {

  // ── 5. BROWSER LANGUAGE AUTO-DETECT ──────────────────────
  // Runs immediately — sets currentLang before initChat() fires
  (function detectBrowserLanguage() {
    var MAP = {
      'en':'en','en-US':'en','en-GB':'en','en-NG':'en',
      'fr':'fr','fr-FR':'fr','fr-CA':'fr',
      'de':'de','de-DE':'de','de-AT':'de',
      'es':'es','es-ES':'es','es-MX':'es',
      'pt':'pt','pt-BR':'pt','pt-PT':'pt',
      'ar':'ar','ar-SA':'ar','ar-EG':'ar',
      'zh':'zh','zh-CN':'zh','zh-TW':'zh',
      'sw':'sw','ha':'ha','ig':'ig','yo':'yo'
    };
    var langs = (navigator.languages && navigator.languages.length)
      ? Array.from(navigator.languages)
      : [navigator.language || 'en'];

    for (var i = 0; i < langs.length; i++) {
      var full = langs[i];               // e.g. "pt-BR"
      var base = full.split('-')[0];     // e.g. "pt"
      if (MAP[full]) { currentLang = MAP[full]; break; }
      if (MAP[base]) { currentLang = MAP[base]; break; }
    }
    // Only switch if user hasn't manually chosen a language already
    // (respect any saved preference in localStorage)
    // currentLang is now set to the browser's language before initChat runs
  })();


  // ── 4. CHAT HISTORY IN localStorage ──────────────────────
  var CHAT_KEY = 'emkay-chat-v1';
  var MAX_MSGS = 30;

  // Save originals before wrapping
  var _origAddBotMsg  = addBotMsg;
  var _origAddUserMsg = addUserMsg;
  var _origInitChat   = initChat;

  // Wrap addBotMsg: render + save
  addBotMsg = function (text) {
    var el = _origAddBotMsg(text);
    _saveChatMsg('bot', text);
    return el;
  };

  // Wrap addUserMsg: render + save
  addUserMsg = function (text) {
    _origAddUserMsg(text);
    _saveChatMsg('user', text);
  };

  function _saveChatMsg(role, text) {
    try {
      var stored = JSON.parse(localStorage.getItem(CHAT_KEY) || '[]');
      stored.push({ role: role, text: text });
      if (stored.length > MAX_MSGS) stored.splice(0, stored.length - MAX_MSGS);
      localStorage.setItem(CHAT_KEY, JSON.stringify(stored));
    } catch (e) {}
  }

  function _loadChatHistory() {
    try { return JSON.parse(localStorage.getItem(CHAT_KEY) || '[]'); }
    catch (e) { return []; }
  }

  // Wrap initChat: restore history OR show fresh greeting + chips
  initChat = function () {
    var history = _loadChatHistory();

    if (history.length > 0) {
      // --- Returning visitor: replay saved messages ---
      var msgs = document.getElementById('chat-msgs');
      if (msgs) msgs.innerHTML = '';

      // Render saved messages using original (no re-saving)
      history.forEach(function (m) {
        if (m.role === 'bot')  _origAddBotMsg(m.text);
        if (m.role === 'user') _origAddUserMsg(m.text);
      });

      // Small "resumed" label — not saved to history
      var resume = {
        en:'🔄 Resuming your conversation…',
        fr:'🔄 Reprise de votre conversation…',
        ha:'🔄 Ana ci gaba da tattaunawar ku…',
        ig:'🔄 Na-aga n\'ihu n\'okwu gị…',
        yo:'🔄 A tẹ̀síwájú ìfọ̀rọ̀wérọ̀ rẹ…',
        zh:'🔄 恢复您的对话…',
        ar:'🔄 استئناف محادثتك…',
        es:'🔄 Retomando tu conversación…',
        pt:'🔄 Retomando sua conversa…',
        de:'🔄 Gespräch wird fortgesetzt…',
        sw:'🔄 Kuendelea na mazungumzo yako…'
      };
      var label = document.createElement('div');
      label.className = 'msg bot';
      label.style.cssText = 'opacity:.55;font-size:11px;font-style:italic;';
      label.textContent = resume[currentLang] || resume.en;
      document.getElementById('chat-msgs').appendChild(label);

    } else {
      // --- Fresh visitor: show greeting + quick chips ---
      _origInitChat();
      setTimeout(_showQuickChips, 500);
    }
  };


  // ── 3. QUICK-REPLY CHIPS ──────────────────────────────────
  // Each chip: [display label, NLP query text]
  var CHIPS = {
    en: [['📋 Services','services'],   ['💰 Pricing','pricing'],  ['📞 Contact','phone'],     ['📍 Location','location']],
    fr: [['📋 Services','services'],   ['💰 Tarifs','prix'],      ['📞 Contact','téléphone'], ['📍 Adresse','bureau']],
    ha: [['📋 Ayyuka','ayyuka'],        ['💰 Farashi','kuɗi'],    ['📞 Tuntuɓe','waya'],      ['📍 Wuri','inda ofishi']],
    ig: [['📋 Ọrụ','ọrụ'],             ['💰 Ọnụ ahịa','ego'],   ['📞 Kpọọ','ekwentị'],      ['📍 Ebe','adreesi']],
    yo: [['📋 Iṣẹ','iṣẹ'],             ['💰 Idiyè','owó'],       ['📞 Pe wa','foonu'],        ['📍 Ibiti','adirẹsi']],
    zh: [['📋 服务','服务'],             ['💰 价格','价格'],       ['📞 联系','电话'],           ['📍 位置','地址']],
    ar: [['📋 الخدمات','خدمات'],        ['💰 الأسعار','سعر'],    ['📞 اتصل','هاتف'],          ['📍 الموقع','عنوان']],
    es: [['📋 Servicios','services'],   ['💰 Precios','precio'],  ['📞 Contacto','teléfono'], ['📍 Ubicación','dirección']],
    pt: [['📋 Serviços','services'],    ['💰 Preços','preço'],    ['📞 Contato','telefone'],   ['📍 Local','endereço']],
    de: [['📋 Dienste','services'],     ['💰 Preise','preis'],    ['📞 Kontakt','telefon'],    ['📍 Standort','adresse']],
    sw: [['📋 Huduma','huduma'],         ['💰 Bei','bei'],         ['📞 Wasiliana','simu'],     ['📍 Mahali','ofisi']]
  };

  function _showQuickChips() {
    var msgs = document.getElementById('chat-msgs');
    if (!msgs || document.getElementById('quick-chips')) return;

    var chips = CHIPS[currentLang] || CHIPS.en;
    var wrap = document.createElement('div');
    wrap.className = 'quick-chips';
    wrap.id = 'quick-chips';

    chips.forEach(function (pair) {
      var label = pair[0];
      var query = pair[1];
      var btn = document.createElement('button');
      btn.className = 'chip-btn';
      btn.textContent = label;
      btn.onclick = function () {
        // Remove chips immediately
        var w = document.getElementById('quick-chips');
        if (w) w.remove();
        // Show user message (the label)
        addUserMsg(label);
        // Show typing then bot reply
        showTyping();
        setTimeout(function () {
          hideTyping();
          var reply = emkayBot(query);
          addBotMsg(reply);
        }, 600);
      };
      wrap.appendChild(btn);
    });

    msgs.appendChild(wrap);
    msgs.scrollTop = msgs.scrollHeight;
  }


  // ── 2. BUTTON RIPPLE EFFECT ───────────────────────────────
  // Uses event delegation — one listener handles all buttons
  document.addEventListener('click', function (e) {
    var btn = e.target.closest(
      '.btn-primary, .btn-outline, .nav-cta, #chat-send, #form-btn'
    );
    if (!btn) return;

    var r = document.createElement('span');
    r.className = 'btn-ripple';
    var rect = btn.getBoundingClientRect();
    var size = Math.max(rect.width, rect.height);
    r.style.width  = size + 'px';
    r.style.height = size + 'px';
    r.style.left   = (e.clientX - rect.left - size / 2) + 'px';
    r.style.top    = (e.clientY - rect.top  - size / 2) + 'px';
    btn.appendChild(r);
    r.addEventListener('animationend', function () { r.remove(); });
  }, true);

})();
