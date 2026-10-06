import sys
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
W,H=867.401,612.283
# safe area from guide (pdf coords, origin bottom-left)
SX0,SX1=69.574,797.227
SY0,SY1=H-546.445,H-65.121
pad=8
src,out=sys.argv[1],sys.argv[2]
im=Image.open(src).convert('RGBA')
bb=im.getchannel('A').getbbox(); im=im.crop(bb)
# trim white margins
bg=Image.new('RGBA',im.size,(255,255,255,255))
flat=Image.alpha_composite(bg,im).convert('RGB')
from PIL import ImageChops
diff=ImageChops.difference(flat,Image.new('RGB',im.size,(255,255,255))).convert('L').point(lambda v:255 if v>12 else 0)
im=im.crop(diff.getbbox())
aw,ah=SX1-SX0-2*pad,SY1-SY0-2*pad
s=min(aw/im.width,ah/im.height); w,h=im.width*s,im.height*s
# upscale to ~300dpi
px=int(w/72*300); im=im.resize((px,int(px*im.height/im.width)),Image.LANCZOS)
flat=Image.alpha_composite(Image.new('RGBA',im.size,(255,255,255,255)),im).convert('RGB')
c=canvas.Canvas(out,pagesize=(W,H)); c.setTitle(out.split('/')[-1])
c.setFillColorRGB(1,1,1); c.rect(0,0,W,H,stroke=0,fill=1)
x=(SX0+SX1)/2-w/2; y=(SY0+SY1)/2-h/2
c.drawImage(ImageReader(flat),x,y,w,h); c.showPage(); c.save()
print(out, f"{w/72*25.4:.0f}x{h/72*25.4:.0f}mm")
