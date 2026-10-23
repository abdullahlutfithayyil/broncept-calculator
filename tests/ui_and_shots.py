import asyncio, os, sys
from playwright.async_api import async_playwright
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'store', 'screenshots'); os.makedirs(OUT, exist_ok=True)
URL = 'http://localhost:8765/'
async def tap(page, *keys):
    for k in keys: await page.click(f'.key[data-k="{k}"]')
async def res(page): return await page.inner_text('#result')
async def expr(page): return (await page.inner_text('#expr')).replace('\u00a0', '').strip()
async def new(browser, scheme):
    ctx = await browser.new_context(viewport={'width': 360, 'height': 800}, device_scale_factor=3, color_scheme=scheme, is_mobile=True, has_touch=True)
    page = await ctx.new_page(); await page.goto(URL); await page.wait_for_timeout(300)
    await page.add_style_tag(content=':root{--safe-area-inset-top:44px;--safe-area-inset-bottom:20px}')  # mimic system bars for shots
    return ctx, page
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ok = []
        def check(name, cond):
            ok.append((name, bool(cond))); print(('PASS ' if cond else 'FAIL ') + name)
        ctx, pg = await new(b, 'dark')
        await tap(pg, '1', '2', '×')
        check('pending operator highlighted', await pg.eval_on_selector('.key[data-k="×"]', 'e=>e.classList.contains("active")'))
        await pg.wait_for_timeout(350); await pg.screenshot(path=f'{OUT}/02-operator-dark.png')
        await tap(pg, '3', '=')
        check('12 × 3 = 36', await res(pg) == '36' and await expr(pg) == '12 × 3 =')
        await pg.wait_for_timeout(350); await pg.screenshot(path=f'{OUT}/01-result-dark.png')
        await tap(pg, 'AC'); check('AC resets', await res(pg) == '0')
        await tap(pg, '1','2','3','4','5','6','7','8','9','0','1','2')
        check('grouping 123,456,789,012', await res(pg) == '123,456,789,012')
        fits = await pg.evaluate('(()=>{const r=document.getElementById("result");return r.scrollWidth<=r.parentElement.clientWidth})()')
        check('long number fits width (auto-shrink)', fits)
        overflow = await pg.evaluate('document.documentElement.scrollWidth<=window.innerWidth && document.body.scrollHeight<=window.innerHeight+1')
        check('no page overflow', overflow)
        await tap(pg, 'AC', '5', '÷', '0', '=')
        check('divide by zero error shown', await res(pg) == 'Error' and 'divide' in await expr(pg))
        await pg.wait_for_timeout(350); await pg.screenshot(path=f'{OUT}/04-error-dark.png')
        await tap(pg, 'AC')
        await pg.keyboard.type('7*8'); await pg.keyboard.press('Enter')
        check('keyboard 7*8=56', await res(pg) == '56')
        await ctx.close()
        ctx, pg = await new(b, 'light')
        await tap(pg, '1', '2', '8', '×', '4', '=')
        check('light: 128 × 4 = 512', await res(pg) == '512')
        bg = await pg.evaluate('getComputedStyle(document.body).backgroundColor'); check('light bg is EBEBEB', bg == 'rgb(235, 235, 235)')
        await pg.wait_for_timeout(350); await pg.screenshot(path=f'{OUT}/03-result-light.png')
        await ctx.close()
        ctx, pg = await new(b, 'dark')
        bg = await pg.evaluate('getComputedStyle(document.body).backgroundColor'); check('dark bg is 1D1D1D', bg == 'rgb(29, 29, 29)')
        opbg = await pg.evaluate('getComputedStyle(document.querySelector(".key.op")).backgroundColor'); check('operator is 006AEB', opbg == 'rgb(0, 106, 235)')
        await ctx.close(); await b.close()
        sys.exit(0 if all(c for _, c in ok) else 1)
asyncio.run(main())
