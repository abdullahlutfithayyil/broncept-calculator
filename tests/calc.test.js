const test = require('node:test'); const assert = require('node:assert/strict');
const { create, group, fmt } = require('../www/calc.js');
const run = (...keys) => { const c = create(); keys.forEach((k) => c.press(k)); return c.state(); };

test('basic arithmetic', () => {
  assert.equal(run('1', '2', '×', '3', '=').display, '36');
  assert.equal(run('9', '−', '4', '=').display, '5');
  assert.equal(run('8', '÷', '4', '=').display, '2');
  assert.equal(run('2', '+', '3', '=').display, '5');
});
test('expression line', () => {
  assert.equal(run('1', '2', '×', '3', '=').expr, '12 × 3 =');
  assert.equal(run('1', '2', '×').expr, '12 ×');
});
test('floating point is tidy', () => {
  assert.equal(run('0', '.', '1', '+', '0', '.', '2', '=').display, '0.3');
  assert.equal(run('1', '÷', '3', '=').display, '0.333333333333');
});
test('chaining is left-to-right and shows running total', () => {
  const s = run('2', '+', '3', '×');
  assert.equal(s.display, '5'); assert.equal(s.expr, '5 ×');
  assert.equal(run('2', '+', '3', '×', '4', '=').display, '20');
});
test('equals repeats last operation', () => {
  assert.equal(run('2', '+', '3', '=', '=', '=').display, '11');
});
test('operator after result continues from result', () => {
  assert.equal(run('2', '+', '3', '=', '×', '4', '=').display, '20');
});
test('typing after result starts a new number', () => {
  const s = run('2', '+', '3', '=', '7'); assert.equal(s.display, '7'); assert.equal(s.expr, '');
});
test('changing operator before typing replaces it', () => {
  assert.equal(run('5', '+', '×', '3', '=').display, '15');
});
test('divide by zero shows error and recovers', () => {
  const s = run('5', '÷', '0', '='); assert.equal(s.error, true); assert.equal(s.display, 'Error'); assert.equal(s.expr, "Can't divide by 0");
  assert.equal(run('5', '÷', '0', '=', '7').display, '7');
  assert.equal(run('5', '÷', '0', '=', '7').error, false);
});
test('decimal handling', () => {
  assert.equal(run('.', '5').display, '0.5');
  assert.equal(run('1', '.', '2', '.', '3').display, '1.23');
  assert.equal(run('3', '.', '=').display, '3.');   // still typing
});
test('leading zeros', () => { assert.equal(run('0', '0', '7').display, '7'); });
test('digit limit', () => { assert.equal(run(...'12345678901234567'.split('')).display, '123456789012'); });
test('plus/minus', () => {
  assert.equal(run('5', '±').display, '-5');
  assert.equal(run('5', '±', '±').display, '5');
  assert.equal(run('0', '±').display, '0');
  assert.equal(run('5', '×', '±', '3', '=').display, '-15');
});
test('percent', () => {
  assert.equal(run('5', '0', '%').display, '0.5');
  assert.equal(run('2', '0', '0', '×', '5', '0', '%', '=').display, '100');
});
test('AC resets everything', () => {
  const s = run('5', '+', '3', 'AC'); assert.equal(s.display, '0'); assert.equal(s.expr, '');
});
test('pending operator is reported for highlighting', () => {
  assert.equal(run('5', '×').op, '×'); assert.equal(run('5', '×', '3').op, null);
});
test('large and small results', () => {
  assert.equal(run(...'999999999999'.split(''), '×', '9', '=').display, '9e+12');
  assert.equal(fmt(0.000000000123), '1.23e-10');
  assert.equal(fmt(-0), '0');
});
test('grouping', () => {
  assert.equal(group('1234567.5'), '1,234,567.5'); assert.equal(group('-1234'), '-1,234'); assert.equal(group('12 × 3 ='), '12 × 3 ='); assert.equal(group('1234.'), '1,234.');
  assert.equal(group('0.123456'), '0.123456');
});
