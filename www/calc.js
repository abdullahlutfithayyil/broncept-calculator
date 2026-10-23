/* Calculator engine — pure logic, no DOM. Works in browser (window.Calc) and Node (require). */
(function (root) {
  'use strict';
  const MAX_DIGITS = 12;
  const OPS = { '+': (a, b) => a + b, '−': (a, b) => a - b, '×': (a, b) => a * b, '÷': (a, b) => a / b };

  function fmt(n) {
    if (Object.is(n, -0)) n = 0;
    let r = Number(n.toPrecision(12));
    if (Object.is(r, -0)) r = 0;
    const a = Math.abs(r);
    if (a !== 0 && (a >= 1e12 || a < 1e-9)) return r.toExponential(6).replace(/\.?0+e/, 'e');
    return String(r);
  }
  const num = (s) => parseFloat(s);
  const digitCount = (s) => s.replace(/[^0-9]/g, '').length;

  function create() {
    let s;
    const reset = () => {
      s = { display: '0', expr: '', acc: null, op: null, entering: false, done: false, error: false, lastOp: null, lastOperand: null };
    };
    reset();

    const fail = () => { reset(); s.error = true; s.display = 'Error'; s.expr = "Can't divide by 0"; };
    const apply = (a, op, b) => (op === '÷' && b === 0) ? null : OPS[op](a, b);
    const fresh = () => { if (s.error) reset(); };

    return {
      state: () => ({ display: s.display, expr: s.expr, error: s.error, op: s.op && !s.entering ? s.op : null }),
      clear: reset,

      digit(d) {
        fresh();
        if (s.done) { s.expr = ''; s.acc = null; s.op = null; s.done = false; s.entering = false; }
        if (!s.entering) { s.display = d; s.entering = true; return; }
        if (s.display === '0') s.display = d;
        else if (s.display === '-0') s.display = '-' + d;
        else if (digitCount(s.display) < MAX_DIGITS) s.display += d;
      },

      dot() {
        fresh();
        if (s.done) { s.expr = ''; s.acc = null; s.op = null; s.done = false; s.entering = false; }
        if (!s.entering) { s.display = '0.'; s.entering = true; return; }
        if (!s.display.includes('.')) s.display += '.';
      },

      operator(o) {
        if (s.error) return;
        if (s.op && s.entering) {                 // chain: 2 + 3 + → 5 +
          const r = apply(s.acc, s.op, num(s.display));
          if (r === null) return fail();
          s.acc = r; s.display = fmt(r);
        } else if (!s.op) {
          s.acc = num(s.display);
        }
        s.op = o; s.expr = fmt(s.acc) + ' ' + o; s.entering = false; s.done = false;
      },

      equals() {
        if (s.error) return;
        let a, op, b;
        if (s.op) { a = s.acc; op = s.op; b = num(s.display); }
        else if (s.done && s.lastOp) { a = num(s.display); op = s.lastOp; b = s.lastOperand; }  // repeat last
        else return;
        const r = apply(a, op, b);
        if (r === null) return fail();
        s.expr = fmt(a) + ' ' + op + ' ' + fmt(b) + ' =';
        s.display = fmt(r);
        s.lastOp = op; s.lastOperand = b; s.op = null; s.acc = null; s.entering = false; s.done = true;
      },

      negate() {
        if (s.error) return;
        if (!s.entering && s.op) { s.display = '-0'; s.entering = true; return; }
        if (s.display === '0') return;
        s.display = s.display.startsWith('-') ? s.display.slice(1) : '-' + s.display;
      },

      percent() {
        if (s.error) return;
        s.display = fmt(num(s.display) / 100); s.entering = false;
      },

      press(key) {
        if (/^[0-9]$/.test(key)) this.digit(key);
        else if (key === '.') this.dot();
        else if (key in OPS) this.operator(key);
        else if (key === '=') this.equals();
        else if (key === '±') this.negate();
        else if (key === '%') this.percent();
        else if (key === 'AC') this.clear();
      },
    };
  }

  /* Thousands separators for display only: "1234567.5" → "1,234,567.5" */
  function group(str) {
    return str.replace(/\d+(?:\.\d*)?/g, (m) => {
      const [i, f] = m.split('.');
      return i.replace(/\B(?=(\d{3})+(?!\d))/g, ',') + (f !== undefined ? '.' + f : '');
    });
  }

  const api = { create, group, fmt };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.Calc = api;
})(typeof window !== 'undefined' ? window : globalThis);
