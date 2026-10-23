(function () {
  'use strict';
  const calc = Calc.create();
  const $ = (id) => document.getElementById(id);
  const exprEl = $('expr'), resEl = $('result'), srEl = $('sr-status');
  const keys = [...document.querySelectorAll('.key')];

  /* Shrink a text element until it fits its container (also helps when the user's system font size is large). */
  function fitText(el, min, room) {
    el.style.fontSize = '';
    let size = parseFloat(getComputedStyle(el).fontSize);
    el.style.fontSize = size + 'px';
    while (el.scrollWidth > room && size > min) { size -= 2; el.style.fontSize = size + 'px'; }
  }
  function fit() {
    const room = resEl.parentElement.clientWidth - 56;
    fitText(resEl, 36, room);
    fitText(exprEl, 16, room);
  }

  /* ---- Screen-reader speech -------------------------------------------------- */
  const WORDS = { '+': 'plus', '−': 'minus', '×': 'times', '÷': 'divided by', '=': 'equals' };
  function spoken(t) {
    return t.replace(/[+−×÷=]/g, (m) => ' ' + WORDS[m] + ' ')
            .replace(/(^|\s)-(?=\d)/g, '$1negative ')     // "-5" → "negative 5"
            .replace(/\s+/g, ' ').trim();
  }
  let flip = false;
  function announce(text) {                                // toggling an invisible char makes identical text re-announce
    flip = !flip; srEl.textContent = text + (flip ? '\u200B' : '');
  }

  function render() {
    const st = calc.state();
    resEl.textContent = st.error ? st.display : Calc.group(st.display);
    exprEl.textContent = st.expr ? Calc.group(st.expr) : '\u00A0';
    exprEl.classList.toggle('error', st.error);
    resEl.classList.toggle('error', st.error);
    keys.forEach((k) => {
      const isOp = k.classList.contains('op'), on = isOp && k.dataset.k === st.op;
      k.classList.toggle('active', on);
      if (k.hasAttribute('aria-pressed')) k.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    fit();
    return st;
  }

  function press(k) {
    calc.press(k);
    const st = render();
    if (st.error) announce('Error. ' + st.expr);
    else if (k === 'AC') announce('Cleared. 0');
    else if (k === '=') announce(spoken(Calc.group(st.expr + ' ' + st.display)));
    else if (st.op) announce(spoken(Calc.group(st.expr)));
    else announce(spoken(Calc.group(st.display)));
  }

  document.querySelector('.keypad').addEventListener('click', (e) => {
    const b = e.target.closest('.key'); if (!b) return;
    press(b.dataset.k);
    if (e.detail > 0) b.blur();            // pointer/touch tap: don't leave focus here, so an external keyboard's Enter means "="
  });

  /* Hardware-keyboard support. Digits and operator symbols only — NO single-letter shortcuts, so speech
     dictation / stray typing can't trigger actions (WCAG 2.1.4). Enter/Space are left alone when a key has
     focus, so keyboard users activate the key they tabbed to (WCAG 2.1.1 / 3.2.2). */
  const map = { '*': '×', '/': '÷', '-': '−', '+': '+', '%': '%', '.': '.', ',': '.', '=': '=', 'Escape': 'AC' };
  document.addEventListener('keydown', (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const onKey = e.target && e.target.classList && e.target.classList.contains('key');
    if (onKey && (e.key === 'Enter' || e.key === ' ')) return;     // native button activation
    const k = /^[0-9]$/.test(e.key) ? e.key : (e.key === 'Enter' ? '=' : map[e.key]);
    if (k) { e.preventDefault(); press(k); }
  });

  window.addEventListener('resize', fit);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
  render();
})();
