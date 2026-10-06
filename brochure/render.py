"""Render BGF_FamilyDay_worksheet.html into print-ready A5 bi-fold PDFs (OhPrint.me guide).
Work area 299x212mm (1mm bleed), trim 297x210mm, safe area 10mm inside trim.
Output is image-only (text effectively outlined, effects rasterized, no fonts in PDF)."""
import sys, asyncio
from PIL import Image
from playwright.async_api import async_playwright

SRC, OUT = sys.argv[1], sys.argv[2]
SCALE = 0.955   # shrink panel content so it sits inside the 10mm safe area
INNER_SCALE = 0.93  # inside sheets have full-height cards; give them extra clearance
DSF = 4         # 96dpi * 4 = 384dpi
CSS = f"""
body{{background:#fff!important}}
.toolbar,.fold-mark,.sheet::before,.sheet::after{{display:none!important}}
.sheet{{width:299mm!important;height:212mm!important;margin:0!important;padding:1mm!important;box-shadow:none!important;
  background-position:1mm 1mm!important}}
.sheet>.panel{{flex:none;transform:scale({SCALE});transform-origin:center center}}
.sheet>.panel.inner-left,.sheet>.panel.inner-right{{transform:scale({INNER_SCALE})}}
"""
NAMES = ["parent_outside_cover", "parent_inside", "child_outside_cover", "child_inside"]

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
        pg = await b.new_page(viewport={'width': 1300, 'height': 900}, device_scale_factor=DSF)
        await pg.goto('file://' + SRC, wait_until='networkidle')
        await pg.emulate_media(media='print')
        await pg.add_style_tag(content=CSS)
        await pg.evaluate('document.fonts.ready')
        await pg.wait_for_timeout(800)
        sheets = pg.locator('section.sheet')
        for i, n in enumerate(NAMES):
            png = f'{OUT}/{n}.png'
            await sheets.nth(i).screenshot(path=png)
            im = Image.open(png).convert('RGB')
            dpi = im.width / (299 / 25.4)
            im.save(f'{OUT}/BGF_FamilyDay_{n}.pdf', resolution=dpi, quality=100)
            print(n, im.size, round(dpi))
        await b.close()
asyncio.run(main())
