import sys, numpy as np
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
S, OUT = sys.argv[1], sys.argv[2]
bg = Image.open(f'{S}/img/x-000.jpg').convert('RGB')
bear = Image.open(f'{S}/img/x-001.jpg').convert('RGB')
bear.putalpha(Image.open(f'{S}/img/x-002.png').convert('L'))
# place bear onto bg using original PDF placement (pt -> bg px)
sx, sy = 630/226.8, 629/226.68
bw, bh = round(77.28*sx), round(105.24*sy)
bg.paste(bear.resize((bw, bh), Image.LANCZOS), (round((88.44-13.68)*sx), round((237.84-134.16)*sy)), bear.resize((bw, bh), Image.LANCZOS))
a = np.array(bg).astype(int)
cx, cy, R = 314.0, 313.0, 310.5
Y, X = np.mgrid[0:a.shape[0], 0:a.shape[1]]
r = np.hypot(X-cx, Y-cy)
purple = (a[...,0]<120)&(a[...,1]<80)&(a[...,2]>110)&(r>0.8*R)
P = np.median(a[purple], axis=0).astype(int); print('purple', P)
# output canvas: 84mm work area @400dpi, scaled so scallop edge sits at 36.5mm (safe area r=37mm)
DPI = 400; ppm = DPI/25.4; N = round(84*ppm)
k = 36.5/291.17  # mm per bg px
big = Image.fromarray(a.astype('uint8')).resize((round(a.shape[1]*k*ppm), round(a.shape[0]*k*ppm)), Image.LANCZOS)
pm = Image.fromarray((purple*255).astype('uint8')).resize(big.size, Image.BILINEAR)
canvas_img = Image.new('RGB', (N, N), tuple(P))
ox, oy = round(N/2 - cx*k*ppm), round(N/2 - cy*k*ppm)
# inner disc of the artwork (inset 3px to drop the white antialias fringe), purple ring flattened to one colour
clip = Image.new('L', big.size, 0)
rr = (R-3)*k*ppm; d = ImageDraw.Draw(clip); d.ellipse((cx*k*ppm-rr, cy*k*ppm-rr, cx*k*ppm+rr, cy*k*ppm+rr), fill=255)
flat = Image.new('RGB', big.size, tuple(P))
art = Image.composite(flat, big, pm)
canvas_img.paste(art, (ox, oy), clip)
# white outside the 84mm work circle
outside = Image.new('L', (N, N), 255); ImageDraw.Draw(outside).ellipse((0, 0, N-1, N-1), fill=0)
canvas_img.paste((255,255,255), (0,0), outside)
canvas_img.save(f'{OUT}/BGF_dagwa_sticker_80x80.png', dpi=(DPI, DPI))
canvas_img.save(f'{S}/print.png')
W = 238.11
c = canvas.Canvas(f'{OUT}/BGF_dagwa_sticker_80x80.pdf', pagesize=(W, W))
c.setTitle('BGF 다과용 동글 스티커 80x80'); c.drawImage(f'{S}/print.png', 0, 0, W, W); c.showPage(); c.save()
# check preview with template guides (NOT for printing)
pv = canvas_img.copy(); d = ImageDraw.Draw(pv); h = N/2
for rad, col in ((42,(0,174,239)),(40,(120,120,120)),(37,(237,28,36))):
    q = rad*ppm; d.ellipse((h-q, h-q, h+q, h+q), outline=col, width=3)
pv.save(f'{OUT}/preview_with_guides.png')
