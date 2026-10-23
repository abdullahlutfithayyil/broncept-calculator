import asyncio, pathlib
from playwright.async_api import async_playwright
root = pathlib.Path(__file__).resolve().parent.parent
font = (root / 'www/fonts/inter.woff2').as_uri(); dark = (root / 'store/screenshots/01-result-dark.png').as_uri(); light = (root / 'store/screenshots/03-result-light.png').as_uri()
html = f"""<html><head><style>
@font-face {{ font-family:Inter; src:url({font}); font-weight:100 900; }}
body {{ margin:0; width:1024px; height:500px; background:#1D1D1D; overflow:hidden; font-family:Inter; position:relative; color:#EBEBEB }}
h6 {{ position:absolute; left:68px; top:128px; margin:0; font-size:20px; font-weight:600; letter-spacing:.32em; color:#888888 }}
h1 {{ position:absolute; left:64px; top:150px; margin:0; font-size:92px; font-weight:600; letter-spacing:-0.03em }}
p {{ position:absolute; left:68px; top:262px; margin:0; font-size:30px; color:#888888; font-weight:400 }}
.pill {{ position:absolute; left:68px; top:330px; background:#006AEB; color:#EBEBEB; border-radius:999px; padding:12px 26px; font-size:22px; font-weight:600 }}
.ph {{ position:absolute; width:250px; height:556px; border-radius:34px; border:6px solid #3D3D3D; background-size:cover; background-position:top; box-shadow:0 20px 50px rgba(0,0,0,.5) }}
</style></head><body>
<h6>BRONCEPT</h6><h1>Calculator</h1><p>Clean. Fast. No ads.</p><div class="pill">Light &amp; dark themes</div>
<div class="ph" style="left:560px; top:70px; background-image:url({light})"></div>
<div class="ph" style="left:760px; top:40px; background-image:url({dark})"></div>
</body></html>"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width':1024,'height':500})
        tmp = root/'store/_fg.html'; tmp.write_text(html); await pg.goto(tmp.as_uri()); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(500)
        await pg.screenshot(path=str(root/'store/play-feature-graphic-1024x500.png')); await b.close(); (root/'store/_fg.html').unlink()
asyncio.run(main())
