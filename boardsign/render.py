# Font-free board sign PDF: whole page rasterised at 300dpi, written by Pillow.
import sys
from PIL import Image, ImageChops
DPI=300
W,H=867.401,612.283                     # pt, work area 306x216mm
SX0,SX1,SY0,SY1=69.574,797.227,65.121,546.445   # safe area, top-left origin
pad=8

def write_pdf(rgb,path):
    """Minimal PDF: one page, one lossless (Flate) RGB image, no fonts or text."""
    import zlib
    h,w,_=rgb.shape
    data=zlib.compress(rgb.tobytes(),9)
    content=f"q {W} 0 0 {H} 0 0 cm /Im0 Do Q".encode()
    objs=[b"<< /Type /Catalog /Pages 2 0 R >>",
          b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
          f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {W} {H}] /Resources << /XObject << /Im0 4 0 R >> >> /Contents 5 0 R >>".encode(),
          f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length {len(data)} >>\nstream\n".encode()+data+b"\nendstream",
          f"<< /Length {len(content)} >>\nstream\n".encode()+content+b"\nendstream"]
    out=bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"); offs=[]
    for n,o in enumerate(objs,1):
        offs.append(len(out)); out+=f"{n} 0 obj\n".encode()+o+b"\nendobj\n"
    x=len(out)
    out+=f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode()+b"".join(f"{o:010d} 00000 n \n".encode() for o in offs)
    out+=f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{x}\n%%EOF\n".encode()
    open(path,"wb").write(out)
src,out=sys.argv[1],sys.argv[2]
im=Image.open(src).convert('RGBA')
im=im.crop(im.getchannel('A').getbbox())
flat=Image.alpha_composite(Image.new('RGBA',im.size,'white'),im).convert('RGB')
m=ImageChops.difference(flat,Image.new('RGB',im.size,'white')).convert('L').point(lambda v:255 if v>12 else 0)
im=im.crop(m.getbbox())
k=DPI/72
aw,ah=(SX1-SX0-2*pad)*k,(SY1-SY0-2*pad)*k
s=min(aw/im.width,ah/im.height)
w,h=round(im.width*s),round(im.height*s)
im=im.resize((w,h),Image.LANCZOS)
page=Image.new('RGBA',(round(W*k),round(H*k)),'white')
page.alpha_composite(im,(round((SX0+SX1)/2*k-w/2),round((SY0+SY1)/2*k-h/2)))
import numpy as np
a=np.array(page.convert('RGB'))
a[(a>=248).all(2)]=255          # snap near-white upscaler noise to paper white
write_pdf(a,out)
print(out,page.size)
