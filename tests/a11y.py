"""Accessibility regression tests (WCAG 2.2 AA oriented). Run: python3 tests/a11y.py  (needs `www/` served on :8765)"""
import asyncio, sys
from playwright.async_api import async_playwright
URL = 'http://localhost:8765/'
results = []
def check(name, cond, extra=''):
    results.append(bool(cond)); print(('PASS ' if cond else 'FAIL ') + name + (f'  [{extra}]' if extra else ''))

def lum(rgb):
    f = lambda c: (c/255)/12.92 if c/255 <= 0.03928 else (((c/255)+0.055)/1.055)**2.4
    r, g, b = rgb; return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)
def ratio(a, b):
    hi, lo = max(lum(a), lum(b)), min(lum(a), lum(b)); return (hi+0.05)/(lo+0.05)
def parse(c):
    import re; return tuple(int(x) for x in re.findall(r'\d+', c)[:3])

async def tap(page, *ks):
    for k in ks: await page.click(f'.key[data-k="{k}"]')
async def status(page): return (await page.inner_text('#sr-status')).replace('\u200b', '')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for scheme in ('light', 'dark'):
            ctx = await b.new_context(viewport={'width': 360, 'height': 800}, color_scheme=scheme, has_touch=True, is_mobile=True)
            pg = await ctx.new_page(); await pg.goto(URL); await pg.wait_for_timeout(300)
            T = f'[{scheme}] '
            # ---- contrast of every key (text vs background), normal + pressed + pending ----
            for kind in ('', ' fn', ' op'):
                sel = f'.key{kind}'.replace(' ', '.') if kind else '.key:not(.fn):not(.op)'
                fg, bg, size = await pg.eval_on_selector(sel, 'e=>{const s=getComputedStyle(e);return [s.color,s.backgroundColor,parseFloat(s.fontSize)]}')
                need = 3.0 if size >= 24 else 4.5       # WCAG "large text" = 24px+
                r = ratio(parse(fg), parse(bg)); check(T+f'key{kind or " digit"} text contrast', r >= need, f'{r:.2f}:1, need {need}')
            for name, var_bg, var_fg in [('digit pressed','--digit-p','--digit-t'),('fn pressed','--fn-p','--fn-t'),('op pressed','--op-p','--op-t')]:
                bgc, fgc = await pg.evaluate(f'(()=>{{const s=getComputedStyle(document.documentElement);const t=document.createElement("i");document.body.appendChild(t);'
                    f't.style.color=s.getPropertyValue("{var_fg}");t.style.background=s.getPropertyValue("{var_bg}");const c=[getComputedStyle(t).backgroundColor,getComputedStyle(t).color];t.remove();return c}})()')
                r = ratio(parse(fgc), parse(bgc)); check(T+f'{name} text contrast', r >= 3.0, f'{r:.2f}:1')
            await tap(pg, '5', '+'); await pg.wait_for_timeout(300)   # let the 80ms colour transition finish
            fg, bg = await pg.eval_on_selector('.key.op.active', 'e=>[getComputedStyle(e).color,getComputedStyle(e).backgroundColor]')
            check(T+'pending-operator key contrast', ratio(parse(fg), parse(bg)) >= 3.0, f'{ratio(parse(fg), parse(bg)):.2f}:1')
            await tap(pg, 'AC')
            page_bg = parse(await pg.evaluate('getComputedStyle(document.body).backgroundColor'))
            r = ratio(parse(await pg.eval_on_selector('#expr', 'e=>getComputedStyle(e).color')), page_bg); check(T+'expression text contrast', r >= 4.5, f'{r:.2f}:1')
            r = ratio(parse(await pg.eval_on_selector('#result', 'e=>getComputedStyle(e).color')), page_bg); check(T+'result text contrast', r >= 4.5, f'{r:.2f}:1')
            await tap(pg, '5', '÷', '0', '=')
            c, s = await pg.eval_on_selector('#expr', 'e=>[getComputedStyle(e).color,parseFloat(getComputedStyle(e).fontSize)]')
            r = ratio(parse(c), page_bg); check(T+'error message contrast (large text rule)', r >= (3.0 if s >= 24 else 4.5), f'{r:.2f}:1 at {s}px')
            await tap(pg, 'AC')
            # ---- key shapes identifiable: fill OR outline must reach 3:1 against the page (WCAG 1.4.11) ----
            for kind, sel in [('digit', '.key:not(.fn):not(.op)'), ('fn', '.key.fn'), ('op', '.key.op')]:
                fill, shadow = await pg.eval_on_selector(sel, 'e=>[getComputedStyle(e).backgroundColor,getComputedStyle(e).boxShadow]')
                import re
                ring = parse(re.match(r'rgb[a]?\([^)]*\)', shadow).group(0)) if shadow != 'none' else None
                best = max(ratio(parse(fill), page_bg), ratio(ring, page_bg) if ring else 0)
                check(T+f'{kind} key shape visible against page', best >= 3.0, f'{best:.2f}:1')
            # ---- pending-operator key must stay identifiable (ring or fill >= 3:1 vs page) ----
            await tap(pg, '5', '×'); await pg.wait_for_timeout(300)
            fill, shadow = await pg.eval_on_selector('.key.op.active', 'e=>[getComputedStyle(e).backgroundColor,getComputedStyle(e).boxShadow]')
            ring = parse(re.match(r'rgb[a]?\([^)]*\)', shadow).group(0)) if shadow != 'none' else None
            best = max(ratio(parse(fill), page_bg), ratio(ring, page_bg) if ring else 0)
            check(T+'pending-operator key shape visible against page', best >= 3.0, f'{best:.2f}:1')
            await tap(pg, 'AC')
            # ---- focus indicator visible (>=3:1 vs page, >=2px) ----
            await pg.keyboard.press('Tab')
            oc, ow = await pg.evaluate('(()=>{const s=getComputedStyle(document.activeElement);return [s.outlineColor,parseFloat(s.outlineWidth)]})()')
            r = ratio(parse(oc), page_bg); check(T+'keyboard focus ring contrast', r >= 3.0 and ow >= 2, f'{r:.2f}:1, {ow}px')
            await ctx.close()

        ctx = await b.new_context(viewport={'width': 360, 'height': 800}, has_touch=True, is_mobile=True, reduced_motion='reduce')
        pg = await ctx.new_page(); await pg.goto(URL); await pg.wait_for_timeout(200)
        # ---- structure / semantics ----
        vp = await pg.get_attribute('meta[name=viewport]', 'content')
        check('pinch-zoom NOT disabled', 'user-scalable=no' not in vp and 'maximum-scale' not in vp, vp)
        check('page language declared', (await pg.get_attribute('html', 'lang')) == 'en')
        n = await pg.eval_on_selector_all('.key', 'e=>e.length'); check('19 keys present', n == 19)
        SYMBOLS = {'÷': 'divide', '×': 'times', '−': 'minus', '+': 'plus', '.': 'point', '=': 'equals'}   # symbols are exempt from 2.5.3, but names must be what people SAY
        bad = await pg.evaluate('''(S)=>[...document.querySelectorAll('.key')].filter(k=>{
            const name=(k.getAttribute('aria-label')||k.textContent).trim().toLowerCase(), vis=k.textContent.trim().toLowerCase();
            return S[vis] ? name!==S[vis] : !name.includes(vis)}).map(k=>k.textContent)''', SYMBOLS)
        check('every key: accessible name matches what a voice-control user would say', not bad, str(bad))
        check('live region present (role=status, polite)', await pg.eval_on_selector('#sr-status', 'e=>e.getAttribute("role")==="status" && e.getAttribute("aria-live")==="polite"'))
        check('no aria-label on non-interactive div', await pg.eval_on_selector('#result', 'e=>!e.hasAttribute("aria-label")'))
        # ---- keyboard: every key reachable, in order, Enter/Space activate the FOCUSED key ----
        seen = []
        for _ in range(19):
            await pg.keyboard.press('Tab'); seen.append(await pg.evaluate('document.activeElement.dataset.k'))
        check('Tab reaches all 19 keys exactly once', len(set(seen)) == 19, ' '.join(seen))
        await pg.reload(); await pg.wait_for_timeout(200)
        for _ in range(5): await pg.keyboard.press('Tab')     # focus is now on a digit key
        k = await pg.evaluate('document.activeElement.dataset.k'); await pg.keyboard.press('Enter')
        check('Enter on a focused key activates THAT key (not "=")', (await pg.inner_text('#result')) == k, f'key {k}')
        await pg.keyboard.press('Space'); check('Space activates focused key', (await pg.inner_text('#result')) == k + k)
        await pg.reload(); await pg.wait_for_timeout(200)
        await tap(pg, '9'); await pg.keyboard.press('c'); await pg.keyboard.press('x')
        check('letter shortcuts (c, x) are disabled', (await pg.inner_text('#result')) == '9')
        await pg.keyboard.press('Escape'); check('Escape clears', (await pg.inner_text('#result')) == '0')
        # ---- screen reader feedback ----
        await tap(pg, '1', '2'); check('SR announces number being typed', await status(pg) == '12', await status(pg))
        await tap(pg, '×'); check('operator exposed as pressed (aria-pressed)', await pg.get_attribute('.key[data-k="×"]', 'aria-pressed') == 'true')
        check('SR announces pending operator in words', await status(pg) == '12 times', await status(pg))
        await tap(pg, '3', '='); check('SR announces full equation + result', await status(pg) == '12 times 3 equals 36', await status(pg))
        check('aria-pressed cleared after =', await pg.get_attribute('.key[data-k="×"]', 'aria-pressed') == 'false')
        await tap(pg, 'AC', '5', '÷', '0', '='); check('SR announces the error', (await status(pg)).startswith('Error.') and "divide" in await status(pg), await status(pg))
        await tap(pg, 'AC', '5', '±'); check('SR says "negative" for negatives', await status(pg) == 'negative 5', await status(pg))
        # ---- motion ----
        tr = await pg.eval_on_selector('.key', 'e=>getComputedStyle(e).transitionDuration'); check('reduced-motion: key transitions off', tr in ('0s', '0s, 0s'), tr)
        await ctx.close()
        # ---- touch targets & layout in portrait + landscape ----
        for name, vw, vh in [('portrait 360x800', 360, 800), ('small phone 320x568', 320, 568), ('landscape 800x360', 800, 360)]:
            ctx = await b.new_context(viewport={'width': vw, 'height': vh}, has_touch=True, is_mobile=True)
            pg = await ctx.new_page(); await pg.goto(URL); await pg.wait_for_timeout(250)
            minside = await pg.evaluate('Math.min(...[...document.querySelectorAll(".key")].map(k=>{const r=k.getBoundingClientRect();return Math.min(r.width,r.height)}))')
            check(f'{name}: touch targets >= 44 CSS px (WCAG 2.5.8 needs 24)', minside >= 44, f'{minside:.0f}px')
            ov = await pg.evaluate('(()=>{const r=document.querySelector(".keypad").getBoundingClientRect();return r.bottom<=innerHeight+1 && document.documentElement.scrollWidth<=innerWidth})()')
            check(f'{name}: all keys on screen, no sideways scroll', ov)
            await tap(pg, '1','2','3','4','5','6','7','8','9','0','1','2','×','9','9','=')
            fits = await pg.evaluate('(()=>{const r=document.getElementById("result");return r.scrollWidth<=r.parentElement.clientWidth})()'); check(f'{name}: long result stays inside display', fits)
            await ctx.close()
        await b.close()
    print(f'\n{sum(results)}/{len(results)} passed'); sys.exit(0 if all(results) else 1)
asyncio.run(main())
