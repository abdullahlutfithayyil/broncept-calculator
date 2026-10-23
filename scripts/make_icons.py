"""Generates the Android launcher icons, splash screens and Play Store icon from one glyph definition."""
import os
from PIL import Image, ImageDraw
RES = 'android/app/src/main/res'
BG, BLUE, GREY, LIGHT = (29, 29, 29), (0, 106, 235), (136, 136, 136), (235, 235, 235)
S = 4  # supersampling

def glyph(size, mono=False):
    """Foreground on a transparent 108dp-style canvas (size px). Content stays inside the 66% safe zone."""
    c = size * S; im = Image.new('RGBA', (c, c), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    u = c / 432.0
    gw, gh = 200 * u, 188 * u                      # glyph box
    x0, y0 = (c - gw) / 2, (c - gh) / 2
    col = lambda rgb: (255, 255, 255, 255) if mono else rgb + (255,)
    bar_h = 48 * u
    d.rounded_rectangle([x0, y0, x0 + gw, y0 + bar_h], radius=14 * u, fill=col(LIGHT))
    r = 30 * u; gap = (gw - 6 * r) / 2; top = y0 + bar_h + 16 * u
    for row in range(2):
        for k in range(3):
            cx = x0 + r + k * (2 * r + gap); cy = top + r + row * (2 * r + 16 * u)
            rgb = BLUE if (k == 2) else GREY
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col(rgb))
    return im.resize((size, size), Image.LANCZOS)

def composite(size):                                # background + glyph, full bleed
    im = Image.new('RGBA', (size, size), BG + (255,)); im.alpha_composite(glyph(size)); return im

def legacy(px, round_):                             # pre-adaptive icons: crop to the safe zone then mask
    full = composite(432).crop((72, 72, 360, 360)).resize((px * S, px * S), Image.LANCZOS)
    m = Image.new('L', full.size, 0); dm = ImageDraw.Draw(m)
    if round_: dm.ellipse([0, 0, full.size[0] - 1, full.size[1] - 1], fill=255)
    else: dm.rounded_rectangle([0, 0, full.size[0] - 1, full.size[1] - 1], radius=int(full.size[0] * 0.22), fill=255)
    out = Image.new('RGBA', full.size, (0, 0, 0, 0)); out.paste(full, (0, 0), m)
    return out.resize((px, px), Image.LANCZOS)

dens = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
for n, f in dens.items():
    d = f'{RES}/mipmap-{n}'
    glyph(int(108 * f)).save(f'{d}/ic_launcher_foreground.png')
    glyph(int(108 * f), mono=True).save(f'{d}/ic_launcher_monochrome.png')
    legacy(int(48 * f), False).save(f'{d}/ic_launcher.png')
    legacy(int(48 * f), True).save(f'{d}/ic_launcher_round.png')

# splash: solid brand dark in every density/orientation the template ships
for root, _, files in os.walk(RES):
    for fn in files:
        if fn == 'splash.png':
            p = os.path.join(root, fn); w, h = Image.open(p).size
            Image.new('RGB', (w, h), BG).save(p)

os.makedirs('store', exist_ok=True)
composite(432).crop((72, 72, 360, 360)).resize((512, 512), Image.LANCZOS).convert('RGB').save('store/play-icon-512.png')
print('icons ok')
